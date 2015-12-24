import unittest
from unittest import TestCase
from mailchimpy import MailChimpClient

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

		email = 'an-email-we-know-is-not-subscribed-to-the-list@example.com'

		response = self.mc.check_subscription_status(email, list_id)

		self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
	unittest.main()