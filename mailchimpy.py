import os
import requests

class MailChimpClient(object):

	def __init__(self):

		with open('./api_key.txt') as f:
			self.api_key = f.read().strip()

		# the subdomain to use in the api url
		# is always the last 3 characters of the api key
		self.subdomain = self.api_key[-3:]

	def get_api_root(self):

		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/'.format(self.subdomain),
			auth=('apikey', self.api_key)
		)

		return response