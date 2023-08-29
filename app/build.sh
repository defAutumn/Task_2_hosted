#!/bin/bash

# Build the project
echo "Building the project..."
python3.9 -m pip install -r requirements.txt

export POSTGRES_HOST=containers-us-west-69.railway.app
export POSTGRES_PORT=7685
export POSTGRES_DB=railway
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=AX0zcgCW7QadcP23Zr9M
export DATABASE_URL=postgresql://postgres:AX0zcgCW7QadcP23Zr9M@containers-us-west-69.railway.app:7685/railway

echo "Make Migration..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

echo "Collect Static..."
python3.9 manage.py collectstatic --noinput --clear
#python3.9 docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
#python3.9 celery -A app worker -l info -P gevent
#python3.9 celery -A app flower