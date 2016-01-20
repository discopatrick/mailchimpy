import unittest
from unittest import TestCase
import requests
from uuid import uuid4
from pprint import pformat

from .basemailchimptest import BaseMailChimpTest
from . import config

# It would be helpful in these tests to be able to test specific values, e.g.:
# 
# self.assertEqual(new_list['response'].json().get('name'), list_name)
# 
# However, because we are using betamax, and playing back previously recorded
# http interactions, the responses we receive are not going to be the exact 
# response of the request we just sent. As such, we are only testing those
# values of which we can be sure of the responses, e.g.:
# 
# self.assertEqual(new_list['status_code'], 200)
# self.assertIsNotNone(new_list['response'].json().get('id'))
# 
# Some assertions are left commented below, rather than removed, in case we
# can fix this problem in future.



class BaseMailChimpAPITest(BaseMailChimpTest):

    cassette_dir = 'cassettes/api'


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

        self.assertEqual(self.temp_list['status_code'], 200)
        self.assertIsNotNone(self.temp_list['id'])
        # self.assertEqual(response.json().get('name'), list_name)
        self.assertIsNotNone(self.temp_list['name'])

    def test_getting_a_specific_list(self):

        # retrieve a list
        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists/{}'.format(
                    self.subdomain, self.temp_list['id']),
                auth=('apikey', self.api_key)
            )

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json().get('id'), new_list['id'])
        self.assertIsNotNone(response.json().get('id'))
        # self.assertEqual(response.json().get('name'), new_list['name'])
        self.assertIsNotNone(response.json().get('name'))

    def test_deleting_a_list(self):

        with self.recorder.use_cassette(self.id()):
            result = self._api_delete_list(self.temp_list['id'])

        self.assertEqual(result['response'].content, b'')
        self.assertEqual(result['status_code'], 204)


