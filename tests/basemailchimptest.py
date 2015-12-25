from unittest import TestCase

from . import config

class BaseMailChimpTest(TestCase):

	def setUp(self):
		self.api_key = config.MAILCHIMP_API_KEY
		self.list_id = config.MAILCHIMP_LIST_ID
		
		# the subdomain to use in the api url
		# is always the last 3 characters of the api key
		self.subdomain = self.api_key[-3:]