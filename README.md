## Memcached - Lite: Performance comparison of various storage types

### Introduction.
The project deals with designing, developing, and implementing a robust Key-Value Store and deploying the same in Google Cloud Platform (GCP). A Memcached Client-Server based architecture has been chosen to start with the designing part. TCP-socket server which listens to a host and port is used to start the server and consecutively connect to the clients. Three different types of storage system (VM Boot Disk, GCS Bucket, Redis Memory Store) have been used to save the data instead of the traditional Memcached server which store the data in memory and data is wiped off once the server is either restarted or shut down. `get` and `set` instructions have been used to either get the data from the Memcached server, insert, or update a new value. Concurrent connection of multiple clients connecting to a single server and performing the instructions have been considered.

![System Architecture - Memcached Lite](./GCP-Memcached.png)

### Prerequisites.  
•	Install Google SDK in your local machine to access Google Cloud Platform.  
•	A Google Cloud account with active credits and projects are required.  
•	Clone this Repo  
•	Create a Redis Instance on Google Cloud (Included in the VirtualMachineCreation.sh bash script)  
•	Create a Bucket and Blob in Google Cloud Storage (Not included in the Bash script since I created it manually and did not get the equivalent CLI command)  
•	Mention respective bucket and blob details in the `configFile.py`  

### Initial Setup and Instructions.
Once the Google account has been configured with active credits and project, we need to first create Virtual Machine Instances for Client and Server. We also need to create Virtual Private Cloud (VPC) network to be used by the VM and set the necessary firewall rules. The command line code to create the above are given in the Bash Script. Once the VM’s have been created, we need to setup the Git, pip to install necessary python packages. All the necessary installation packages are mentioned in `requirements.txt`. Additionally, I have also used Redis Memory Store for faster and effective get and set operations. Script to create a Redis instance has also been included in the bash script. Ensure that the bucket and blob storage are created in Google Cloud Storage.  

### Files.
**1.	Server Side**  
•	`kvsserver.py` – Contains the main server code to handle incoming client calls and process the get and set operations.  
•	`configFile.py` – Contains the server configurations such as IP, port, encoding format, header size, bucket name, blob name, Redis IP address, port, authentication password.  
•	`generatekvsTesting.py` – Generates 100 records of Keys-Values in KeyValueStore.txt for performance testing.  
•	`KeyValueStore.txt` – Local file to store the key-value pair.  
**2.	Client Side**  
•	`kvsclient.py` – Contains the main client code to send the get and set message to the server.  
•	`configFile.py` – Contains the client configurations such as Server IP, port, encoding format, header size, file name.  
•	`generatekvsTesting.py` – Generates 100 records of Keys in Keys.txt and values in values.txt for performance testing.  
•	`Keys.txt` – Local file to store the keys to be used for performance testing and comparison.  
•	`Values.txt` – Local file to store the values to be used for performance testing and comparison.  
•	`Kvsmultipleclient.py` – Contain code to spawn multiple clients at the same time to test concurrency.  

### Execution Instructions.
Ensure all the requirements are installed using the `installRequirements.sh` bash script inside the Google Compute Engine VM.  
•	Execute `python3 kvsserver.py` on server side and select any one storage structure.  
•	Once the Server is started and we get the message  `Server started on host` execute `python3 kvsclient.py` on the client side.  
    a.	Test Client Calls One by One – Allows user to enter get and set information one by one as per their requirements and accordingly performs the get and set operation.  
        - `get Key` eg `get A` returns the value stored against key A.  
        - `set Key len(updatedValue) \\r\\n updatedValue \\r\\n` eg `set A 4 \\r\\n Test \\r\\n` will update the value of A to Test.  
    b.	Performance Testing – Allows user to test the performance of the key value store.  

The performance testing option further lets users choose if they want to test the performance of the GET operation or SET operation.  

To Execute Multiple clients in multiple spawned windows, execute `python3 kvsmultipleclient.py` on the client terminal and select option 3.  

This will spawn 50 clients and then Get or set operations can be performed on each of the clients and the memory store will be modified accordingly.  

The performance testing mode enables multithreading functionality to perform multiple get and set operations on the storage selected in the first instance.  

### Google’s Key-Value Store.
I have implemented two of the Google’s Key – Value Store features for performing the comparison with the native VM Disk file based Memcached.  
**1.	Google Cloud Storage Bucket**  
•	Created a bucket-based storage which consisted of the blob file of `json` type to store the keys and values.  
•	GCS bucket provides file-based storage system that can handle large amounts of data and can be used for long term storage.  
•	However, the performance is not optimized for a low latency Key-Value storage.  
•	Bucket is mostly used for data archival and long-term storage use cases.  
**2.	Redis Memory Store**  
•	Redis is an in-memory data store specifically designed for low latency key-value storage and high-speed access.  
•	The get and set operations are extremely fast and makes an excellent choice for a typical Key- Value Store.  
•	Redis can be scaled on Google cloud by increasing the required resources.  
•	I deployed the Redis instance on Google cloud and made corresponding get and Set operations.  
P.S: - Make sure `Allow full access to all Cloud APIs` option is checked on the VM instance from which the Redis instance is being called.  

### Performance Analysis
•	`Performance_Analysis.ipynb` contains a simple bar graph of the results obtained from the above performance testing.  
•	It is evident that **Redis Memory Store** performs as good as the local VM Boot Disk.  
•	**Google Cloud Storage Bucket** performs relatively slower than Redis and even throws out an error `Rate Limit Exceeded` when consecutive `set` opertaions are performed within a short period of time.

### Conclusion  
•	**Redis Memory Store** seems to be the ideal choice for a Key-Value based caching system since it can easily handle huge amount of data along with multiple consecutive read and write operations.  
•	**Google Cloud Storage Bucket** is a good choice if the functionality does not demand concecutive write operations and there needs to be a visibility of the data stored in and transferred through any third party integrations.  