class MembersAPITest(BaseMailChimpAPITest):

    def test_api_returns_a_response(self):

        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/'.format(self.subdomain),
                auth=('apikey', self.api_key)
            )

        self.assertEqual(response.status_code, 200)

    def test_can_check_if_email_address_is_subscribed_to_list(self):

        with self.recorder.use_cassette(self.id()):
            member = self._api_get_member(self.temp_list['id'])

        self.assertEqual(member['status_code'], 404)

    def test_can_subscribe_a_new_email_to_list(self):

        with self.recorder.use_cassette(self.id()):
            new_subscription = self._api_subscribe_email_to_list(self.temp_list['id'])

        self.assertEqual(new_subscription['status_code'], 200)
        self.assertEqual(new_subscription['status'], 'subscribed')

    def test_subscribing_an_email_that_is_already_subscribed(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange_subscription'.format(self.id())):
            self._api_subscribe_email_to_list(self.temp_list['id'], email)

        with self.recorder.use_cassette(self.id()):
            resubscription_attempt = self._api_subscribe_email_to_list(self.temp_list['id'], email)

        self.assertEqual(resubscription_attempt['status_code'], 400)
        self.assertEqual(resubscription_attempt['title'], 'Member Exists')

    def test_subscribing_a_known_disallowed_email(self):

        known_disallowed_email = 'anything@example.com'

        with self.recorder.use_cassette(self.id()):
            subscription = self._api_subscribe_email_to_list(self.temp_list['id'], known_disallowed_email)

        self.assertEqual(subscription['status_code'], 400)
        self.assertEqual(subscription['title'], 'Invalid Resource')

    def test_unsubscribing_an_email(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            self._api_subscribe_email_to_list(self.temp_list['id'], email)

        with self.recorder.use_cassette(self.id()):
            unsubscription = self._api_unsubscribe_email_from_list(self.temp_list['id'], email)

        self.assertEqual(unsubscription['status_code'], 200)
        self.assertEqual(unsubscription['status'], 'unsubscribed')

    def test_unsubscribing_an_email_that_is_already_unsubscribed(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            # subscribe an email address to the list
            self._api_subscribe_email_to_list(self.temp_list['id'], email)

            # unsubscribe that same email address from the list
            self._api_unsubscribe_email_from_list(self.temp_list['id'], email)

        # attempt to unsubscribe again
        with self.recorder.use_cassette(self.id()):
            unsub_attempt_two = self._api_unsubscribe_email_from_list(self.temp_list['id'], email)

        self.assertEqual(unsub_attempt_two['status_code'], 200)
        self.assertEqual(unsub_attempt_two['status'], 'unsubscribed')

    def test_unsubscribing_an_email_that_has_never_existed_in_the_list(self):

        email = self._get_fresh_email()

        with self.recorder.use_cassette(self.id()):
            unsubscription = self._api_unsubscribe_email_from_list(self.temp_list['id'], email)

        self.assertEqual(unsubscription['status_code'], 404)
        self.assertEqual(unsubscription['title'], 'Resource Not Found')

class InterestCategoriesAPITest(BaseMailChimpAPITest):

    def test_get_all_interest_categories_of_list(self):

        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories'.format(
                    self.subdomain, self.temp_list['id']),
                auth=('apikey', self.api_key),
            )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('categories'))

    def test_create_interest_category_in_list(self):

        with self.recorder.use_cassette(self.id()):
            new_category = self._api_create_interest_category(self.temp_list['id'])

        self.assertEqual(new_category['status_code'], 200)
        self.assertIsNotNone(new_category['id'])

    def test_create_interest_category_of_each_type_in_list(self):

        for category_type in ('checkboxes', 'dropdown', 'radio', 'hidden'):
            with self.recorder.use_cassette('{}_{}'.format(self.id(), category_type)):
                new_category = self._api_create_interest_category(self.temp_list['id'], category_type)

                self.assertEqual(new_category['status_code'], 200)
                self.assertEqual(new_category['type'], category_type)

    def test_get_specific_interest_category(self):

        with self.recorder.use_cassette('{}_arrange'.format(self.id())):
            new_category = self._api_create_interest_category(self.temp_list['id'])

        # retrieve that category
        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}'.format(
                    self.subdomain, self.temp_list['id'], new_category['id']),
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

        with self.recorder.use_cassette('{}_arrange_category'.format(self.id())):
            new_category = self._api_create_interest_category(self.temp_list['id'])

        # get all the interests of the category (should be none)
        with self.recorder.use_cassette(self.id()):
            interests = self._api_get_interests(self.temp_list['id'], new_category['id'])

        self.assertEqual(interests['status_code'], 200)
        self.assertEqual(interests['interests'], [])
        self.assertEqual(interests['total_items'], 0)

    def test_can_create_an_interest_in_a_category(self):

        with self.recorder.use_cassette('{}_arrange_category'.format(self.id())):
            new_category = self._api_create_interest_category(self.temp_list['id'])

        with self.recorder.use_cassette(self.id()):
            new_interest = self._api_create_interest(self.temp_list['id'], new_category['id'])

        self.assertEqual(new_interest['status_code'], 200)
        # self.assertEqual(response.json().get('name'), interest_name)
        self.assertIsNotNone(new_interest['response'].json().get('name'))

    def test_can_get_a_specific_interest(self):

        with self.recorder.use_cassette('{}_arrange_category'.format(self.id())):
            new_category = self._api_create_interest_category(self.temp_list['id'])

        with self.recorder.use_cassette('{}_arrange_interest'.format(self.id())):
            new_interest = self._api_create_interest(self.temp_list['id'], new_category['id'])

        # retrieve the interest
        with self.recorder.use_cassette(self.id()):
            response = self.session.get(
                'https://{}.api.mailchimp.com/3.0/lists/{}/interest-categories/{}/interests/{}'.format(
                    self.subdomain, self.temp_list['id'], new_category['id'], new_interest['id']),
                auth=('apikey', self.api_key)
            )

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json().get('name'), interest_name)
        self.assertIsNotNone(response.json().get('name'))
        # self.assertEqual(response.json().get('id'), interest_id)
        self.assertIsNotNone(response.json().get('id'))

    def test_get_all_interests_of_category_with_interests(self):

        with self.recorder.use_cassette('{}_arrange_category'.format(self.id())):
            new_category = self._api_create_interest_category(self.temp_list['id'])

        # create two interests in the category
        with self.recorder.use_cassette('{}_arrange_interest_one'.format(self.id())):
            new_interest_one = self._api_create_interest(self.temp_list['id'], new_category['id'])

        with self.recorder.use_cassette('{}_arrange_interest_two'.format(self.id())):
            new_interest_two = self._api_create_interest(self.temp_list['id'], new_category['id'])

        # get all interests of category (should be two)
        with self.recorder.use_cassette(self.id()):
            interests = self._api_get_interests(self.temp_list['id'], new_category['id'])

        self.assertEqual(interests['status_code'], 200)
        self.assertEqual(interests['total_items'], 2)
        self.assertEqual(len(interests['interests']), 2)
        # self.assertEqual(response.json().get('interests')[0].get('name'), interest_one_name)
        # self.assertEqual(response.json().get('interests')[0].get('id'), interest_one_id)
        # self.assertEqual(response.json().get('interests')[1].get('name'), interest_two_name)
        # self.assertEqual(response.json().get('interests')[1].get('id'), interest_two_id)

        # print(response.status_code)
        # print(pformat(response.json()))
