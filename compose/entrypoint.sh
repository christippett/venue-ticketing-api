#!/bin/bash

function runTests() {
    cd /app
    echo "CHECKING TYPINGS..."
    mypy app.py
    echo "CHECKING PEP8..."
    pep8 **/*.py
    echo "RUNNING TEST SUITE..."
    pytest
}

if [ "$1" == "test" ]; then
    runTests
    exit 0
else
    openssl req -x509 -newkey rsa:2048 -sha256 -keyout /cert/key.pem -out /cert/cert.crt -days 365 -nodes -subj "/C=AU/ST=Victoria/L=Melbourne/O=Ticket Bounty/OU=Venue API/CN=$1"
    /usr/local/bin/gunicorn wsgi:app -w 4 -b 0.0.0.0:5000 --certfile=/cert/cert.crt --keyfile=/cert/key.pem --ssl-version 2 --ciphers TLSv1.2 --chdir=/app
fi


