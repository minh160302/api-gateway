#!/bin/bash

# Run the first instance on port 5000
FLASK_APP=service.py flask run --port=6000 &

# Run the second instance on port 5001
FLASK_APP=service.py flask run --port=6001 &
