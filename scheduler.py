#! /usr/bin/env python

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
from courseraresearchexports.exports import api
from courseraresearchexports.exports import utils

'''
Create a request to the API
'''

class coursera:
    
    def __init__(self, course_slug):
        self.course_slug = course_slug
        self.interval = [str(datetime.date.today() - datetime.timedelta(days=7)), # If you're running it on friday, you want the results from
                         str(datetime.date.today() - datetime.timedelta(days=1))] # Previous friday to yesterday.]
        self.folder = os.getcwd() + "/data/" + course_slug + "/"
        
        # Set up logger
        logging.basicConfig(filename = "scheduler.log", filemode='w', format='%(asctime)s %(message)s', 
                            level=logging.INFO)
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
        
    '''
    Check if download is ready every 10 minutes
    '''
    
    def status_export(self, interval = 600):
        
        # Get status of export download
        request = api.get(self.id_)[0].to_json()
        
        # If ready, return download link; if not, sleep for interval time
        if request['status'] == 'IN_PROGRESS':
            time.sleep(interval) # Add a maximum wating time (e.g. ~4 hours). Else, log error and continue with next course
        elif request['status'] == 'SUCCESSFUL':
            # if clickstream data, return download links, else return download link for 
            if request['exportType'] == 'RESEARCH_EVENTING':
                # Create request for links
                CLL = ClickstreamDownloadLinksRequest(course_id = self.course_id, 
                                                      interval = self.interval)
                # Get links --> add try / except
                links = api.get_clickstream_download_links(CLL)
                return links
            else:
                # This is table (sql) data.
                return request['download_link']
        else:
            logging.error("Unknown status <{}> returned by api".format(request['status']))
            raise ValueError("Unknown status returned by api")
            
    '''
    Download data 
    '''
    
    def download(self, link):
        
        data_folder = os.getcwd() + "/data/"
        # Check if 'data' folder exists
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        # Check if course slug folder exists in data folder
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        
        logging.info("Downloading file ({})".format(course_slug))
        
        resp = utils.download_url(link, self.folder)
        
        # Return
        return self.folder
        
    '''
    Add metadata
    '''
    
    def return_metadata(self):
        
        # Create metadata
        mt = {"course":self.course_slug, "course_id":self.course_id, "exportType":self.type_,
              "meta":self.metadata, "path":self.folder}
        # Return
        return mt
