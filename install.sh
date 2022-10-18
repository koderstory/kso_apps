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
pipenv install django gunicorn
source "$HOMEDIR/.venv/bin/activate"
django-admin startproject config .

# NGINX
echo "Creating NGINX config file..."
echo "server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    error_log /var/log/nginx/$SITENAME.error.log;
    access_log /var/log/nginx/$SITENAME.access.log;
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
}" | sudo tee /etc/nginx/sites-available/$DOMAIN.conf
sudo ln -sf /etc/nginx/sites-available/$DOMAIN.conf /etc/nginx/sites-enabled/$DOMAIN.conf
sudo systemctl restart nginx


# SYSTEMD
echo "Creating Gunicorn config file..."
echo "[Unit]
Description=gunicorn $DOMAIN daemon
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=${HOMEDIR}
ExecStart=$HOMEDIR/.venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn_$DOMAIN.sock app.wsgi:application

[Install]
WantedBy=multi-user.target
" | sudo tee /etc/systemd/system/gunicorn_$DOMAIN.service

# exit from the virtual environment and restart Gunicorn
deactivate
systemctl start gunicorn_$DOMAIN
systemctl enable gunicorn_$DOMAIN



