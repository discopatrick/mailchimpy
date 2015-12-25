from unittest import TestCase
from uuid import uuid4
import requests

from . import config

class BaseMailChimpTest(TestCase):

	def setUp(self):
		self.api_key = config.MAILCHIMP_API_KEY
		self.list_id = config.MAILCHIMP_LIST_ID
		
		# the subdomain to use in the api url
		# is always the last 3 characters of the api key
		self.subdomain = self.api_key[-3:]

	def _get_fresh_email(self):

		# generate a random email address, which we can be almost
		# certain is not already subscribed to our list(s)
		return '{}@{}.com'.format(uuid4(), uuid4())

	def _api_subscribe_email_to_list(self, email, list_id):

		# subscribe an email address to the list (via direct API call)
		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(self.subdomain, list_id),
			auth=('apikey', self.api_key),
			json={'email_address': email, 'status': 'subscribed'}
		)