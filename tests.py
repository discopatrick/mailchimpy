import unittest
from unittest import TestCase
from mailchimpy import MailChimpClient

class MailChimpClientTest(TestCase):

	def setUp(self):

		self.mc = MailChimpClient()

	def test_api_returns_a_response(self):

		response = self.mc.get_api_root()

		self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
	unittest.main()