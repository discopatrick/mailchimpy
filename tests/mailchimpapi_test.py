import unittest
from unittest import TestCase
import hashlib
import requests
from uuid import uuid4
from pprint import pformat

from .basemailchimptest import BaseMailChimpTest
from . import config

class MailChimpAPITest(BaseMailChimpTest):
	
	# def setUp(self):

	# 	super().setUp()

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

		email = self._get_fresh_email()
		email_md5 = self.get_md5(email)

		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(self.subdomain, self.list_id, email_md5),
			auth=('apikey', self.api_key)
		)

		self.assertEqual(response.status_code, 404)

	def test_can_subscribe_a_new_email_to_list(self):

		email = self._get_fresh_email()

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
			json={'email_address': email, 'status': 'subscribed'}
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json().get('status'), 'subscribed')

	def test_subscribing_an_email_that_is_already_subscribed(self):

		# subscribe an email address to the list

		email = self._get_fresh_email()
		self._api_subscribe_email_to_list(email, self.list_id)

		# attempt to subscribe that same email address again

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
			json={'email_address': email, 'status': 'subscribed'}
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.json().get('title'), 'Member Exists')

	def test_subscribing_a_known_disallowed_email(self):

		known_disallowed_email = 'anything@example.com'

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
			json={'email_address': known_disallowed_email, 'status': 'subscribed'}
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.json().get('title'), 'Invalid Resource')

	def test_unsubscribing_an_email(self):

		# subscribe an email address to the list

		email = self._get_fresh_email()
		self._api_subscribe_email_to_list(email, self.list_id)

		# unsubscribe that same email address from the list
		
		email_md5 = self.get_md5(email)
		response = requests.patch(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(self.subdomain, self.list_id, email_md5),
			auth=('apikey', self.api_key),
			json={'status': 'unsubscribed'}
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json().get('status'), 'unsubscribed')

	def test_unsubscribing_an_email_that_is_already_unsubscribed(self):

		# subscribe an email address to the list

		email = self._get_fresh_email()
		self._api_subscribe_email_to_list(email, self.list_id)

		# unsubscribe that same email address from the list
		
		email_md5 = self.get_md5(email)
		response = requests.patch(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(self.subdomain, self.list_id, email_md5),
			auth=('apikey', self.api_key),
			json={'status': 'unsubscribed'}
		)

		# attempt to unsubscrbe again
		
		response = requests.patch(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(self.subdomain, self.list_id, email_md5),
			auth=('apikey', self.api_key),
			json={'status': 'unsubscribed'}
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json().get('status'), 'unsubscribed')

	def test_unsubscribing_an_email_that_has_never_existed_in_the_list(self):

		email = self._get_fresh_email()
		email_md5 = self.get_md5(email)
		response = requests.patch(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(self.subdomain, self.list_id, email_md5),
			auth=('apikey', self.api_key),
			json={'status': 'unsubscribed'}
		)

		self.assertEqual(response.status_code, 404)
		self.assertEqual(response.json().get('title'), 'Resource Not Found')

class InterestCategoriesTest(BaseMailChimpTest):

	def test_get_all_interest_categories_of_list(self):

		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
		)

		self.assertEqual(response.status_code, 200)
		self.assertIsNotNone(response.json().get('categories'))

	def test_create_interest_category_in_list(self):
		
		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
			json={
				'title': self._get_guid(),
				'type': 'checkboxes'
			}
		)

		self.assertEqual(response.status_code, 200)
		self.assertIsNotNone(response.json().get('id'))

	def test_create_interest_category_of_each_type_in_list(self):

		for interest_type in ('checkboxes', 'dropdown', 'radio', 'hidden'):
			response = requests.post(
				'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(self.subdomain, self.list_id),
				auth=('apikey', self.api_key),
				json={
					'title': self._get_guid(),
					'type': interest_type
				}
			)

			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.json().get('type'), interest_type)

	def test_get_specific_interest_category(self):

		# create the category
		category_name = self._get_guid()
		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
			json={
				'title': category_name,
				'type': 'checkboxes'
			}
		)

		category_id = response.json().get('id')

		# retrieve that category
		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}'.format(self.subdomain, self.list_id, category_id),
			auth=('apikey', self.api_key)
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json().get('title'), category_name)


class InterestsTest(BaseMailChimpTest):

	def test_get_all_interests_of_empty_category(self):

		# create the category
		category_name = self._get_guid()
		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
			json={
				'title': category_name,
				'type': 'checkboxes'
			}
		)

		category_id = response.json().get('id')

		# get all the interests of that category (should be none)
		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests'.format(self.subdomain, self.list_id, category_id),
			auth=('apikey', self.api_key)
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json().get('interests'), [])
		self.assertEqual(response.json().get('total_items'), 0)

	def test_can_create_an_interest_in_a_category(self):

		# create the category
		category_name = self._get_guid()
		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
			json={
				'title': category_name,
				'type': 'checkboxes'
			}
		)

		category_id = response.json().get('id')

		# create an interest in that category
		interest_name = self._get_guid()

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests'.format(self.subdomain, self.list_id, category_id),
			auth=('apikey', self.api_key),
			json={
				'name': interest_name,
				'display_order': 1,
			}
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json().get('name'), interest_name)

	def test_can_get_a_specific_interest(self):

		# create the category
		category_name = self._get_guid()
		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
			json={
				'title': category_name,
				'type': 'checkboxes'
			}
		)

		category_id = response.json().get('id')

		# create an interest in that category
		interest_name = self._get_guid()

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests'.format(self.subdomain, self.list_id, category_id),
			auth=('apikey', self.api_key),
			json={
				'name': interest_name,
				'display_order': 1,
			}
		)

		interest_id = response.json().get('id')		

		# retrieve that interest
		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests/{}'.format(self.subdomain, self.list_id, category_id, interest_id),
			auth=('apikey', self.api_key)
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json().get('name'), interest_name)		
		self.assertEqual(response.json().get('id'), interest_id)		


	def test_get_all_interests_of_category_with_interests(self):

		# create the category
		category_name = self._get_guid()
		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(self.subdomain, self.list_id),
			auth=('apikey', self.api_key),
			json={
				'title': category_name,
				'type': 'checkboxes'
			}
		)

		category_id = response.json().get('id')

		# create two interests in that category
		interest_one_name = self._get_guid()
		interest_two_name = self._get_guid()

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests'.format(self.subdomain, self.list_id, category_id),
			auth=('apikey', self.api_key),
			json={
				'name': interest_one_name,
				'display_order': 1,
			}
		)
		interest_one_id = response.json().get('id')	

		response = requests.post(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests'.format(self.subdomain, self.list_id, category_id),
			auth=('apikey', self.api_key),
			json={
				'name': interest_two_name,
				'display_order': 1,
			}
		)
		interest_two_id = response.json().get('id')

		# get all interests of category (should be two)
		response = requests.get(
			'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests'.format(self.subdomain, self.list_id, category_id),
			auth=('apikey', self.api_key)
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json().get('total_items'), 2)
		self.assertEqual(len(response.json().get('interests')), 2)
		self.assertEqual(response.json().get('interests')[0].get('name'), interest_one_name)
		self.assertEqual(response.json().get('interests')[0].get('id'), interest_one_id)
		self.assertEqual(response.json().get('interests')[1].get('name'), interest_two_name)
		self.assertEqual(response.json().get('interests')[1].get('id'), interest_two_id)

		# print(response.status_code)
		# print(pformat(response.json()))
		
if __name__ == '__main__':
	unittest.main(warnings='ignore') # suppress this warning: ResourceWarning: unclosed <ssl.SSLSocket