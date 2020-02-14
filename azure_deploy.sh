#!/bin/bash
#cp -r ./drop .
#python -m venv antenv
#source ./antenv/bin/activate
#apt-get -y install python-dev
#apt-get -y install default-libmysqlclient-dev
#apt-get -y install build-essential
#pip install -r ./requirements.txt


echo "Running as `whoami`"
echo "Running from `pwd`"
@echo off
if NOT exist requirements.txt (
 echo No Requirements.txt found.
 EXIT /b 0
)
if NOT exist "$(PYTHON_EXT)/python.exe" (
 echo Python extension not available >&2
 EXIT /b 1
)
echo Installing dependencies
call "$(PYTHON_EXT)/python.exe" -m pip install -U setuptools
if %errorlevel% NEQ 0 (
 echo Failed to install setuptools >&2
 EXIT /b 1
)
call "$(PYTHON_EXT)/python.exe" -m pip install -r requirements.txt
if %errorlevel% NEQ 0 (
 echo Failed to install dependencies>&2
 EXIT /b 1
)