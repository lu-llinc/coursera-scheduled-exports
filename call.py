#! /usr/bin/env python

'''
# Call scheduler.py and store.py to download files and store them in a google cloud bucket
# Jasper Ginn
# 07/10/2016
'''

import argparse
from scheduler import coursera
from store import gcloud

if __name__=="__main__":
    
    # Set up parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help="Either one of 'clickstream' or 'tables'", type=str, choices=["clickstream", "tables"])
    parser.add_argument("course_slugs", help="Location of a file containing course slug names. Each slug should be placed on a new line.", type=str)
    parser.add_argument("-c", "--copy_to_gcloud", help="Copy the downloaded files to a mounted gcloud bucket. Use the '--mount_location' argument to specify the mounted gcloud directory and '--bucket_name' to specify the bucket name", action="store_true", type=str)
    parser.add_argument("-m", "--gcloud_mount_location", help="The directory where the gcloud directory is mounted.", type=str)
    parser.add_argument("-b", "--bucket_name", help="Name of the gcloud bucket.", type=str)
    args = parser.parse_args()
    
    # Check arguments that are supposed to go together
    req = c["copy_to_gcloud", "gcloud_mount_location", "bucket_name"]
    if not all([getattr(args, x) for x in req]):
        raise RuntimeError("Please supply the gcloud bucket mount location on your local system and the bucket name for the bucket.")
    
    # Check directories
    if not os.path.exists(args.gcloud_mount_location):
        raise RuntimeError("gcloud bucket is not mounted at path {}".format(args.gcloud_mount_location))
    
    '''
    Call download class
    '''
    
    '''
    Call store class
    '''