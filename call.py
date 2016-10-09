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
# Call scheduler.py and store.py to download files and store them in a mounted google cloud bucket
# Jasper Ginn
# 07/10/2016
'''

import os
import datetime
import argparse
from scheduler import coursera

# NOTE: Removed the gcloud package because we can just download straight away to location

'''
Wrapper to download files.
'''

def coursera_download(course_slugs, request_type, location, store_metadata = True):

    # For each course slug
    for course_slug in course_slugs:

        '''
        Coursera allows at most 1 request per hour. As such, we need to record time of request and wait 60 minutes before we make next request
        '''

        time_now = datetime.datetime.now()

        # Init
        c = coursera(course_slug)
        # Fetch course id
        c.get_course_id()
        # Depending on request type, call tables or clickstream
        if request_type == 'clickstream':
            c.request_clickstream()
        else:
            c.request_schemas()
        # Make request
        links = c.status_export(interval = 600)

        # TODO: Check if folders exist. If they do not, create them!

        # Download data to destination folder
        for link in links:

            # Check if file exists
            filename = urlparse(link).path.split('/')[-1]
            filepath = "{}/{}/{}/{}".format(location, request_type, course_slugs, filename)
            if not os.path.isfile(filepath):
                logging.info("File {} already exists in target location. Moving on ... ".format(filepath))

            c.download(link)
        # Get metadata and store in file
        meta = c.metadata()

'''
Run file
'''

if __name__=="__main__":

    # TODO: Create logger here!

    # Set up parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-export_type","export_type", help="Either one of 'clickstream' or 'tables'", type=str, choices=["clickstream", "tables"])
    parser.add_argument("-slugs","course_slugs", help="EITHER: A course slug name or names separated by a comma, OR: Location of a text file (.txt) containing multiple course slug names. Each slug should be placed on a new line.", type=str)
    parser.add_argument("-l", "location", help="Base directory in which to store the data. The program will automatically add the course slug to the folder and download the data there.", type = str)
    parser.add_argument("-m", "--save_metadata", help="Add the course's metadata to a 'metadata.txt' file saved in the base directory? Defaults to 'True'. If file does not exist, it will be created.", action="store_true")
    args = parser.parse_args()

    # Check directories
    if args.location != None:
        if not os.path.exists(args.location):
            raise RuntimeError("Directory {} does not exist.".format(args.location))

    # Check slugs. If slug is mispelled it will be caught downstream in the coursera class.
    if ".txt" in args.course_slugs:
        with open(args.course_slugs, 'r') as inFile:
            courseSlugs = [line.replace("\n", "").replace(" ", "") for line in inFile]
    else:
        # Check if a filepath
        if os.path.isfile(args.course_slugs):
            raise RuntimeError("You entered a file path but the destination file is not a .txt file.")
        elif '/' in args.course_slugs:
            raise RuntimeError("You entered an invalid file path. Additionally, the file path you specified did not contain a .txt file.")
        elif '.' in args.course_slugs:
            raise RuntimeError("You entered a file type that is currently not supported. Type --help for more information.")
        else:
            courseSlugs = [cl.replace(" ", "") for cl in args.course_slugs.split(",")]

    '''
    Download data for each url
    '''

    coursera_download(courseSlugs, args.export_type, args.location, args.save_metadata)
