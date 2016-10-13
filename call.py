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
# Call this script using crontab to download & store coursera export data at scheduled times.
# Jasper Ginn
# 07/10/2016
'''

import os
import argparse
import logging
import datetime
from urlparse import urlparse
from scheduler import coursera, FailedRequest, ApiResolve

'''
Store metadata function
'''

def store_metadata_file(location, status, course, course_id, exportType, meta, schema_names, files_downloaded):
    meta = {"course":course, "course_id":course_id, "exportType":exportType, "meta":meta, "schema_names":schema_names, "status":status}
    time_now = str(datetime.datetime.now())
    with open("{}/metadata.txt".format(location), 'a') as inFile:
        inFile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(time_now.encode("utf8"), meta["status"].encode("utf8"), meta["course"].encode("utf8"),
                                                     meta["course_id"].encode("utf8"), meta["exportType"].encode("utf8"),
                                                     meta["meta"], meta["schema_names"], files_downloaded.encode("utf8")))

'''
Wrapper to download files.
'''

def coursera_download(course_slug, request_type, location, store_metadata = True):

    if not os.path.exists("{}{}".format(location, request_type)):
        os.makedirs("{}{}".format(location, request_type))
    # Check if course slug folder exists in data folder
    if not os.path.exists("{}{}/{}".format(location, request_type, course_slug)):
        os.makedirs("{}{}/{}".format(location, request_type, course_slug))
    # Init
    c = coursera(course_slug, args.verbose, args.log)
    # Fetch course id
    c.get_course_id()
    if args.verbose:
        print 'Successfully fetched course ID'
    # Check if a request for this course was made in the past 5 days (tables) or 1 day (clickstream)
    if request_type == "tables":
        threshold = 5 * 86400
    else:
        threshold = 1 * 86400
    check = c.catch_download(threshold = threshold, request_type = request_type)
    # If true, skip request
    if not check or args.force_request:
        # Depending on request type, call tables or clickstream
        if request_type == 'clickstream':
            c.create_cs_interval(ndays = args.clickstream_days, interval = args.interval)
            c.request_clickstream()
        else:
            c.request_schemas()
            if args.verbose:
                print 'Successful request'
    else:
        print "Found '{}' request for {} created in the past {} days. Resuming that download ... (if you'd like to override this, add '--force_request' to your command.)".format(request_type, course_slug, str(threshold / 86400))
    # Create cs interval
    c.create_cs_interval(ndays = args.clickstream_days, interval = args.interval)
    # Check if ready for download
    links = c.status_export(interval = 300)
    # Download data to destination folder
    files_downloaded = 0
    for link in links:
        # Check if file exists
        filename = urlparse(link).path.split('/')[-1]
        # Create location
        tloc = "{}{}/{}/".format(location, request_type, course_slug)
        if os.path.isfile("{}{}".format(tloc, filename)):
            if args.verbose:
                print "File {} already exists in target location. Moving on ... ".format(filename)
            if args.log:
                logging.info("File {} already exists in target location. Moving on ... ".format(filename))
            continue
        # If incomplete file, skip and notice
        if "_part_" in filename:
            if args.verbose:
                print "Download link leads to incomplete file. Skipping for now."
            if args.log:
                logging.error("File {} is incomplete. Skipping download of this file. Check if there are days missing in your download folder {}.".format(filename, tloc))
		continue
	try:
            c.download(link, tloc)
            files_downloaded += 1
	except:
	    if args.verbose:
                print "Download failed for {}".format("filename")
	    if args.log:
                logging.error("Download failed for {}".format("filename"))
    # Get metadata and store in file
    if store_metadata:
        meta = c.return_metadata()
        store_metadata_file(location, "SUCCESS", meta["course"], meta["course_id"], meta["exportType"],meta["meta"], meta["schema_names"], str(files_downloaded))

'''
Run file
'''

if __name__=="__main__":

    # Set up parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("export_type", help="Either one of 'clickstream' or 'tables'", type=str, choices=["clickstream", "tables"])
    parser.add_argument("course_slugs", help="EITHER: A course slug name or names separated by a comma, OR: Location of a text file (.txt) containing multiple course slug names. Each slug should be placed on a new line.", type=str)
    parser.add_argument("location", help="Base directory in which to store the data. The program will automatically add the course slug to the folder and download the data there.", type = str)
    parser.add_argument("--clickstream_days", help="Optional. When requesting clickstream data, it automatically requests data for the last 7 days. Using this argument, you can change this number to any number you wish.", type=int)
    parser.add_argument("--interval", nargs=2, metavar = ('FROM', 'TO'), help="Use if you want to download clickstream data for a specific date range. Overrides '--clickstream_days' argument. You should format the date range as YYYY-MM-DD.")
    parser.add_argument("--save_metadata", help="Add the course's metadata to a 'metadata.txt' file saved in the base directory? Defaults to 'True'. If file does not exist, it will be created.", action="store_true")
    parser.add_argument("--force_request", help="If you are requesting data for a course for which you have already requested data in the past 5 days (for tables) or 1 day (for clickstreams), the program will not create a new request. Instead, it will continue from the previous request. If you add this flag, the program will ignore this and create a new request.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Print verbose messages.", action="store_true")
    parser.add_argument("-l","--log", help="Store error log. Will be stored in the 'location' directory.", action="store_true")
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

    # Check if location ends with '/'. If it does not, add.
    if not args.location.endswith("/"):
        args.location = "{}/".format(args.location)

    # Check if arguments are logical
    if args.clickstream_days != None:
        if args.clickstream_days < 1:
            raise ValueError("You cannot request less than 1 day of clickstream data.")

    # Check if interval is used. If so, turn number of clickstream_days to None
    if args.interval != None:
        if args.clickstream_days != None:
            args.clickstream_days = None

    # Create logger here!
    if args.log:
        logging.basicConfig(filename = "{}{}".format(args.location, "scheduled_downloads.log"), filemode='a', format='%(asctime)s %(name)s %(levelname)s %(message)s',
                            level=logging.INFO)
        # Set requests logging so that it doesn't crowd out the log file
        logging.getLogger("requests").setLevel(logging.WARNING)

    # Call
    for courseSlug in courseSlugs:
        try:
            coursera_download(courseSlug, args.export_type, args.location, args.save_metadata)
        except FailedRequest as e:
            print "Failed to make a request for course {} and export_type {}. You may not have the correct permissions or you may be requesting too many exports for your course (limited to 1 per hour).".format(courseSlug, args.export_type)
            if args.save_metadata:
                store_metadata_file(args.location, "FAILED REQUEST", courseSlug, "NONE", "NONE", "NONE", "NONE", "0")
        except ApiResolve as e:
            print "Your request succeeded but the API failed. Returned error '{}'".format(e)
            if args.save_metadata:
                store_metadata_file(args.location, "FAILED API", courseSlug, "NONE", "NONE", "NONE", "NONE", "0")
