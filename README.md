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

* Clone this repo.
* `pip install -r requirements.txt`
* Create a file inside tests/ called `config.py` containing these values (see `config-example.py` for an example):
	* MAILCHIMP_API_KEY (your MailChimp acccount API key)
	* MAILCHIMP_LIST_ID (the id of a list you have created for test purposes - do not use a real list!)
	* EMAIL_ALREADY_SUBSCRIBED_TO_LIST (an email address that you know is already subscribed to your list)
* Run one of the test classes below.

There are two test classes:

### MailChimpClientTest

These tests are for our client. From the project root, run:
`python3 -m tests.mailchimpclient_test`

### MailChimpAPITest

These tests are for the MailChimp API itself. While we wouldn't normally want to test the API directly, these tests help us understand how the API works, and will warn us of any changes to the API that may be introduced. From the project root, run:
`python3 -m tests.mailchimpapi_test`