import unittest
from unittest import TestCase
from uuid import uuid4

from mailchimpy.mailchimpy import MailChimpClient
from . import config

class MailChimpClientTest(TestCase):

	def setUp(self):

		self.api_key = config.MAILCHIMP_API_KEY
		self.list_id = config.MAILCHIMP_LIST_ID

		self.mc = MailChimpClient(self.api_key)

	def get_fresh_email(self):

		# generate a random email address, which we can be almost
		# certain is not already subscribed to our list(s)
		return '{}@{}.com'.format(uuid4(), uuid4())

	def test_check_subscription_status_returns_false_for_email_address_not_subscribed_to_list(self):

		subscribed, response = self.mc.check_subscription_status(self.get_fresh_email(), self.list_id)

		self.assertIsNotNone(subscribed)
		self.assertFalse(subscribed)

	def test_check_subscription_status_returns_true_for_email_address_already_subscribed_to_list(self):

		subscribed, response = self.mc.check_subscription_status(config.EMAIL_ALREADY_SUBSCRIBED_TO_LIST, self.list_id)

		self.assertIsNotNone(subscribed)
		self.assertTrue(subscribed)

	def test_subscribe_email_to_list_returns_true_on_success(self):

		success = self.mc.subscribe_email_to_list(self.get_fresh_email(), self.list_id)

		self.assertTrue(success)

	def test_subscribe_email_to_list_returns_false_for_email_already_subscribed(self):

		success = self.mc.subscribe_email_to_list(config.EMAIL_ALREADY_SUBSCRIBED_TO_LIST, self.list_id)

		self.assertIsNotNone(success)
		self.assertFalse(success)

if __name__ == '__main__':
	unittest.main()