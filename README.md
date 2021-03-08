# procd - Private Robust Contact Discovery

This project is an exemplary implementation for a privacy preserving contact discovery service.

An exemplary implementation for a corresponding client is included as well.

# Usage

## Server

1. Initialize a PostgreSQL database using the provided [db_init.sql](src/server/db_init.sql)
2. Configure [config.yaml](src/server/config.yaml) to your liking.
3. Run the server

```bash
cd src/server/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Your local PCD server is now running and can be accessed on port 5000.

## Client

For custom configuration adjust [config.yaml](src/client/config.yaml) to your liking.

```bash
cd src/client/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```
