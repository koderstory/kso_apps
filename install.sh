#!/bin/bash

# Generate passowrds
DBPASS=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c12`
SFTPPASS=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c12`

# Input domain name
echo -n "Enter your domain name:"
read DOMAIN

# Creating the working directory
HOMEDIR="$(pwd)/websites/$DOMAIN"
mkdir -p "$HOMEDIR/.venv"
cd $HOMEDIR

# INSTALL DJANGO 
sudo -H pip install -U pipenv

pipenv install django gunicorn
source "$HOMEDIR/.venv/bin/activate"
django-admin startproject config .


echo "======================================="
echo "Creating Systemd and Socket Config ..."
echo "======================================="
echo "\n"
echo "[Unit]
Description=gunicorn socket -> $DOMAIN

[Socket]
ListenStream=/run/gunicorn_$DOMAIN.sock

[Install]
WantedBy=sockets.target
"| sudo tee /etc/systemd/system/gunicorn_$DOMAIN.socket

echo "\n"
echo "[Unit]
Description=gunicorn $DOMAIN daemon
Requires=gunicorn_$DOMAIN.socket
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$HOMEDIR
ExecStart=$HOMEDIR/.venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn_$DOMAIN.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
" | sudo tee /etc/systemd/system/gunicorn_$DOMAIN.service

sudo systemctl start gunicorn_$DOMAIN.socket
sudo systemctl enable gunicorn_$DOMAIN.socket
curl --unix-socket /run/gunicorn_$DOMAIN.sock localhost


echo "\n\n\n"
echo "======================================="
echo "NGINX Config ..."
echo "======================================="

echo "\n"
echo "server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    error_log /var/log/nginx/.$DOMAIN_error.log;
    access_log /var/log/nginx/.$DOMAIN_access.log;
    rewrite_log on;
    server_tokens off;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection '1; mode=block';

    location /static/ {
        root $HOMEDIR;
            expires 30d;
        log_not_found off;
        access_log off;
    }
    location /media/ {
        root $HOMEDIR;
            expires 30d;
        log_not_found off;
        access_log off;
     }
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn_$DOMAIN.sock;
    }
}
" | sudo tee /etc/nginx/sites-available/$DOMAIN
sudo ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled
sudo systemctl restart nginx
