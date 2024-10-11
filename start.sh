#!/usr/bin/bash
source env/bin/activate
gunicorn -b 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker --timeout 0 main:app