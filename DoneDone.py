#!/usr/bin/env python
import os
import sys
import hashlib
import hmac
import urllib
from base64 import b64encode
import requests

class IssueTracker(object):
        '''Provide access to the DoneDone IssueTracker API.

        See http://www.getdonedone.com/api for complete documentation for the
        API.
        '''
        def __init__(self, domain, token, username, password=None, debug=False):
            '''Default constructor
	    _debug - print debug messages
            domain - company's DoneDone domain
            token - the project API token
            username - DoneDone username
            password - DoneDone password
            '''
            self.baseURL = 'https://%s.mydonedone.com/IssueTracker/API/' % domain
            self.auth = self._calculateAuth(username, token)
            self.token = token
            self.result = None 
            self._debug = debug;

        def _curlCallback(self, result):
            '''PyCurl callback'''
            self.result = result

        def _calculateAuth(self, username, password):
            '''Calculate Basic access authentication string

            username - DoneDone username
            password - DoneDone password
            '''
            return b64encode(username + ':' + password)

       

        def API(self, methodURL, data=None, attachments=None, update=False,post=False):
            '''Perform generic API calling

            This is the base method for all IssueTracker API calls.

            methodURL - IssueTracker method URL
            data - optional POST form data
            attachemnts - optional list of file paths
            update - flag to indicate if this is a PUT operation
            '''
            url = self.baseURL + methodURL
            headers = {}
            files = []

            if attachments:
                request_method = requests.post
                if attachments:
                    files = []
                    for index, attachment in enumerate(attachments):
                        files.append(('attachment-%d' % index, attachment))
            else:
                request_method = requests.get

            if update:
                request_method = requests.put

            if post:
 		request_method = requests.post

            headers["Authorization"] = "Basic %s" % self.auth
            return request_method(url, data=data, files=files, headers=headers)

        def getProjects(self, loadWithIssues=False):
            '''Get all Projects with the API enabled

            loadWithIssues - Passing true will deep load all of the projects as
            well as all of their active issues.
            '''
            url = 'Projects/true' if loadWithIssues else 'Projects'
            return self.API(url)

        def getPriorityLevels(self):
            '''Get priority levels'''
            return self.API('PriorityLevels')

        def getAllPeopleInProject(self, projectID):
            '''Get all people in a project

            projectID - project id
            '''
            return self.API('PeopleInProject/%s' % projectID)

        def getAllIssuesInProject(self, projectID):
            '''Get all issues in a project

            projectID - project id
            '''
            return self.API('IssuesInProject/%s' % projectID)

        def doesIssueExist(self, projectID, issueID):
            '''Check if an issue exists

            projectID - project id
            issueID - issue id
            '''
            return self.API('DoesIssueExist/%s/%s' % (projectID, issueID))

        def getPotentialStatusesForIssue(self, projectID, issueID):
            '''Get potential statuses for issue

            Note: If you are an admin, you'll get both all allowed statuses
            as well as ALL statuses back from the server

            projectID - project id
            issueID - issue id
            '''
            return self.API(
                'PotentialStatusesForIssue/%s/%s' % (
                    str(projectID),
                    str(issueID)))

        def getIssueDetails(self, projectID, issueID):
            '''Note: You can use this to check if an issue exists as well,
            since it will return a 404 if the issue does not exist.'''
            return self.API(
                'Issue/%s/%s' % (
                    str(projectID),
                    str(issueID)))

        def getPeopleForIssueAssignment(self, projectID, issueID):
            '''Get a list of people that cane be assigend to an issue'''
            return self.API(
                'PeopleForIssueAssignment/%s/%s' % (
                    str(projectID),
                    str(issueID)))

        def createIssue(
                self, projectID, title, priorityID, resolverID, testerID,
                description='',  tags='', watcherIDs='', attachments=None):
            '''Create Issue

            projectID - project id
            title - required title.
            priorityID - priority levels
            resolverID - person assigned to solve this issue
            testerID - person assigned to test and verify if a issue is
            resolved
            description - optional description of the issue
            tags - a string of tags delimited by comma
            watcherIDs - a string of people's id delimited by comma
            attachments - list of file paths
            '''
            data = [
                ('title', title),
                ('priority_level_id', str(priorityID)),
                ('resolver_id', str(resolverID)),
                ('tester_id', str(testerID))]
            if description:
                data.append(('description', description))
            if tags:
                data.append(('tags', tags))
            if watcherIDs:
                data.append(('watcher_ids', str(watcherIDs)))
            return self.API('Issue/%s' % projectID, data, attachments,post=True)

        def createComment(
            self, projectID, issueID, comment,
            peopleToCCIDs=None, attachments=None):
            '''Create Comment on issue

            projectID - project id
            issueID - issue id
            comment - comment string
            peopleToCCIDs - a string of people to be CCed on this comment,
            delimited by comma
            attachments - list of absolute file path.
            '''
            data = [('comment', comment)]

            if peopleToCCIDs:
                data.append(('people_to_cc_ids', peopleToCCIDs))
            return self.API('Comment/%s/%s' % (projectID, issueID), data, attachments,post=True)

        def updateIssue(
            self, projectID, issueID, title=None, priorityID=None,
            resolverID=None, testerID=None, description=None,
            tags=None, stateID=None, attachments=None):
            '''Update Issue

            If you provide any parameters then the value you pass will be
            used to update the issue. If you wish to keep the value that's
            already on an issue, then do not provide the parameter in your
            PUT data. Any value you provide, including tags, will overwrite
            the existing values on the issue. If you wish to retain the
            tags for an issue and update it by adding one new tag, then
            you'll have to provide all of the existing tags as well as the
            new tag in your tags parameter, for example.

            projectID - project id
            issueID - issue id
            title - required title
            priorityID - priority levels
            resolverID - person assigned to solve this issue
            testerID - person assigned to test and verify if a issue is
            resolved
            description - optional description of the issue
            tags -  a string of tags delimited by comma
            stateID - a valid state that this issue can transition to
            attachments - list of file paths
            '''
            data = []
            if title:
                data.append(('title', title))
            if priorityID:
                data.append(('priority_level_id', str(priorityID)))
            if resolverID:
                data.append(('resolver_id', str(resolverID)))
            if testerID:
                data.append(('tester_id', str(testerID)))
            if description:
                data.append(('description', description))
            if tags:
                data.append(('tags', tags))
            if stateID:
                data.append(('state_id', str(stateID)))
            return self.API('Issue/%s/%s' % (projectID, issueID), data,
                attachments, True)
