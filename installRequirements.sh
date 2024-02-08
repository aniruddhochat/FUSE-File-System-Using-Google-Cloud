#!/bin/bash

# Check if Python 3.9.10 or greater is installed
required_version="3.9.10"
current_version=$(python3 -c "import sys; print(sys.version.split()[0])")

if [ "$(printf '%s\n' "$required_version" "$current_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Python version $current_version is not compatible. Installing Python $required_version..."
    sudo apt-get install "python$required_version"
fi


# Update the package list
apt-get update

# Install pip
yes Y | apt-get install python3-pip
yes Y | apt install git
yes Y | apt install fio
yes Y | apt install fuse

#Install Docker in VM
sudo apt install docker
sudo apt install docker.io

#Check if user exists in docker group for Permissions
grep 'docker' /etc/group

#Add user to Docker group
sudo usermod -aG docker caswapan

#Change ownership from root to username
sudo chown your_username:docker /var/run/docker.sock
sudo chmod 777 /var/run/docker.sock

# Install requirements from requirements.txt
pip3 install -r requirements.txt -v