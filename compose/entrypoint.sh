#!/bin/bash

function runTests() {
    FAILED_TEST=0
    cd /app
    printf "CHECKING TYPINGS...\n"
    mypy run.py
    if (( $? != 0 )); then (( FAILED_TEST+=1 )); else echo "All good!"; fi

    printf "\n\nCHECKING PEP8...\n"
    pep8 **/*.py
    if (( $? != 0 )); then (( FAILED_TEST+=1 )); else echo "All good!"; fi

    printf "\n\nRUNNING TEST SUITE...\n"
    pytest
    if (( $? != 0 )); then (( FAILED_TEST+=1 )); fi

    if (( $FAILED_TEST > 0 )); then return 1; else return 0; fi
}

if [ "$1" == "test" ]; then
    runTests
else
    gunicorn run:app -w 4 -b 0.0.0.0:8080 --chdir=/app
fi


