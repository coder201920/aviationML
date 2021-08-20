#!/bin/bash --login
set -e
conda activate aviation
cd /app/
exec python manage.py runserver 0.0.0.0:8000