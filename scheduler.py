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
    * log location
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
        self.interval = [datetime.date.today() - datetime.timedelta(days=7 # Change to number of days in config), # If you're running it on friday, you want the results from
                         datetime.date.today() - datetime.timedelta(days=1)]: # Previous friday to yesterday.]
        self.folder = os.chdir() + "/data/" + course_slug + "/"
        
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
                                            
        # Add log entry --> TODO
        
        # Construct request
        er = ExportRequest(course_id=self.course_id, export_type=export_type, anonymity_level = anonymity_level, 
                           statement_of_purpose = statement_of_purpose, schema_names = schema_names)
        # Fire request
        ERM = api.post(er)[0]
        
        # Add log entry --> TODO
        
        # Add id to self
        self.id_ = ERM.to_json()['id']
        
        
    '''
    Request clickstream data
    '''
    
    def request_clickstream(self, export_type = "RESEARCH_EVENTING", anonymity_level = "HASHED_IDS_NO_PII", 
                            statement_of_purpose = "Weekly backup of course data")
                                            
        # Add log entry --> TODO
        
        # Construct request
        er = ExportRequest(course_id=self.course_id, export_type=export_type, anonymity_level = anonymity_level, 
                           statement_of_purpose = statement_of_purpose, interval=self.interval)
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
                # Create request for links
                CLL = ClickstreamDownloadLinksRequest(course_id = self.course_id, 
                                                      interval = self.interval)
                # Get links --> add try / except
                links = api.get_clickstream_download_links(CLL)
                return links
            else:
                # This is table (sql) data.
                return request['download_link']
            
    '''
    Download data 
    '''
    
    '''
    MERGE DOWNLOAD_URL INTO DOWNLOAD FUNCTION BELOW!!!
    '''

    def download_url(url, dest_folder):
        """
        Download url to dest_folder/FILENAME, where FILENAME is the last
        part of the url path.
        """
        filename = urlparse(url).path.split('/')[-1]
        full_filename = os.path.join(dest_folder, filename)
        response = requests.get(url, stream=True)
        chunk_size = 1024 * 1024
        logging.debug('Writing to file: {}'.format(full_filename))

        with open(full_filename, 'wb') as f:
            for data in tqdm(
                        iterable=response.iter_content(chunk_size),
                        total=int(response.headers['Content-length']) / chunk_size,
                        unit='MB',
                        desc=filename):
                f.write(data)
        return full_filename
    
    def download(self, link):
        
        data_folder = os.chdir() + "/data/"
        
        # Check if 'data' folder exists
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        # Check if course slug folder exists in data folder
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
            
        # Download file to folder
        download_url(link, self.folder)
        