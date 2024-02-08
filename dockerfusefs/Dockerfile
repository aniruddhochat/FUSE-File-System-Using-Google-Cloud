FROM ubuntu:latest

# Create "local" and "mount" directories inside /tmp
RUN mkdir /tmp/local
RUN mkdir /tmp/mount

# Copy your FUSE file system code into the image
COPY FuseFS.py /tmp/
COPY configFile.py /tmp/
COPY aniruddho-chatterjee-fall2023-f967fa2ed4a5.json /tmp/
COPY fio_fuse_fs.fio /tmp/

# Install system-level dependencies
COPY sudoRequirements.txt /tmp/
RUN apt-get update && cat /tmp/sudoRequirements.txt | xargs -L 1 apt-get install -y

# Copy the Python dependencies list and install them
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Make the Python script executable
RUN chmod +x /tmp/FuseFS.py

# Set the working directory
WORKDIR /tmp/

# Specify the command to run your FUSE file system
CMD ["/tmp/FuseFS.py", "/tmp/local", "/tmp/mount"]

