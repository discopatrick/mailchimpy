import os
import requests
import hashlib

class MailChimpClient(object):

	def __init__(self, api_key):

		self.api_key = api_key

		# the subdomain to use in the api url
		# is always the last 3 characters of the api key
		self.subdomain = self.api_key[-3:]

	def get_md5(self, string):

		hashobject = hashlib.md5(string.encode())
		md5 = hashobject.hexdigest()
		return md5

	def get_api_root(self):

		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/'.format(self.subdomain),
			auth=('apikey', self.api_key)
		)

		return response

	def check_subscription_status(self, email, list_id):

		email_md5 = self.get_md5(email)

		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(self.subdomain, list_id, email_md5),
			auth=('apikey', self.api_key)
		)

		if response.status_code == 404:
			subscribed = False
		elif response.status_code == 200:
			subscribed = True
		else:
			subscribed = None

		return subscribed, response