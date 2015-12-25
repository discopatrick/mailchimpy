import unittest
from unittest import TestCase
from uuid import uuid4
import requests
import hashlib

from .basemailchimptest import BaseMailChimpTest
from mailchimpy.mailchimpy import MailChimpClient
from . import config

class MailChimpClientTest(BaseMailChimpTest):

	def setUp(self):

		super().setUp()

		self.mc = MailChimpClient(self.api_key)

	def get_md5(self, string):

		hashobject = hashlib.md5(string.encode())
		md5 = hashobject.hexdigest()
		return md5

	def test_check_subscription_status_returns_false_for_email_address_not_subscribed_to_list(self):

		subscribed, response = self.mc.check_subscription_status(self._get_fresh_email(), self.list_id)

		self.assertIsNotNone(subscribed)
		self.assertFalse(subscribed)

	def test_check_subscription_status_returns_true_for_email_address_already_subscribed_to_list(self):

		subscribed, response = self.mc.check_subscription_status(config.EMAIL_ALREADY_SUBSCRIBED_TO_LIST, self.list_id)

		self.assertIsNotNone(subscribed)
		self.assertTrue(subscribed)

	def test_subscribe_email_to_list_returns_true_on_success(self):

		success = self.mc.subscribe_email_to_list(self._get_fresh_email(), self.list_id)

		self.assertTrue(success)

	def test_subscribe_email_to_list_returns_false_for_email_already_subscribed(self):

		success = self.mc.subscribe_email_to_list(config.EMAIL_ALREADY_SUBSCRIBED_TO_LIST, self.list_id)

		self.assertIsNotNone(success)
		self.assertFalse(success)

	def test_unsubscribe_email_from_list_returns_true_on_success(self):

		# subscribe an email address to the list (via API directly)
		email = self._get_fresh_email()
		self._api_subscribe_email_to_list(email, self.list_id)

		# unsubscribe that email address (via the client)
		success = self.mc.unsubscribe_email_from_list(email, self.list_id)

		self.assertTrue(success)

	def test_unsubscribe_email_from_list_returns_true_even_when_it_was_already_unsubscribed(self):

		# subscribe an email address to the list (via API directly)
		email = self._get_fresh_email()
		self._api_subscribe_email_to_list(email, self.list_id)

		# unsubscribe that email address (also via HTTP)
		email_md5 = self.get_md5(email)
		response = requests.patch(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(self.subdomain, self.list_id, email_md5),
			auth=('apikey', self.api_key),
			json={'status': 'unsubscribed'}
		)

		# attempt to unsubscribe again (via the client)
		success = self.mc.unsubscribe_email_from_list(email, self.list_id)

		self.assertTrue(success)		

	def test_unsubscribe_email_from_list_returns_none_when_email_did_not_exist_on_list(self):

		email = self._get_fresh_email()

		success = self.mc.unsubscribe_email_from_list(email, self.list_id)

		self.assertIsNone(success)

if __name__ == '__main__':
	unittest.main()