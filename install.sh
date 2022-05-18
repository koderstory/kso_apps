#!/bin/bash

# read data
read -p "1. Using subdomain www? (Y/n) " WWW
read -p "2. Enter Domain?  (urdomain.com) " DOMAIN

# set variables
DIR=$(pwd)
BIND="unix:"$DIR"/.server/.gunicorn.sock"
GUNICORN=$DIR"/.server/.gunicorn.sh"
GUNICORN_ACCESS=$DIR"/logs/gunicorn-access.log"
GUNICORN_ERROR=$DIR"/logs/gunicorn-errors.log"
NGINX_ACCESS=$DIR"/logs/nginx-access.log"
NGINX_ERROR=$DIR"/logs/nginx-errors.log"

cd $DIR

sed -i "s/MYDOMAIN/$DOMAIN/g" .server/gunicorn.sh
sed -i "s~MYDIR~$DIR~g" .server/gunicorn.sh
sed -i "s/MYUSER/$USER/g" .server/gunicorn.sh
sed -i "s~MYBIND~$BIND~g" .server/gunicorn.sh
sed -i "s/MYDEBUG/$DEBUG/g" .server/gunicorn.sh

sed -i "s/MYDOMAIN/$DOMAIN/g" .server/supervisor.conf
sed -i "s~MYGUNICORN~$GUNICORN~g" .server/supervisor.conf
sed -i "s~MYDIR~$DIR~g" .server/supervisor.conf
sed -i "s/MYUSER/$USER/g" .server/supervisor.conf
sed -i "s~MYLOG_ACCESS~$GUNICORN_ACCESS~g" .server/supervisor.conf
sed -i "s~MYLOG_ERROR~$GUNICORN_ERROR~g" .server/supervisor.conf

sed -i "s/MYDOMAIN/$DOMAIN/g" .server/nginx.conf
sed -i "s~MYLOG_ACCESS~$NGINX_ACCESS~g" .server/nginx.conf
sed -i "s~MYLOG_ERROR~$NGINX_ERROR~g" .server/nginx.conf
sed -i "s~MYBIND~$BIND~g" .server/nginx.conf


if [[ -z "$WWW" || "$WWW" = "Y"  ]]; then
    sed -i "s/WWWDOMAIN/www.$DOMAIN/g" .server/nginx.conf
else
    sed -i 's/WWWDOMAIN/ /g' .server/nginx.conf
fi

chmod u+x .server/gunicorn.sh
mv .server/nginx.conf $DOMAIN"_nginx.conf"
mv .server/supervisor.conf $DOMAIN".conf"
mv example.env .env

sudo mv -i $DOMAIN /etc/nginx/sites-available/
sudo mv -i $DOMAIN".conf" /etc/supervisor/conf.d/
sudo ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo supervisorctl reread
sudo supervisorctl update
sudo systemctl reload nginx




