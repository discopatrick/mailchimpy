# mailchimpy
A python 3 client for the MailChimp API v3.

## Installation

`pip install git+git://github.com/discopatrick/mailchimpy`

## Example usage

    from mailchimpy import MailChimpClient
    
    mc = MailChimpClient(YOUR_API_KEY)
    
    subscribed = mc.check_subscription_status('someone@example.com', YOUR_LIST_ID)
    
    if not subscribed:
        mc.subscribe_email_to_list('someone@example.com', YOUR_LIST_ID):

## Tests

Currently the tests are calling the API directly, rather than using mock objects, and are therefore not true unit tests. Eventually the test suite will use [betamax](https://github.com/sigmavirus24/betamax) to record http interactions and play them back.

Some of the tests rely on an email address already being subscribed to the list. Because of this, some tests need to make an extra API call to create this subscription before performing the test itself. Wherever this occurs, the 'arrange' step of the test will make API calls via Python's **requests** module, while the 'act' step of the test will use our **mailchimpy** client. This is to ensure (as much as is possible) that we are only testing one thing at a time.

To run the tests:

* Clone this repo.
* `pip install -r requirements.txt`
* Create a file inside `tests/` called `config.py` containing these values (see `config-example.py` for an example):
	* MAILCHIMP_API_KEY (your MailChimp acccount API key)
	* MAILCHIMP_LIST_ID (the id of a list you have created for test purposes - do not use a real list!)
* Run one of the test classes below.

There are two test classes:

### MailChimpClientTest

These tests are for our client. From the project root, run:
`python3 -m tests.mailchimpclient_test`

### MailChimpAPITest

These tests are for the MailChimp API itself. While we wouldn't normally want to test the API directly, these tests help us understand how the API works, and will warn us of any changes to the API that may be introduced. From the project root, run:
`python3 -m tests.mailchimpapi_test`