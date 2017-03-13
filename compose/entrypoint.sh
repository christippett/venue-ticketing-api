#!/bin/bash

function runTests() {
    FAILED_TEST=0
    cd /app
    echo "CHECKING TYPINGS..."
    mypy run.py
    if (( $? != 0 )); then (( FAILED_TEST+=1 )); fi

    echo "CHECKING PEP8..."
    pep8 **/*.py
    if (( $? != 0 )); then (( FAILED_TEST+=1 )); fi

    echo "RUNNING TEST SUITE..."
    pytest
    if (( $? != 0 )); then (( FAILED_TEST+=1 )); fi

    if (( $FAILED_TEST > 0 )); then return 1; else return 0; fi
}

if [ "$1" == "test" ]; then
    runTests
else
    /usr/local/bin/gunicorn run:app -w 4 -b 0.0.0.0:5000 --chdir=/app
fi


