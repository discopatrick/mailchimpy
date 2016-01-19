import os
import warnings
import hashlib
from unittest import TestCase
from uuid import uuid4
import requests
from betamax import Betamax
from betamax_serializers import pretty_json
import base64

from mailchimpy.mailchimpy import MailChimpClient
from . import config


class BaseMailChimpTest(TestCase):

    cassette_dir = 'cassettes'

    @classmethod
    def setUpClass(self):

        self.session = requests.Session()
        self.recorder = Betamax(self.session)

        self.api_key = config.MAILCHIMP_API_KEY

        # the subdomain to use in the api url
        # is always the last 3 characters of the api key
        self.subdomain = self.api_key[-3:]

        # define the string that will be passed in the MailChimp request
        # 'Authorization' header
        MAILCHIMP_REQUEST_AUTH_HEADER_NAME = 'apikey'
        MAILCHIMP_REQUEST_AUTH_HEADER = '{}:{}'.format(
            MAILCHIMP_REQUEST_AUTH_HEADER_NAME, self.api_key)

        # create the directory to store betamax cassettes
        abs_cassette_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), self.cassette_dir)
        os.makedirs(abs_cassette_dir, exist_ok=True)

        Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
        with Betamax.configure() as betamaxconfig:
            betamaxconfig.cassette_library_dir = abs_cassette_dir
            betamaxconfig.default_cassette_options['record_mode'] = 'once'
            betamaxconfig.default_cassette_options[
                'serialize_with'] = 'prettyjson'
            betamaxconfig.default_cassette_options['match_requests_on'] = [
                'method'
            ]
            betamaxconfig.define_cassette_placeholder(
                '<MAILCHIMP_AUTH_B64>',
                base64.b64encode(
                    MAILCHIMP_REQUEST_AUTH_HEADER.encode()
                ).decode()
            )
            betamaxconfig.define_cassette_placeholder(
                '<MAILCHIMP_SUBDOMAIN>',
                self.subdomain
            )

        # suppress these warnings (due to requests module): 
        # ResourceWarning: unclosed <ssl.SSLSocket
        warnings.simplefilter("ignore", ResourceWarning)

    def _get_guid(self):
        return str(uuid4())

    def _get_md5(self, string):

        hashobject = hashlib.md5(string.encode())
        md5 = hashobject.hexdigest()
        return md5

    def _get_fresh_email(self):

        # generate a random email address, which we can be almost
        # certain is not already subscribed to our list(s)
        return '{}@{}.com'.format(uuid4(), uuid4())

    def _api_subscribe_email_to_list(self, list_id, email=None):

        if email is None:
            email = self._get_fresh_email()

        # subscribe an email address to the list (via direct API call)
        response = self.session.post(
            'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(
                self.subdomain, list_id),
            auth=('apikey', self.api_key),
            json={'email_address': email, 'status': 'subscribed'}
        )

        return {
            'status': response.json().get('status'),
            'title': response.json().get('title'),
            'status_code': response.status_code,
            'response': response
        }

    def _api_unsubscribe_email_from_list(self, list_id, email):

        email_md5 = self._get_md5(email)

        response = self.session.patch(
            'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                self.subdomain, list_id, email_md5),
            auth=('apikey', self.api_key),
            json={'status': 'unsubscribed'}
        )

        return {
            'status': response.json().get('status'),
            'title': response.json().get('title'),
            'status_code': response.status_code,
            'response': response
        }

    def _api_get_member(self, list_id, email=None):

        if email is None:
            email = self._get_fresh_email()

        email_md5 = self._get_md5(email)

        response = self.session.get(
            'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                self.subdomain, list_id, email_md5),
            auth=('apikey', self.api_key)
        )

        return {
            'status': response.json().get('status'),
            'status_code': response.status_code,
            'response': response
        }

    def _api_create_new_list(self, list_name=None):

        if not list_name:
            list_name = self._get_guid()

        # subscribe an email address to the list (via direct API call)
        response = self.session.post(
            'https://{}.api.mailchimp.com/3.0/lists'.format(self.subdomain),
            auth=('apikey', self.api_key),
            json={
                'name': list_name,
                'contact': {
                    'company': 'company',
                    'address1': 'address1',
                    'city': 'city',
                    'state': 'state',
                    'zip': 'zip',
                    'country': 'country'
                },
                'permission_reminder': 'permission reminder',
                'campaign_defaults': {
                    'from_name': 'from name',
                    'from_email': self._get_fresh_email(),
                    'subject': 'subject',
                    'language': 'language'
                },
                'email_type_option': False
            }
        )

        return {
            'id': response.json().get('id'),
            'name': response.json().get('name'),
            'status_code': response.status_code,
            'response': response
        }

    def _api_delete_list(self, list_id):

        response = self.session.delete(
            'https://{}.api.mailchimp.com/3.0/lists/{}'.format(
                self.subdomain, list_id),
            auth=('apikey', self.api_key)
        )

        return {
            'status_code': response.status_code,
            'response': response
        }

    def _api_create_interest_category(self, list_id, category_type='checkboxes'):

        response = self.session.post(
            'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(
                self.subdomain, list_id),
            auth=('apikey', self.api_key),
            json={
                'title': self._get_guid(),
                'type': category_type
            }
        )

        return {
            'id': response.json().get('id'),
            'name': response.json().get('name'),
            'type': response.json().get('type'),
            'status_code': response.status_code,
            'response': response
        }

    def _api_get_interests(self, list_id, category_id):
        
        response = self.session.get(
            'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests'.format(
                self.subdomain, list_id, category_id),
            auth=('apikey', self.api_key)
        )

        return {
            'total_items': response.json().get('total_items'),
            'interests': response.json().get('interests'),
            'status_code': response.status_code,
            'response': response
        }

    def _api_create_interest(self, list_id, category_id, interest_name=None):

        if interest_name is None:
            interest_name = self._get_guid()

        response = self.session.post(
            'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests'.format(
                self.subdomain, list_id, category_id),
            auth=('apikey', self.api_key),
            json={
                'name': interest_name,
                'display_order': 1,
            }
        )

        return {
            'id': response.json().get('id'),
            'name': response.json().get('name'),
            'status_code': response.status_code,
            'response': response
        }



