#!/bin/sh
/usr/local/bin/gunicorn wsgi:app -w 4 -b 0.0.0.0:5000 --chdir=/app