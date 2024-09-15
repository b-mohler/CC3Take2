#!/bin/bash

# Install dependencies
pip install -r requirements.txt
pip install pytest boto3

# Run tests
pytest --maxfail=1 --disable-warnings -q

# Capture the exit code of tests
EXIT_CODE=$?

# Exit with the appropriate status code
exit $EXIT_CODE

chmod +x test_script.sh
