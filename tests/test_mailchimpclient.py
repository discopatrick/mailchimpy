import unittest
from unittest import TestCase
from uuid import uuid4
import requests
import hashlib
from betamax import Betamax

from .basemailchimptest import BaseMailChimpClientTest
from mailchimpy.mailchimpy import MailChimpClient
from . import config


class MailChimpClientTest(BaseMailChimpClientTest):

	def setUp(self):

		super().setUp()

		self.mc = MailChimpClient(self.api_key)
		self.recorder = Betamax(self.mc.session)

	def get_md5(self, string):

		hashobject = hashlib.md5(string.encode())
		md5 = hashobject.hexdigest()
		return md5

	def test_check_subscription_status_returns_false_for_email_address_not_subscribed_to_list(self):

		email = self._get_fresh_email()

		with self.recorder.use_cassette(self.id(), serialize_with='prettyjson'):
			subscribed = self.mc.check_subscription_status(email, self.list_id)

			self.assertIsNotNone(subscribed)
			self.assertFalse(subscribed)

	def test_check_subscription_status_returns_true_for_email_address_already_subscribed_to_list(self):

		# subscribe an email address to the list (via API directly)
		email = self._get_fresh_email()
		self._api_subscribe_email_to_list(email, self.list_id, self.mc.session)

		# check that email's subscription status (via the client)
		# with self.recorder.use_cassette(self.id(), serialize_with='prettyjson'):
		subscribed = self.mc.check_subscription_status(email, self.list_id)

		self.assertIsNotNone(subscribed)
		self.assertTrue(subscribed)

	def test_subscribe_email_to_list_returns_true_on_success(self):

		# with self.recorder.use_cassette(self.id(), serialize_with='prettyjson'):
		success = self.mc.subscribe_email_to_list(self._get_fresh_email(), self.list_id)

		self.assertTrue(success)

	def test_subscribe_email_to_list_returns_false_for_email_already_subscribed(self):

		# subscribe an email address to the list (via API directly)
		email = self._get_fresh_email()
		self._api_subscribe_email_to_list(email, self.list_id, self.mc.session)

		# attempt to subscribe that same email a second time (via the client)
		# with self.recorder.use_cassette(self.id(), serialize_with='prettyjson'):
		success = self.mc.subscribe_email_to_list(email, self.list_id)

		self.assertIsNotNone(success)
		self.assertFalse(success)

	def test_unsubscribe_email_from_list_returns_true_on_success(self):

		# subscribe an email address to the list (via API directly)
		email = self._get_fresh_email()
		self._api_subscribe_email_to_list(email, self.list_id, self.mc.session)		

		# unsubscribe that email address (via the client)
		# with self.recorder.use_cassette(self.id(), serialize_with='prettyjson'):
		success = self.mc.unsubscribe_email_from_list(email, self.list_id)

		self.assertTrue(success)

	def test_unsubscribe_email_from_list_returns_true_even_when_it_was_already_unsubscribed(self):

		# subscribe an email address to the list (via API directly)
		email = self._get_fresh_email()
		self._api_subscribe_email_to_list(email, self.list_id, self.mc.session)

		# unsubscribe that email address (also via API directly)
		email_md5 = self.get_md5(email)
		response = requests.patch(
			'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(self.subdomain, self.list_id, email_md5),
			auth=('apikey', self.api_key),
			json={'status': 'unsubscribed'}
		)

		# attempt to unsubscribe a second time (via the client)
		# with self.recorder.use_cassette(self.id(), serialize_with='prettyjson'):
		success = self.mc.unsubscribe_email_from_list(email, self.list_id)

		self.assertTrue(success)		

	def test_unsubscribe_email_from_list_returns_none_when_email_did_not_exist_on_list(self):

		email = self._get_fresh_email()

		# with self.recorder.use_cassette(self.id(), serialize_with='prettyjson'):
		success = self.mc.unsubscribe_email_from_list(email, self.list_id)

		self.assertIsNone(success)