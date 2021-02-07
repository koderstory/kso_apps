#!/bin/bash

read -p "Enter Domain? " DOMAIN
read -p "Sub Domain WWW? (y/N) " WWW
read -p "Deploy production? (y/N) " DEPLOYMENT


DIR=$(pwd)/$DOMAIN
if [ "$DEPLOYMENT" = "N" ]; then
    DEPLOYMENT="Development"
else
    DEPLOYMENT="Production"
fi

# download zip


# extract zip
# create directory
# install dependencies using pipenv
# setup supervisor
# setup nginx
