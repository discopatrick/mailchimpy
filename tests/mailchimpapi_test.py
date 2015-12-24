import unittest
from unittest import TestCase
import hashlib
import requests
from uuid import uuid4
from pprint import pformat

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

	def test_can_subscribe_a_new_email_to_list(self):

		list_id = config.MAILCHIMP_LIST_ID

		# can't use 'example.com' here, MailChimp will refuse an
		# address with that domain.
		email = '{}@{}.com'.format(uuid4(), uuid4())

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(self.subdomain, list_id),
			auth=('apikey', self.api_key),
			json={'email_address': email, 'status': 'subscribed'}
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json().get('status'), 'subscribed')

	def test_subscribing_an_email_that_is_already_subscribed(self):

		list_id = config.MAILCHIMP_LIST_ID

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(self.subdomain, list_id),
			auth=('apikey', self.api_key),
			json={'email_address': config.EMAIL_ALREADY_SUBSCRIBED_TO_LIST, 'status': 'subscribed'}
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.json().get('title'), 'Member Exists')

	def test_subscribing_a_known_disallowed_email(self):

		list_id = config.MAILCHIMP_LIST_ID
		known_disallowed_email = 'anything@example.com'

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(self.subdomain, list_id),
			auth=('apikey', self.api_key),
			json={'email_address': known_disallowed_email, 'status': 'subscribed'}
		)

		# print(pformat(response.json()))

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.json().get('title'), 'Invalid Resource')

if __name__ == '__main__':
	unittest.main()