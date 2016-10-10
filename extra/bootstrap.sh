#!/usr/bin/env bash

# Run to install dependencies on Linux.
# I use this for a clean VM or VPS.

# Set timezone
export TZ=Europe/Amsterdam

sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install bzip2 libpq-dev
# Install gsfuse
export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install gcsfuse
# Install anaconda
wget https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh
bash Anaconda2-4.2.0-Linux-x86_64.sh -b -p ~/anaconda

#PATH='${PATH}:/home/Jasper/anaconda/bin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games'
#source ~/.bashrc

# Install python packages
~/anaconda/bin/pip install -r requirements.txt
