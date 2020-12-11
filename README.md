# KCCS - Private Contact Discovery

This project is an exemplary implementation for a privacy preserving contact discovery service.

An exemplary implementation for a corresponding client is included as well.

# Usage

Make sure pipenv & python >= 3.8 is available on your system.

## Server

For custom configuration adjust [config.yaml](src/server/config.yaml) to your liking.

```bash
cd src/server
pipenv install
pipenv run python3 main.py
```

Your local PCD server is now running and can be accessed on port 5000.

## Client

For custom configuration adjust [config.yaml](src/client/config.yaml) to your liking.

```bash
cd src/client/
pipenv install
pipenv run python3 main.py
```
