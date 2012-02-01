#!/usr/bin/env python
'''Import projct issues from LightHouse CSV exports

This is a simple example that migrates data from LightHouse to DoneDone using
the Python client. It makes a couple of assumptions. First, the CSV file must
contain columns listed below.

number | state | title | milestone | assigned | created | updated | project | tags

Second, it also assumes the accounts have already been created for the
project, and throws an execption if not. Because LightHouse handles things a
bit different from DoneDone, this script will also create the project with assignee
as both resolver and tester.

'''
import sys
import csv
from simplejson import loads

from time import sleep
from DoneDone import IssueTracker

domain = "Your company domain"
username = "Your donedone username"
password = "Your donedone password"
tokn = "Your project API token"
projectID = "Your donedone project ID"
priorityID = 2 #Assuming medium priority
CSVFilePath = "Path to the CSV file exported from lighthouseapp.com"

class FindDoneDoneID(object):
        '''Find DoneDone ID for a given person'''
        def __init__(self, accountList):
            self.accounts = accountList
        def search(self, name):
            for account in self.accounts:
                if account['Value'] == name:
                    return account['ID']
                else:
                    continue
            raise Exception("Fail to find DoneDone account for %s" % name)

class CSVReader(object):
        '''Read CSV file into a list of dictionaries with column name as key'''
        def __init__(self, CSVFilePath):
            '''Default Constructor'''
            self.reader = csv.reader(
                open(CSVFilePath, 'rb'),
                delimiter = ',',
                quotechar =  '"')

        def __del__(self):
            '''Default Destructor'''
            del self.reader;


        def read(self):
            result = [];
            '''Assume the first row is header and skip it'''
            next(self.reader)
            for row in self.reader:
                result.append({
                    'number' : row[0],
                    'state'  : row[1],
                    'title'  : row[2],
                    'milestone' : row[3],
                    'assigned' : row[4],
                    'created' : row[5],
                    'updated' : row[6],
                    'project' : row[7],
                    'tags' : row[8]})

            return result


issueTracker = IssueTracker(domain, token, username, password)
findID = FindDoneDoneID(loads(issueTracker.getAllPeopleInProject(projectID)))

reader = CSVReader(CSVFilePath)
issueList = reader.read()
for issue in issueList:
    '''Create issue with medium priority'''
    print staging.createIssue(
        projectID, issue['title'], priorityID,
        findID.search(issue['assigned']), findID.search(issue['assigned']),
        "Created by DoneDone API Python client.", issue['tags'])
    '''Pause execution for API request wait time.'''
    sleep(5)
