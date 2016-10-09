#! /usr/bin/env python

'''
Copyright 2016 Leiden University

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''
# Schedule coursera research exports downloads
# Jasper Ginn
# 07/10/2016
'''

import os
import requests
import json
import datetime
import time
import logging
import courseraresearchexports
from courseraresearchexports.models.ExportRequest import ExportRequest
from courseraresearchexports.models.ClickstreamDownloadLinksRequest import ClickstreamDownloadLinksRequest
from courseraresearchexports.exports import api
from courseraresearchexports.exports import utils

'''
Create a request to the API
'''

class coursera:

    def __init__(self, course_slug):
        self.course_slug = course_slug

        logging.info("Started download for course {}".format(course_slug))

    '''
    Retrieve course id based on course slug
    '''

    def get_course_id(self):
        # Link below retrieves JSON file with course information based on course name
        base_url = "https://www.coursera.org/api/onDemandCourses.v1?q=slug&slug="
        # Paste
        url_tmp = base_url + self.course_slug
        # GET
        resp = requests.get(url_tmp)
        # If not ok
        if not resp.ok:
            # Log event
            logging.error("Cannot fetch course id ({})".format(self.course_slug))
            raise ValueError("Server returned {}. Check whether course name is correct.".format(str(resp)))
        json_data = resp.json()
        # Get courseID
        course_id = json_data["elements"][0]["id"]
        # Return
        self.course_id = course_id

    '''
    Request sql data
    '''

    def request_schemas(self, export_type = "RESEARCH_WITH_SCHEMAS", anonymity_level = "HASHED_IDS_NO_PII",
                        statement_of_purpose = "Weekly backup of course data",
                        schema_names = ["demographics",
                                        "users",
                                        "course_membership",
                                        "course_progress",
                                        "feedback",
                                        "assessments",
                                        "course_grades",
                                        "peer_assignments",
                                        "discussions",
                                        "programming_assignments",
                                        "course_content"]):

        logging.info("Requesting table data ({})".format(self.course_slug))

        # Construct request
        er = ExportRequest(course_id=self.course_id, export_type=export_type, anonymity_level = anonymity_level,
                           statement_of_purpose = statement_of_purpose, schema_names = schema_names)
        # Fire request
        try:
            ERM = api.post(er)[0]
        except: # Find out specific error
            logging.error("Request failed ({})".format(self.course_slug))
            raise ValueError("Failed request")

        logging.info("Request successfull ({})".format(self.course_slug))

        # Add info to self
        vals = ERM.to_json()
        self.id_ = vals['id']
        self.type_ = "TABLE"
        self.metadata = vals["metadata"]
        self.schemaNames = vals["schemaNames"]

    '''
    Request clickstream data
    '''

    def request_clickstream(self, export_type = "RESEARCH_EVENTING", anonymity_level = "HASHED_IDS_NO_PII",
                            statement_of_purpose = "Weekly backup of course data"):

        self.interval = [str(datetime.date.today() - datetime.timedelta(days=7)), # If you're running it on friday, you want the results from
                    str(datetime.date.today() - datetime.timedelta(days=1))] # Previous friday to yesterday.]

        logging.info("Requesting clickstream data ({}) for period {} to {}".format(self.course_slug, self.interval[0], self.interval[1]))

        # Construct request
        er = ExportRequest(course_id=self.course_id, export_type=export_type, anonymity_level = anonymity_level,
                           statement_of_purpose = statement_of_purpose, interval=self.interval)
        # Fire request
        try:
            ERM = api.post(er)[0]
        except:
            logging.error("Request failed ({})".format(self.course_slug))
            raise ValueError("Failed request")

        logging.info("Request successfull ({})".format(self.course_slug))

        # Add id to self
        vals = ERM.to_json()
        self.id_ = vals['id']
        self.type_ = "CLICKSTREAM"
        self.metadata = vals["metadata"]
        self.schemaNames = "NONE"

    '''
    Check if download is ready every 10 minutes
    '''

    def status_export(self, interval = 600):

        # Get status of export download
        request = api.get(self.id_)[0].to_json()

        # If pending, wait for it to jump to in progress or successful.
        while request['status'] == 'PENDING':
            print 'Api returned {} for job {}. Retrying in 10 seconds.'format(request['status'], self.course_slug)
            time.sleep(10)
            request = api.get(self.id_)[0].to_json()
        # If in progress, check for every interval.
        while request['status'] == 'IN_PROGRESS':
            print 'API returned {} for job {}. Retrying in {} minutes.'.format(request['status'], self.course_slug, str(interval / 60))
            time.sleep(interval)
            # Check
            request = api.get(self.id_)[0].to_json()
        if request['status'] == 'SUCCESSFUL':
            # if clickstream data, return download links, else return download link for
            if request['exportType'] == 'RESEARCH_EVENTING':
                # Create request for links
                CLL = ClickstreamDownloadLinksRequest(course_id = self.course_id,
                                                      interval = self.interval)
                links = api.get_clickstream_download_links(CLL)
                return links
            else:
                # This is table (sql) data.
                return [request['download_link']]
        else:
            logging.error("Unknown status <{}> returned by api".format(request['status']))
            raise ValueError("Unknown status returned by api")

    '''
    Download data
    '''

    def download(self, link, location):

        print "Downloading file from url {}".format(link)
        logging.info("Downloading file ({})".format(self.course_slug))

        resp = utils.download_url(link, location)

        # Return
        return location

    '''
    Add metadata
    '''

    def return_metadata(self):

        # Create metadata
        mt = {"course":self.course_slug, "course_id":self.course_id, "exportType":self.type_,
              "meta":self.metadata, "schema_names":self.schemaNames}
        # Return
        return mt
