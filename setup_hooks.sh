#!/bin/bash

# Install pre-commit if it's not installed
if ! command -v pre-commit &> /dev/null
then
    echo "pre-commit could not be found. Installing..."
    pip install pre-commit
fi

# Install the pre-commit hooks
pre-commit install
