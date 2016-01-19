import unittest
from unittest import TestCase
from uuid import uuid4
import requests
from betamax import Betamax

from .basemailchimptest import BaseMailChimpTest
from mailchimpy.mailchimpy import MailChimpClient
from . import config


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


class MailChimpClientTest(BaseMailChimpClientTest):

    def test_check_subscription_status_returns_false_for_email_address_not_subscribed_to_list(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        email = self._get_fresh_email()

        with self.recorder.use_cassette(self.id()):
            subscribed = self.mc.check_subscription_status(email, new_list['id'])

        self.assertIsNotNone(subscribed)
        self.assertFalse(subscribed)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_check_subscription_status_returns_true_for_email_address_already_subscribed_to_list(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list (via API directly)
            self._api_subscribe_email_to_list(new_list['id'], email)

        with self.recorder.use_cassette(self.id()):
            # check that email's subscription status (via the client)
            subscribed = self.mc.check_subscription_status(email, new_list['id'])

        self.assertIsNotNone(subscribed)
        self.assertTrue(subscribed)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_subscribe_email_to_list_returns_true_on_success(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        with self.recorder.use_cassette(self.id()):
            success = self.mc.subscribe_email_to_list(
                self._get_fresh_email(), new_list['id'])

        self.assertTrue(success)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_subscribe_email_to_list_returns_false_for_email_already_subscribed(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list (via API directly)
            self._api_subscribe_email_to_list(new_list['id'], email)

        with self.recorder.use_cassette(self.id()):
            # attempt to subscribe that same email a second time (via the
            # client)
            success = self.mc.subscribe_email_to_list(email, new_list['id'])

        self.assertIsNotNone(success)
        self.assertFalse(success)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_unsubscribe_email_from_list_returns_true_on_success(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list (via API directly)
            self._api_subscribe_email_to_list(new_list['id'], email)

        # unsubscribe that email address (via the client)
        with self.recorder.use_cassette(self.id()):
            success = self.mc.unsubscribe_email_from_list(email, new_list['id'])

        self.assertTrue(success)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_unsubscribe_email_from_list_returns_true_even_when_it_was_already_unsubscribed(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list (via API directly)
            self._api_subscribe_email_to_list(new_list['id'], email)

            # unsubscribe that email address (also via API directly)
            email_md5 = self._get_md5(email)
            response = self.mc.session.patch(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                    self.subdomain, new_list['id'], email_md5),
                auth=('apikey', self.api_key),
                json={'status': 'unsubscribed'}
            )

        # attempt to unsubscribe a second time (via the client)
        with self.recorder.use_cassette(self.id()):
            success = self.mc.unsubscribe_email_from_list(email, new_list['id'])

        self.assertTrue(success)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_unsubscribe_email_from_list_returns_none_when_email_did_not_exist_on_list(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        email = self._get_fresh_email()

        with self.recorder.use_cassette(self.id()):
            success = self.mc.unsubscribe_email_from_list(email, new_list['id'])

        self.assertIsNone(success)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_create_new_interest_category(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        category_name = self._get_guid()

        with self.recorder.use_cassette(self.id()):
            success = self.mc.create_interest_category(
                category_name, new_list['id'])

        self.assertTrue(success)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_get_existing_interest_category(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        category_name = self._get_guid()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            response = self.session.post(
                'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(
                    self.subdomain, new_list['id']),
                auth=('apikey', self.api_key),
                json={'title': category_name, 'type': 'checkboxes'}
            )

        category_id = response.json().get('id')

        with self.recorder.use_cassette(self.id()):
            success = self.mc.get_interest_category(category_id, new_list['id'])

        self.assertTrue(success)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])
            