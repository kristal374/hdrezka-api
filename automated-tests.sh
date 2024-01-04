#!/bin/bash

source ./venv/Scripts/activate

if ! python -m tests; then
  echo "unit tests failed"
  exit 1
fi

if ! pylint HDrezka --fail-under=9; then
  echo "pylint failed"
  exit 1
fi
