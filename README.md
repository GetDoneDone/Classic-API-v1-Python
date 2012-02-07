# DoneDone API Python Client Library

## REQUIREMENT
Python version 2.6+ (developed against 2.6.7)
Python's cURL module

## USAGE
To use the Python library with a DoneDone project, you will need to enable the API option under the Project Settings page.

Please see http://www.getdonedone.com/api fore more detailed documentation.

## EXAMPLES
```python
'''Initializing'''
from DoneDone import IssueTracker

domain = "YOUR_COMPANY_DOMAIN" #e.g. wearemammoth
token = "YOUR_API_TOKEN"
username = "YOUR_USERNAME"
password = "YOUR_PASSWORD"

issueTracker = IssueTracker(domain, token, username, password)

'''Calling the API 

API methods can be accessed by calling IssueTracker::API(), or by calling the equivalent shorthand.

The examples below will get all your projects with the API enabled.
'''

issueTracker->API("GetProjects")
# or
issueTracker->getProjects()
```
