#!/usr/bin/env bash

# This script will create the PyPi package for Wsgi-15Watt
# Upload it to PyPi with:
#     python3 -m twine upload --repository pypi dist/*

rm -rf pypiPackage
mkdir -p pypiPackage/src/Wsgi_15Watt
mkdir -p pypiPackage/tests

cp pyproject.toml pypiPackage/
cp README.md pypiPackage/
cp *.py pypiPackage/src/Wsgi_15Watt/

cd pypiPackage
python3 -m build

echo "Publish with: python3 -m twine upload --repository pypi dist/*"
