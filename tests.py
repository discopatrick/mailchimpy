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

if __name__ == '__main__':
	unittest.main()