import unittest
from unittest import TestCase
import hashlib
import requests
from uuid import uuid4

from . import config

class MailChimpAPITest(TestCase):
	
	def setUp(self):

		self.api_key = config.MAILCHIMP_API_KEY

		# the subdomain to use in the api url
		# is always the last 3 characters of the api key
		self.subdomain = self.api_key[-3:]

	def get_md5(self, string):

		hashobject = hashlib.md5(string.encode())
		md5 = hashobject.hexdigest()
		return md5

	def test_api_returns_a_response(self):

		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/'.format(self.subdomain),
			auth=('apikey', self.api_key)
		)

		self.assertEqual(response.status_code, 200)

	def test_can_check_if_email_address_is_subscribed_to_list(self):

		list_id = config.MAILCHIMP_LIST_ID

		email = '{}@example.com'.format(uuid4())
		email_md5 = self.get_md5(email)

		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(self.subdomain, list_id, email_md5),
			auth=('apikey', self.api_key)
		)

		self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
	unittest.main()