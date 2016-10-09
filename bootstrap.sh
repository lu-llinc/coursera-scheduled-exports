# Run to install dependencies on Linux.
# I use this for a clean VM or VPS.

sudo apt-get update
sudo apt-get upgrade
# Install anaconda
wget https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh
sudo ./Anaconda2-4.2.0-Linux-x86_64.sh -b -p /opt/anaconda
source ~/.bashrc

# Install python packages
sudo pip install -r requirements.txt
