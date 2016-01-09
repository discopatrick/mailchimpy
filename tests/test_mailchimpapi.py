import unittest
from unittest import TestCase
import requests
from uuid import uuid4
from pprint import pformat

from .basemailchimptest import BaseMailChimpTest, BaseMailChimpAPITest
from . import config


class ListsAPITest(BaseMailChimpAPITest):

    def test_getting_all_lists(self):

        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists'.format(
                    self.subdomain),
                auth=('apikey', self.api_key)
            )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('lists'))

    def test_creating_a_list(self):

        list_name = self._get_guid()

        with self.recorder.use_cassette(self.id()):
            new_list = self._api_create_new_list()

        self.assertEqual(new_list['response'].status_code, 200)
        self.assertIsNotNone(new_list['response'].json().get('id'))
        # self.assertEqual(response.json().get('name'), list_name)
        self.assertIsNotNone(new_list['response'].json().get('name'))

    def test_getting_a_specific_list(self):

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            new_list = self._api_create_new_list()

        # retrieve that list
        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists/{}'.format(
                    self.subdomain, new_list['id']),
                auth=('apikey', self.api_key)
            )

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json().get('id'), new_list['id'])
        self.assertIsNotNone(response.json().get('id'))
        # self.assertEqual(response.json().get('name'), new_list['name'])
        self.assertIsNotNone(response.json().get('name'))

        # print(response.status_code)
        # print(pformat(response.json()))

    def test_deleting_a_list(self):

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            new_list = self._api_create_new_list()

        with self.recorder.use_cassette(self.id()):
            result = self._api_delete_list(new_list['id'])

        self.assertEqual(result['response'].content, b'')
        self.assertEqual(result['response'].status_code, 204)


class MembersAPITest(BaseMailChimpAPITest):

    def test_api_returns_a_response(self):

        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/'.format(self.subdomain),
                auth=('apikey', self.api_key)
            )

        self.assertEqual(response.status_code, 200)

    def test_can_check_if_email_address_is_subscribed_to_list(self):

        email = self._get_fresh_email()
        email_md5 = self._get_md5(email)

        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                    self.subdomain, self.list_id, email_md5),
                auth=('apikey', self.api_key)
            )

        self.assertEqual(response.status_code, 404)

    def test_can_subscribe_a_new_email_to_list(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette(self.id()):
            response = self.session.post(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(
                    self.subdomain, self.list_id),
                auth=('apikey', self.api_key),
                json={'email_address': email, 'status': 'subscribed'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'subscribed')

    def test_subscribing_an_email_that_is_already_subscribed(self):

        email = self._get_fresh_email()

        # subscribe an email address to the list
        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            self._api_subscribe_email_to_list(email, self.list_id)

        # attempt to subscribe that same email address again
        with self.recorder.use_cassette(self.id()):
            response = self.session.post(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(
                    self.subdomain, self.list_id),
                auth=('apikey', self.api_key),
                json={'email_address': email, 'status': 'subscribed'}
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('title'), 'Member Exists')

    def test_subscribing_a_known_disallowed_email(self):

        known_disallowed_email = 'anything@example.com'

        with self.recorder.use_cassette(self.id()):
            response = self.session.post(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members'.format(
                    self.subdomain, self.list_id),
                auth=('apikey', self.api_key),
                json={'email_address': known_disallowed_email,
                      'status': 'subscribed'}
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('title'), 'Invalid Resource')

    def test_unsubscribing_an_email(self):

        email = self._get_fresh_email()

        # subscribe an email address to the list
        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            self._api_subscribe_email_to_list(email, self.list_id)

        email_md5 = self._get_md5(email)

        # unsubscribe that same email address from the list
        with self.recorder.use_cassette(self.id()):
            response = self.session.patch(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                    self.subdomain, self.list_id, email_md5),
                auth=('apikey', self.api_key),
                json={'status': 'unsubscribed'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'unsubscribed')

    def test_unsubscribing_an_email_that_is_already_unsubscribed(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list
            self._api_subscribe_email_to_list(email, self.list_id)

            # unsubscribe that same email address from the list
            email_md5 = self._get_md5(email)
            response = self.session.patch(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                    self.subdomain, self.list_id, email_md5),
                auth=('apikey', self.api_key),
                json={'status': 'unsubscribed'}
            )

        # attempt to unsubscribe again
        with self.recorder.use_cassette(self.id()):
            response = self.session.patch(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                    self.subdomain, self.list_id, email_md5),
                auth=('apikey', self.api_key),
                json={'status': 'unsubscribed'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'unsubscribed')

    def test_unsubscribing_an_email_that_has_never_existed_in_the_list(self):

        email = self._get_fresh_email()
        email_md5 = self._get_md5(email)

        with self.recorder.use_cassette(self.id()):
            response = self.session.patch(
                'https://{}.api.mailchimp.com/3.0/lists/{}/members/{}'.format(
                    self.subdomain, self.list_id, email_md5),
                auth=('apikey', self.api_key),
                json={'status': 'unsubscribed'}
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get('title'), 'Resource Not Found')


class InterestCategoriesAPITest(BaseMailChimpAPITest):

    def test_get_all_interest_categories_of_list(self):

        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(
                    self.subdomain, self.list_id),
                auth=('apikey', self.api_key),
            )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('categories'))

    def test_create_interest_category_in_list(self):

        with self.recorder.use_cassette(self.id()):
            new_category = self._api_create_interest_category(self.list_id)

        self.assertEqual(new_category['response'].status_code, 200)
        self.assertIsNotNone(new_category['response'].json().get('id'))

    def test_create_interest_category_of_each_type_in_list(self):

        for category_type in ('checkboxes', 'dropdown', 'radio', 'hidden'):
            with self.recorder.use_cassette('{}_{}'.format(self.id(), category_type)):
                new_category = self._api_create_interest_category(self.list_id, category_type)

                self.assertEqual(new_category['response'].status_code, 200)
                self.assertEqual(new_category['response'].json().get('type'), category_type)

    def test_get_specific_interest_category(self):

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            new_category = self._api_create_interest_category(self.list_id)

        # retrieve that category
        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}'.format(
                    self.subdomain, self.list_id, new_category['id']),
                auth=('apikey', self.api_key)
            )

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json().get('title'), category_name)
        self.assertIsNotNone(response.json().get('title'))


