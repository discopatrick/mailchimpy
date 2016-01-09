import os
import requests
import hashlib
from pprint import pformat


class MailChimpClient(object):

    def __init__(self, api_key):

        self.api_key = api_key

        # the subdomain to use in the api url
        # is always the last 3 characters of the api key
        self.subdomain = self.api_key[-3:]

        # set up a session for requests to be made in
        self.session = requests.Session()

    def _get_md5(self, string):

        hashobject = hashlib.md5(string.encode())
        md5 = hashobject.hexdigest()
        return md5

    def get_api_root(self):

        response = self.session.get(
            'https://{}.api.mailchimp.com/3.0/'.format(self.subdomain),
            auth=('apikey', self.api_key)
        )

        return response

    def check_subscription_status(self, email, list_id):

        email_md5 = self._get_md5(email)

        response = self.session.get(
            'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                self.subdomain, list_id, email_md5),
            auth=('apikey', self.api_key)
        )

        if response.status_code == 404:
            subscribed = False
        elif response.status_code == 200:
            subscribed = True
        else:
            subscribed = None

        return subscribed

    def subscribe_email_to_list(self, email, list_id):

        response = self.session.post(
            'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(
                self.subdomain, list_id),
            auth=('apikey', self.api_key),
            json={'email_address': email, 'status': 'subscribed'}
        )

        if response.status_code == 200:
            success = True
        elif response.status_code == 400:
            success = False
        else:
            success = None

        return success

    def unsubscribe_email_from_list(self, email, list_id):

        email_md5 = self._get_md5(email)
        response = self.session.patch(
            'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                self.subdomain, list_id, email_md5),
            auth=('apikey', self.api_key),
            json={'status': 'unsubscribed'}
        )

        if response.status_code == 200:
            success = True
        elif response.status_code == 404:
            success = None
        else:
            success = False

        return success

    def create_interest_category(self, category_name, list_id):

        response = self.session.post(
            'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(
                self.subdomain, list_id),
            auth=('apikey', self.api_key),
            json={'title': category_name, 'type': 'checkboxes'}
        )

        if response.status_code == 200:
            success = True

        return success

    def get_interest_category(self, category_id, list_id):

        response = self.session.get(
            'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}'.format(
                self.subdomain, list_id, category_id),
            auth=('apikey', self.api_key)
        )

        if response.status_code == 200:
            success = True

        return success
