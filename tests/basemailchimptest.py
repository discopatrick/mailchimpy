import os
import warnings
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
        self.list_id = config.MAILCHIMP_LIST_ID

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
                '<MAILCHIMP_LIST_ID>',
                self.list_id
            )
            betamaxconfig.define_cassette_placeholder(
                '<MAILCHIMP_SUBDOMAIN>',
                self.subdomain
            )

        # suppress these warnings (due to requests module): ResourceWarning:
        # unclosed <ssl.SSLSocket
        warnings.simplefilter("ignore", ResourceWarning)

    def _get_guid(self):
        return str(uuid4())

    def _get_fresh_email(self):

        # generate a random email address, which we can be almost
        # certain is not already subscribed to our list(s)
        return '{}@{}.com'.format(uuid4(), uuid4())

    def _api_subscribe_email_to_list(self, email, list_id):

        # subscribe an email address to the list (via direct API call)
        response = self.session.post(
            'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(
                self.subdomain, list_id),
            auth=('apikey', self.api_key),
            json={'email_address': email, 'status': 'subscribed'}
        )

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
            'response': response
        }


class BaseMailChimpAPITest(BaseMailChimpTest):

    cassette_dir = 'cassettes/api'


class BaseMailChimpClientTest(BaseMailChimpTest):

    cassette_dir = 'cassettes/client'

    @classmethod
    def setUpClass(cls):

        super(BaseMailChimpClientTest, cls).setUpClass()

        cls.mc = MailChimpClient(cls.api_key)

        # override the default requests session, using instead the
        # MailChimpClient's session
        cls.session = cls.mc.session

        # not sure if this is necessary, may be taken care of by
        # passed-by-ref variables
        cls.recorder = Betamax(cls.session)
