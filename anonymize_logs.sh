#!/bin/bash
source venv/bin/activate
python -c "from app import logging; logging.anonymize_logs_older_than(30)"
