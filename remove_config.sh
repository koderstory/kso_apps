#!/bin/bash

sudo systemctl stop gunicorn_$1
sudo systemctl disable gunicorn_$1
sudo rm /etc/systemd/system/gunicorn_$1.service
sudo rm /etc/systemd/system/gunicorn_$1.socket
sudo systemctl daemon-reload

sudo rm /etc/nginx/sites-available/$1
sudo rm /etc/nginx/sites-enabled/$1
