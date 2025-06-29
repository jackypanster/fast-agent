#!/bin/bash
#
# This script automates the process of setting up the environment and running the application.
# It ensures all dependencies are synced and then launches the main CLI.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Syncing Python dependencies using uv... ---"
uv pip sync requirements.txt

echo
echo "--- Starting K8s Copilot... ---"
echo

# Execute the main python script using uv run.
# The -m flag tells Python to run the module as a script, which correctly handles the package imports.
# The "$@" part allows passing any command-line arguments from this script to the python script.
uv run python -m src.main "$@"

echo
echo "--- K8s Copilot session ended. ---" 