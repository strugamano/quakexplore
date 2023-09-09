#!/bin/bash

echo "Checking requirements..."
echo "> Python version: $(python --version)"
echo "> PIP version: $(pip --version)"
echo "  > pyside6: $(pip show pyside6)"
echo "  > requests $(pip show requests)"
echo "> Qt6 version: $(qmake6 --version)"

echo "Setting up application..."
python earthquakes.py

echo "Goodbye!"
