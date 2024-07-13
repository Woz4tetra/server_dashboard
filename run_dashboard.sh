#!/bin/bash

BASE_DIR=$(realpath "$(dirname $0)")

# Activate virtual environment
source ${BASE_DIR}/venv/bin/activate

# Run the application
cd ${BASE_DIR}
python -m streamlit run run_dashboard.py
