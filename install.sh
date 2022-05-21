#!/bin/bash

# read data
printf "🔆🔆🔆  SETUP DJANGO PROJECT 🔆🔆🔆\n"
printf "===================================\n"
read -p "✅ 1. Using subdomain www? (Y/n) " WWW
read -p "✅ 2. Enter Domain?  (urdomain.com) " DOMAIN
while [ -z $DOMAIN ]; do
    printf "\n‼️ DOMAIN CAN'T BE BLANK ❌\n"
    read -p "✅ 2. Enter Domain?  (urdomain.com) " DOMAIN
done

# set variables
DIR=$(pwd)
BIND="unix:"$DIR"/.server/gunicorn.sock"
GUNICORN=$DIR"/.server/gunicorn.sh"
GUNICORN_ACCESS=$DIR"/.logs/gunicorn-access.log"
GUNICORN_ERROR=$DIR"/.logs/gunicorn-errors.log"
NGINX_ACCESS=$DIR"/.logs/nginx-access.log"
NGINX_ERROR=$DIR"/.logs/nginx-errors.log"

cd $DIR
rm -rf .venv 
mkdir .venv

pip3 install pipenv
pipenv install

[ -f .server/gunicorn.sh ] && sed -i "s/MYDOMAIN/$DOMAIN/g" .server/gunicorn.sh
[ -f .server/gunicorn.sh ] && sed -i "s~MYDIR~$DIR~g" .server/gunicorn.sh
[ -f .server/gunicorn.sh ] && sed -i "s/MYUSER/$USER/g" .server/gunicorn.sh
[ -f .server/gunicorn.sh ] && sed -i "s~MYBIND~$BIND~g" .server/gunicorn.sh
[ -f .server/gunicorn.sh ] && sed -i "s/MYDEBUG/$DEBUG/g" .server/gunicorn.sh

[ -f .server/supervisor.conf ] && sed -i "s/MYDOMAIN/$DOMAIN/g" .server/supervisor.conf
[ -f .server/supervisor.conf ] && sed -i "s~MYGUNICORN~$GUNICORN~g" .server/supervisor.conf
[ -f .server/supervisor.conf ] && sed -i "s~MYDIR~$DIR~g" .server/supervisor.conf
[ -f .server/supervisor.conf ] && sed -i "s/MYUSER/$USER/g" .server/supervisor.conf
[ -f .server/supervisor.conf ] && sed -i "s~MYLOG_ACCESS~$GUNICORN_ACCESS~g" .server/supervisor.conf
[ -f .server/supervisor.conf ] && sed -i "s~MYLOG_ERROR~$GUNICORN_ERROR~g" .server/supervisor.conf

[ -f .server/nginx.conf ] && sed -i "s/MYDOMAIN/$DOMAIN/g" .server/nginx.conf
[ -f .server/nginx.conf ] && sed -i "s~MYLOG_ACCESS~$NGINX_ACCESS~g" .server/nginx.conf
[ -f .server/nginx.conf ] && sed -i "s~MYLOG_ERROR~$NGINX_ERROR~g" .server/nginx.conf
[ -f .server/nginx.conf ] && sed -i "s~MYBIND~$BIND~g" .server/nginx.conf


if [[ -z "$WWW" || "$WWW" = "Y"  ]]; then
    [ -f .server/nginx.conf ] && sed -i "s/WWWDOMAIN/www.$DOMAIN/g" .server/nginx.conf
else
    [ -f .server/nginx.conf ] && sed -i 's/WWWDOMAIN/ /g' .server/nginx.conf
fi

chmod u+x .server/gunicorn.sh
cp .server/nginx.conf $DOMAIN"_nginx.conf"
cp .server/supervisor.conf $DOMAIN".conf"
cp example.env .env

sudo cp $DOMAIN"_nginx.conf" /etc/nginx/sites-available/
sudo cp $DOMAIN".conf" /etc/supervisor/conf.d/
sudo ln -sfn /etc/nginx/sites-available/$DOMAIN"_nginx.conf" /etc/nginx/sites-enabled/
sudo supervisorctl reread
sudo supervisorctl update
sudo systemctl reload nginx




