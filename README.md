# mailchimpy
A python 3 client for the MailChimp API v3, while we're waiting for the official MailChimp python wrapper to be released.

## Installation

`pip install git+git://github.com/discopatrick/mailchimpy`

## Example usage

    from mailchimpy import MailChimpClient
    
    mc = MailChimpClient(YOUR_API_KEY)
    
    (exists, subscribed) = mc.check_subscription_status('someone@example.com', YOUR_LIST_ID)
    
    if not subscribed:
        mc.subscribe_email_to_list('someone@example.com', YOUR_LIST_ID):

## Tests

* Clone this repo.
* `pip install -r requirements.txt`
* Create a file inside `tests/` called `config.py` containing these values (see `config-example.py` for an example):
	* MAILCHIMP_API_KEY (the API key of a MailChimp account you have created for test purposes - do not use a real account!)
* `python3 -m unittest tests.test_mailchimpclient`

In order to minimise the number of requests made to the MailChimp API, and to keep the tests focussed on testing our code rather than the API itself, mailchimpy uses [betamax](https://github.com/sigmavirus24/betamax) to record http interactions and then play them back.

On the first test run, all tests will need to make real calls to the API over the internet. Subsequent test runs will use the betamax recordings, and will be much quicker.

There are two test modules:

### test_mailchimpclient

These tests are for our client. Some of the tests rely on an email address already being subscribed to the list. Because of this, some tests need to make an extra API call to create this subscription before performing the test itself. Wherever this occurs, the 'arrange' step of the test will make API calls via Python's **requests** module, while the 'act' step of the test will use our **mailchimpy** client. This is to ensure (as much as is possible) that we are only testing one thing at a time.

From the project root, run:

`python3 -m unittest tests.test_mailchimpclient`

### test_mailchimpapi

These tests are for the MailChimp API itself. Strictly, we shouldn't be testing the API directly, as it's not our code. However, these tests help us understand how the API works, and will warn us of any changes to the API that may be introduced.

From the project root, run:

`python3 -m unittest tests.test_mailchimpapi`