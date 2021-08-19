#!/bin/bash --login
set -euo pipefail
conda activate aviation
exec python manage.py runserver