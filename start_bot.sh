#!/usr/bin/env bash

PROJECT_DIR=$(pwd)
source "$PROJECT_DIR/venv/bin/activate"
pip install -r "$PROJECT_DIR/requirements.txt"

python "$PROJECT_DIR/src/main.py"
