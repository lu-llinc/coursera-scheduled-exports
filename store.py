#! /usr/bin/env python

'''
# Download data and upload to gcloud bucket
# Jasper Ginn
# 07/10/2016
'''

import logging
import os
import shutil

class gcloud:
    
    def __init__(self, course_slug,gcloud_mounting_path, gcloud_bucket_name, type_,
                 data_folder = "{}/{}/".format(os.getcwd(), "data")):
        self.data_folder = data_folder
        self.course_slug = course_slug
        self.gmp = gcloud_mounting_path,
        self.bucket = gcloud_bucket_name
        self.type_ = type_
        
        '''
        Start logging
        '''
        logging.basicConfig(filename = "store.log", filemode='a', format='%(asctime)s %(message)s', 
                            level=logging.INFO)
        logging.info("Copying data for course {}".format(self.course_slug))
        
        '''
        Check if data folder exists
        '''
        if not os.path.exists(self.data_folder):
            logging.error("Folder {} does not exist.".format(self.data_folder))
            raise ValueError("Folder {} does not exist.".format(self.data_folder))
        
        '''
        Construct folder paths
        '''
        self.copyFrom = "{}/{}/".format(self.data_folder, self.course_slug)
        self.copyTo = "{}/{}/{}/".format(self.gmp, self.type_, self.course_slug)
    
    '''
    List files in directory and detect changes
    '''
    
    def changes(self):
        
        # Which files are not in the target directory?
        copyFrom_files = os.listdir(self.copyFrom)
        copyTo_files = os.listdir(self.copyTo)
        files = [f for file in copyFrom_files if f not in copyTo_files]
            
        self.files_to_copy = files

    '''
    Copy files to destination folder
    '''
    
    def copy(self):
        
        # For each file, copy to mounted gcloud bucket
        for file in self.files_to_copy:
            try:
                shutil.copy2("{}/{}".format(self.copyFrom, file), "{}/{}".format(self.copyTo, file))
                logging.info("Sucessfully copied file {} to the gcloud bucket.".format(file))
                # Remove local file
                os.remove("{}/{}".format(self.copyFrom, file))
            except:
                logging.info("Could not copy file {} to gcloud bucket.".format(file))
    
    # Append metadata file to a local csv with requests
    # Maybe later: add google drive metadata
    # See https://github.com/burnash/gspread
        