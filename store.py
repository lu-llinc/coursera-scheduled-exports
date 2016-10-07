#
# Download data and upload to gcloud bucket
# Jasper Ginn
# 07/10/2016
#

from google.cloud import storage
import logging
import os

'''
Todo:
    * Config file with GC information
    * Config file with clickstream bucket and sql bucket
'''

# SEE:
# http://stackoverflow.com/questions/24811645/renaming-files-in-google-cloud-storage
# https://cloud.google.com/appengine/docs/flexible/python/using-cloud-storage

class gcloud:
    
    def __init__(self, file_path, course_slug, project_id, gcloud_bucket_name):
        self.projId = project_id
        self.bucket = gcloud_bucket_name
        # Check if file path exists
        # Set up log
        
    # Read metadata file in folder. 
    # Determine whether file == table or clickstream
    # Determine path in bucket based on type and course_slug
    # Determine whether file already exists in bucket
    # Upload file 
    # Delete local file 
    # Append metadata file to a local csv with requests
        
        