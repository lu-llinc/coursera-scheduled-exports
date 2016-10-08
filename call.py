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
# Call scheduler.py and store.py to download files and store them in a google cloud bucket
# Jasper Ginn
# 07/10/2016
'''

import argparse
from scheduler import coursera
from store import gcloud
import os

if __name__=="__main__":

    # Set up parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("export_type", help="Either one of 'clickstream' or 'tables'", type=str, choices=["clickstream", "tables"])
    parser.add_argument("course_slugs", help="EITHER: A course slug name, OR: Location of a text file (.txt) containing multiple course slug names. Each slug should be placed on a new line.", type=str)
    parser.add_argument("-c", "--copy_to_gcloud", help="Copy the downloaded files to a mounted gcloud bucket. Use the '--mount_location' argument to specify the mounted gcloud directory and '--bucket_name' to specify the bucket name", action="store_true")
    parser.add_argument("-m", "--gcloud_mount_location", help="The directory where the gcloud directory is mounted.", type=str)
    parser.add_argument("-b", "--bucket_name", help="Name of the gcloud bucket.", type=str)
    args = parser.parse_args()

    # Check arguments that are supposed to go together
    if args.copy_to_gcloud:
        if args.gcloud_mount_location == None or args.bucket_name == None:
            raise RuntimeError("Please supply the gcloud mount directory and the bucket name.")

    # Check directories
    if args.gcloud_mount_location != None:
        if not os.path.exists(args.gcloud_mount_location):
            raise RuntimeError("gcloud bucket is not mounted at path {}. Directory does not exist.".format(args.gcloud_mount_location))

    # Check slugs. If slug is mispelled it will be caught downstream in the coursera class.
    if ".txt" in args.course_slugs:
        with open(args.course_slugs, 'r') as inFile:
            courseSlugs = [line.replace("\n", "") for line in inFile]
    else:
        # Check if a filepath
        if os.path.isfile(args.course_slugs):
            raise RuntimeError("You entered a file path but the destination file is not a .txt file.")
        # Else check if a mispelled filepath
        elif "/" in args.course_slugs:
            raise RuntimeError("You entered an invalid file path containing a destination file that is not a .txt file.")
        else:
            courseSlugs = args.course_slugs

    print courseSlugs
    '''
    Call download class
    '''

    '''
    Call store class
    '''
