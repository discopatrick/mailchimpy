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

    def test_check_subscription_status_for_email_address_that_never_existed_on_list(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette(self.id()):
            (exists, subscribed) = self.mc.check_subscription_status(email, self.temp_list['id'])

        self.assertFalse(exists)
        self.assertIsNone(subscribed)

    def test_check_subscription_status_for_email_address_already_subscribed_to_list(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list (via API directly)
            self._api_subscribe_email_to_list(self.temp_list['id'], email)

        with self.recorder.use_cassette(self.id()):
            # check that email's subscription status (via the client)
            (exists, subscribed) = self.mc.check_subscription_status(email, self.temp_list['id'])

        self.assertTrue(exists)
        self.assertTrue(subscribed)

    def test_check_subscription_status_for_email_that_exists_in_list_but_unsubscribed(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange_subscription'.format(self.id())):
            # subscribe an email address to the list (via API directly)
            self._api_subscribe_email_to_list(self.temp_list['id'], email)

        with self.recorder.use_cassette('{}_arrange_unsubscription'.format(self.id())):
            # unsubscribe same email address from the list (via API directly)
            self._api_unsubscribe_email_from_list(email, self.temp_list['id'])

        with self.recorder.use_cassette(self.id()):
            # check that email's subscription status (via the client)
            (exists, subscribed) = self.mc.check_subscription_status(email, self.temp_list['id'])

        self.assertTrue(exists)
        self.assertIsNotNone(subscribed)
        self.assertFalse(subscribed)

    def test_subscribe_email_to_list_returns_true_on_success(self):

        with self.recorder.use_cassette(self.id()):
            success = self.mc.subscribe_email_to_list(
                self._get_fresh_email(), self.temp_list['id'])

        self.assertTrue(success)

    def test_subscribe_email_to_list_returns_false_for_email_already_subscribed(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list (via API directly)
            self._api_subscribe_email_to_list(self.temp_list['id'], email)

        with self.recorder.use_cassette(self.id()):
            # attempt to subscribe that same email a second time (via the
            # client)
            success = self.mc.subscribe_email_to_list(email, self.temp_list['id'])

        self.assertIsNotNone(success)
        self.assertFalse(success)

    def test_unsubscribe_email_from_list_returns_true_on_success(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list (via API directly)
            self._api_subscribe_email_to_list(self.temp_list['id'], email)

        # unsubscribe that email address (via the client)
        with self.recorder.use_cassette(self.id()):
            success = self.mc.unsubscribe_email_from_list(email, self.temp_list['id'])

        self.assertTrue(success)

    def test_unsubscribe_email_from_list_returns_true_even_when_it_was_already_unsubscribed(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list (via API directly)
            self._api_subscribe_email_to_list(self.temp_list['id'], email)

            # unsubscribe that email address (also via API directly)
            email_md5 = self._get_md5(email)
            response = self.mc.session.patch(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                    self.subdomain, self.temp_list['id'], email_md5),
                auth=('apikey', self.api_key),
                json={'status': 'unsubscribed'}
            )

        # attempt to unsubscribe a second time (via the client)
        with self.recorder.use_cassette(self.id()):
            success = self.mc.unsubscribe_email_from_list(email, self.temp_list['id'])

        self.assertTrue(success)

    def test_unsubscribe_email_from_list_returns_none_when_email_did_not_exist_on_list(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette(self.id()):
            success = self.mc.unsubscribe_email_from_list(email, self.temp_list['id'])

        self.assertIsNone(success)

    def test_create_new_interest_category(self):

        category_name = self._get_guid()

        with self.recorder.use_cassette(self.id()):
            success = self.mc.create_interest_category(
                category_name, self.temp_list['id'])

        self.assertTrue(success)

    def test_get_existing_interest_category(self):

        category_name = self._get_guid()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            response = self.session.post(
                'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(
                    self.subdomain, self.temp_list['id']),
                auth=('apikey', self.api_key),
                json={'title': category_name, 'type': 'checkboxes'}
            )

        category_id = response.json().get('id')

        with self.recorder.use_cassette(self.id()):
            success = self.mc.get_interest_category(category_id, self.temp_list['id'])

        self.assertTrue(success)
