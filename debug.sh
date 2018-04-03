#!/bin/sh

FLASK_APP=iiifcollectionbrowse python -m flask run -h 0.0.0.0 -p 5000
trap command SIGINT
