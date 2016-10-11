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
# Call this script using crontab to clean exports (only keep the most recent ones)
# Jasper Ginn
# 07/10/2016
'''

import os
import argparse

'''
Exceptions
'''

class nopath(Exception):
    pass

class emptyfolders(Exception):
    pass

'''
clean
'''

class cleaner:

    def __init__(self, location, files_to_keep = 2):
        self.location = location
        self.files_to_keep = files_to_keep

        # Check if real location
        if not os.path.exists(location):
            raise nopath("The location you entered does not exist. Please enter a valid location.")

        # Check if 'tables' folder exists
        if not os.path.exists("{}/tables/".format(location)):
            raise nopath("'Tables' folder does not exist in this directory.")

        # If all folders empty
        folders = [d[0] for d in os.walk("{}/tables/".format(location))]
        del folders[0]
        folders_with_files = [f for f in folders if len(os.listdir(f)) >= files_to_keep]
        if len(folders_with_files) < 1:
            raise emptyfolders("All folders have less than {} files.".format(str(files_to_keep)))
        # Add to self
        self.folders = folders_with_files

    def scope(self):
        # For each folder, delete oldest
        for fold in self.folders:
            # List files and ignore system files
            f = [file_ for file_ in os.listdir(fold) if not file_.startswith('.')]
            # If length f > files_to_keep
            if len(f) >= self.files_to_keep:
                # Take out oldest files
                diff = (len(f) - self.files_to_keep)
                #print diff
                for d in range(0,diff):
                    os.remove("{}/{}".format(fold, f[d]))

if __name__=="__main__":

    # Set up parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("location", help="Base directory in which to look for the data. The program will automatically add the course slug to the folder and download the data there.", type = str)
    parser.add_argument("--files_to_keep", help="How many files should the program keep? Defaults to 2", type=int)
    args = parser.parse_args()

    # Run
    clean = cleaner(args.location)
    clean.scope()
