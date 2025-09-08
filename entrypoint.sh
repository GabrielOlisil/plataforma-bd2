#!/bin/sh

flask --app main db upgrade

exec gunicorn --bind 0.0.0.0:8080 -w 4 main:app