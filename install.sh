#!/bin/bash

# Generate passowrds
DBPASS=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c12`
SFTPPASS=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c12`

# Input domain name
echo -n "Enter your domain name:"
read DOMAIN

# Creating the working directory
cd 
mkdir "$(pwd)/Websites/$DOMAIN"
HOMEDIR="$(pwd)/Websites/$DOMAIN"
cd $HOMEDIR

# INSTALL DJANGO 
mkdir .venv
pipenv install django gunicorn
source .venv/bin/activate
django-admin startproject config .





