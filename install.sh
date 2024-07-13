#!/bin/bash

BASE_DIR=$(realpath "$(dirname $0)")

# Create virtual environment
python -m venv venv

# Activate virtual environment
source ${BASE_DIR}/venv/bin/activate

# Install dependencies
pip install -r ${BASE_DIR}/requirements.txt

