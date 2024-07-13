#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source ${BASE_DIR}/venv/bin/activate

# Install dependencies
pip install -r ${BASE_DIR}/requirements.txt

