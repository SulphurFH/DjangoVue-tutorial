#!/bin/bash

#--------------- script to run testcase ---------------#

set -e
cd $(dirname "$0")
cd ../..

pip install virtualenv
VENV_DIR="/cache/runtests-venv/tutorial"
if [ ! -d "$VENV_DIR" ]; then
  virtualenv $VENV_DIR
fi
. $VENV_DIR/bin/activate
pip install -r requirements.txt
pip install -r test_requirements.txt

coverage run --rcfile=.coveragerc manage.py test --settings=tutorial.test_settings tests
coverage report -m
