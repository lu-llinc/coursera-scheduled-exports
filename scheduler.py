#
# Scheduler 
# Jasper Ginn
# 07/10/2016
#

import os
import requests
import json
import datetime
import time
import courseraresearchexports
from courseraresearchexports.models.ExportRequest import ExportRequest
from courseraresearchexports.exports import api
from courseraresearchexports.exports import utils

'''
TODO:

Add config file:
    * Add option to disable logging
    * Add interval to download tables (days)
    * Add interval to download clickstreams (days)
    * Yes/no for downloading clickstreams/tables
    * ...
'''

'''
Simple logger class
'''

class logger:

	def __init__(self, location):
		self.location = location
		self.date = "{}-{}-{}"

	def logMessage(self, loglevel, message):
		self.loglevel = loglevel
		self.message = message
		self.time = time.strftime("%Y-%m-%d %H:%M:%S", localtime())
		# Write
		with open(self.location, 'a') as f:
			f.write("{}	{}	{}".format(self.time, self.loglevel, self.message))
			f.write("\n")

'''
Create a request to the API
'''

class call:
    
    def __init__(self, course_slug):
        self.course_slug = course_slug
    
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
        # If not 200, raise error
        if str(resp) != '<Response [200]>':
            raise ValueError("Server returned {}. Check whether course name is correct.".format(str(resp)))
        json_data = resp.json()
        # Get courseID
        course_id = json_data["elements"][0]["id"]
        # Return
        return course_id
        
    '''
    Request sql data
    '''
    
    def request_schemas(self, course_id, export_type = "RESEARCH_WITH_SCHEMAS", anonymity_level = "HASHED_IDS_NO_PII", 
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
                                            
        # Add log entry --> TODO
        
        # Construct request
        er = ExportRequest(course_id=course_id, export_type=export_type, anonymity_level = anonymity_level, 
                           statement_of_purpose = statement_of_purpose, schema_names = schema_names)
        # Fire request
        ERM = api.post(er)[0]
        
        # Add log entry --> TODO
        
        # Add id to self
        self.id_ = ERM.to_json()['id']
        
        
    '''
    Request clickstream data
    '''
    
    def request_clickstream(self, course_id, export_type = "RESEARCH_EVENTING", anonymity_level = "HASHED_IDS_NO_PII", 
                            statement_of_purpose = "Weekly backup of course data", 
                            from_ = datetime.date.today() - datetime.timedelta(days=7), # If you're running it on friday, you want the results from
                            to_ = datetime.date.today() - datetime.timedelta(days=1): # Previous friday to yesterday.
                                            
        # Add log entry --> TODO
        
        # Construct request
        er = ExportRequest(course_id=course_id, export_type=export_type, anonymity_level = anonymity_level, 
                           statement_of_purpose = statement_of_purpose, interval=[str(from_), str(to_))
        # Fire request
        ERM = api.post(er)[0]
        
        # Add log entry --> TODO
        
        # Add id to self
        self.id_ = ERM.to_json()['id']
        
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
                # Get clickstream download links
                return 'clickstreams_ready'
            else:
                return request['download_link']
            
    '''
    Download 