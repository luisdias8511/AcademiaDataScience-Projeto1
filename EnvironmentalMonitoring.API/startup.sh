#!/bin/bash
curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl -sSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
cd /home/site/wwwroot
if [ -f antenv/bin/activate ]; then source antenv/bin/activate; fi
python -m gunicorn --bind=0.0.0.0:8000 --workers=2 --worker-class=uvicorn_worker.UvicornWorker src.main:app