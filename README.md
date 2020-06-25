# KCCS - Private Contact Discovery
This project is an exemplary implementation for a privacy preserving contact discovery service. 

An exemplary implementation for a corresponding client is included as well.



## Usage
The most convenient way of running both server and client is to use the provided docker images.


## Server

### Prerequisites
Export all required environment variables

| Variable | Description |
| -------: | :---------- |
| HASH_DB_HOST | IP address of your database containing the [hashes table](db_structure.sql) |
| HASH_DB_PORT | Port the database is exposed / accessible on |
| HASH_DB_NAME | The corresponding database name |
| HASH_DB_USERNAME | A valid database user for the previously described database |
| HASH_DB_PASSWORD | The corresponding user-password |

### Running the server image
```bash
docker pull fabiandeifuss/pcd-server:latest 
docker run --rm -it \
    -p 5000:5000 \
    -e HASH_DB_HOST \
    -e HASH_DB_PORT \
    -e HASH_DB_NAME \
    -e HASH_DB_USERNAME \
    -e HASH_DB_PASSWORD \
    fabiandeifuss/pcd-server:latest
```
If docker is not an option for you, make sure Python (>= 3.8) & Pipenv is installed on your system. 
```bash
cd src/server/
pipenv install
pipenv run python3 main.py
```
Your local PCD server is now running and can be accessed on port 5000.


## Client

### Prerequisites
Export all required environment variables

| Variable | Description |
| -------: | :---------- |
| PCD_IP | \<IP address\>:\<port\> the pcd server is exposed / accessible on. For local deployment you can use your docker network address - `ip a \| grep docker0 \| grep inet` should get you the correct IP address |
| MY_PHONE_NUMBER | Your phone number |
| CONTACTS_DB_HOST | IP address of your database containing the [contacts table](db_structure.sql) |
| CONTACTS_DB_PORT | Port the database is exposed / accessible on |
| CONTACTS_DB_NAME | The corresponding database name |
| CONTACTS_DB_USERNAME | A valid database user for the previously described database |
| CONTACTS_DB_PASSWORD | The corresponding user-password |

### Running the client image
```bash
docker pull fabiandeifuss/pcd-client:latest 
docker run --rm -it \
    -e PCD_IP \
    -e MY_PHONE_NUMBER \
    -e CONTACTS_DB_HOST \
    -e CONTACTS_DB_PORT \
    -e CONTACTS_DB_NAME \
    -e CONTACTS_DB_USERNAME \
    -e CONTACTS_DB_PASSWORD \
    fabiandeifuss/pcd-client:latest
```
If docker is not an option for you, make sure Python (>= 3.8) & Pipenv is installed on your system. 
```bash
cd src/client/
pipenv install
pipenv run python3 main.py
```



## Building the images

### Server image
```bash
docker build -t pcd-server:local -f Dockerfile.Server .
```

### Client image
```bash
docker build -t pcd-client:local -f Dockerfile.Client .
```



## TODO 
* how can 2 parties start interacting with each other?


