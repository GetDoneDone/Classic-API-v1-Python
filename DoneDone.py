#!/usr/bin/env python
import os
import sys
import pycurl
import hashlib
import hmac
from base64 import b64encode

class IssueTracker(object):
        '''Provide access to the DoneDone IssueTracker API.

        See http://www.getdonedone.com/api for complete documentation for the
        API.
        '''
        def __init__(self, domain, token, username, password):
            '''Default constructor

            domain - company's DoneDone domain
            token - the project API token
            username - DoneDone username
            password - DoneDone password
            '''
            self.baseURL = 'https://%s.mydonedone.com/IssueTracker/API/' % domain
            self.auth = self._calculateAuth(username, password)
            self.token = token
            self.result = None

        def _curlCallback(self, result):
            '''PyCurl callback'''
            self.result = result

        def _calculateAuth(self, username, password):
            '''Calculate Basic access authentication string

            username - DoneDone username
            password - DoneDone password
            '''
            return b64encode(username + ':' + password)

        def _calculateSignature(self, url, data=None):
            '''Calculate Signature for each request

            url - DoneDone API url
            data - optional POST form data
            '''
            if data:
                for index, value in list(
                    enumerate(sorted(data, key=lambda data: data[0]))):
                    url += str(value[0])+ str(value[1])

            return b64encode(hmac.new(
                self.token, url,
                digestmod=hashlib.sha1).digest())

        def API(self, methodURL, data=None, attachments=None, update=False):
            '''Perform generic API calling

            This is the base method for all IssueTracker API calls.

            methodURL - IssueTracker method URL
            data - optional POST form data
            attachemnts - optional list of file paths
            update - flag to indicate if this is a PUT operation
            '''
            url = self.baseURL + methodURL
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.HTTPHEADER, [
                'Authorization: Basic %s' % self.auth,
                'X-DoneDone-Signature: %s' % self._calculateSignature(url, data)
            ])
            if data or attachments:
                if update:
                    curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
                else:
                    curl.setopt(pycurl.POST, True)
                if attachments:
                    files = []
                    i = 0
                    for item in attachments:
                        files.append(pycurl.FORM_FILE)
                        files.append(item)
                        data.append(('attachment-%s' % i, (pycurl.FORM_FILE,
                            item)))
                        i += 1

                curl.setopt(pycurl.HTTPPOST, data)

            try:
                curl.setopt(pycurl.WRITEFUNCTION, self._curlCallback)
                curl.perform()
                curl.close()
                return self.result
            except:
                return sys.exc_info()[0]

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
            return self.API('Issue/%s' % projectID, data, attachments)

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
            return self.API('Comment/%s/%s' % (projectID, issueID), data, attachments)

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
