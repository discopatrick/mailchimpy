import os
import warnings
from unittest import TestCase
from uuid import uuid4
import requests
from betamax import Betamax
from betamax_serializers import pretty_json
import base64

from . import config

class BaseMailChimpTest(TestCase):

	def setUp(self):

		self.api_key = config.MAILCHIMP_API_KEY
		self.list_id = config.MAILCHIMP_LIST_ID
		
		# the subdomain to use in the api url
		# is always the last 3 characters of the api key
		self.subdomain = self.api_key[-3:]

		# define the string that will be passed in the MailChimp request 'Authorization' header
		MAILCHIMP_REQUEST_AUTH_HEADER_NAME = 'apikey'
		MAILCHIMP_REQUEST_AUTH_HEADER = '{}:{}'.format(MAILCHIMP_REQUEST_AUTH_HEADER_NAME, self.api_key)

		with Betamax.configure() as betamaxconfig:
			betamaxconfig.cassette_library_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cassettes')
			betamaxconfig.default_cassette_options['record_mode'] = 'new_episodes'
			betamaxconfig.define_cassette_placeholder(
				'<MAILCHIMP_AUTH_B64>',
				base64.b64encode(
					MAILCHIMP_REQUEST_AUTH_HEADER.encode()
				).decode()
			)
			betamaxconfig.define_cassette_placeholder(
				'<MAILCHIMP_LIST_ID>',
				self.list_id
			)

		Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

		# suppress these warnings (due to requests module): ResourceWarning: unclosed <ssl.SSLSocket
		warnings.simplefilter("ignore", ResourceWarning)


	def _get_guid(self):
		return str(uuid4())

	def _get_fresh_email(self):

		# generate a random email address, which we can be almost
		# certain is not already subscribed to our list(s)
		return '{}@{}.com'.format(uuid4(), uuid4())

	def _api_subscribe_email_to_list(self, email, list_id, requests_session=None):

		if not requests_session:
			requests_session = requests.Session()

		# subscribe an email address to the list (via direct API call)
		response = requests_session.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(self.subdomain, list_id),
			auth=('apikey', self.api_key),
			json={'email_address': email, 'status': 'subscribed'}
		)