class InterestsAPITest(BaseMailChimpAPITest):
    """
    Testing interests is currently done against an isolated list
    for each test, as each list has a maximum of 60 interests across all
    interest-categories for that list.
    """

    def test_get_all_interests_of_empty_category(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        with self.recorder.use_cassette('{}_arrange_category'.format(self.id())):
            new_category = self._api_create_interest_category(self.list_id)

        # get all the interests of the category (should be none)
        with self.recorder.use_cassette(self.id()):
            interests = self._api_get_interests(new_list['id'], new_category['id'])

        self.assertEqual(interests['response'].status_code, 200)
        self.assertEqual(interests['interests'], [])
        self.assertEqual(interests['total_items'], 0)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_can_create_an_interest_in_a_category(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        with self.recorder.use_cassette('{}_arrange_category'.format(self.id())):
            new_category = self._api_create_interest_category(self.list_id)

        with self.recorder.use_cassette(self.id()):
            new_interest = self._api_create_interest(new_list['id'], new_category['id'])

        self.assertEqual(new_interest['response'].status_code, 200)
        # self.assertEqual(response.json().get('name'), interest_name)
        self.assertIsNotNone(new_interest['response'].json().get('name'))

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_can_get_a_specific_interest(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        with self.recorder.use_cassette('{}_arrange_category'.format(self.id())):
            new_category = self._api_create_interest_category(self.list_id)

        with self.recorder.use_cassette('{}_arrange_interest'.format(self.id())):
            new_interest = self._api_create_interest(new_list['id'], new_category['id'])

        # retrieve the interest
        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests/{}'.format(
                    self.subdomain, new_list['id'], new_category['id'], new_interest['id']),
                auth=('apikey', self.api_key)
            )

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json().get('name'), interest_name)
        self.assertIsNotNone(response.json().get('name'))
        # self.assertEqual(response.json().get('id'), interest_id)
        self.assertIsNotNone(response.json().get('id'))

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

    def test_get_all_interests_of_category_with_interests(self):

        with self.recorder.use_cassette('{}_arrange_list'.format(self.id())):
            new_list = self._api_create_new_list()

        with self.recorder.use_cassette('{}_arrange_category'.format(self.id())):
            new_category = self._api_create_interest_category(self.list_id)

        # create two interests in the category
        with self.recorder.use_cassette('{}_arrange_interest_one'.format(self.id())):
            new_interest_one = self._api_create_interest(new_list['id'], new_category['id'])

        with self.recorder.use_cassette('{}_arrange_interest_two'.format(self.id())):
            new_interest_two = self._api_create_interest(new_list['id'], new_category['id'])

        # get all interests of category (should be two)
        with self.recorder.use_cassette(self.id()):
            interests = self._api_get_interests(new_list['id'], new_category['id'])

        self.assertEqual(interests['response'].status_code, 200)
        self.assertEqual(interests['total_items'], 2)
        self.assertEqual(len(interests['interests']), 2)
        # self.assertEqual(response.json().get('interests')[0].get('name'), interest_one_name)
        # self.assertEqual(response.json().get('interests')[0].get('id'), interest_one_id)
        # self.assertEqual(response.json().get('interests')[1].get('name'), interest_two_name)
        # self.assertEqual(response.json().get('interests')[1].get('id'), interest_two_id)

        with self.recorder.use_cassette('{}_cleanup'.format(self.id())):
            self._api_delete_list(new_list['id'])

        # print(response.status_code)
        # print(pformat(response.json()))
