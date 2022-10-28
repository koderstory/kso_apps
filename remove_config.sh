#!/bin/bash

sudo rm -r /home/$USER/websites/$1
sudo systemctl stop gunicorn_$1.service
sudo systemctl disable gunicorn_$1.service

sudo systemctl stop gunicorn_$1.socket
sudo systemctl disable gunicorn_$1.socket

sudo rm /etc/systemd/system/gunicorn_$1.service
sudo rm /etc/systemd/system/gunicorn_$1.socket

sudo systemctl daemon-reload
sudo systemctl reset-failed

sudo rm /etc/nginx/sites-available/$1
sudo rm /etc/nginx/sites-enabled/$1
