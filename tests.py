import unittest
from uuid import uuid4
from unittest import TestCase
from mailchimpy import MailChimpClient

import config

class MailChimpClientTest(TestCase):

	def setUp(self):

		with open('./api_key.txt') as f:
			self.api_key = f.read().strip()

		self.mc = MailChimpClient(self.api_key)

	def test_api_returns_a_response(self):

		response = self.mc.get_api_root()

		self.assertEqual(response.status_code, 200)

	def test_can_check_if_email_address_is_subscribed_to_list(self):

		with open('./list_id.txt') as f:
			list_id = f.read().strip()

		email = '{}@example.com'.format(uuid4())

		subscribed, response = self.mc.check_subscription_status(email, list_id)

		self.assertEqual(response.status_code, 404)

	def test_check_subscription_status_returns_false_for_email_address_not_subscribed_to_list(self):

		with open('./list_id.txt') as f:
			list_id = f.read().strip()

		email = '{}@example.com'.format(uuid4())

		subscribed, response = self.mc.check_subscription_status(email, list_id)

		self.assertIsNotNone(subscribed)
		self.assertFalse(subscribed)

	def test_check_subscription_status_returns_true_for_email_address_already_subscribed_to_list(self):

		with open('./list_id.txt') as f:
			list_id = f.read().strip()

		subscribed, response = self.mc.check_subscription_status(config.EMAIL_ALREADY_SUBSCRIBED_TO_LIST, list_id)

		self.assertIsNotNone(subscribed)
		self.assertTrue(subscribed)

if __name__ == '__main__':
	unittest.main()