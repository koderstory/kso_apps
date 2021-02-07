#!/bin/bash
printf "\n==================\n SETUP\n==================\n"
read -p "Using subdomain www? (y/N) " WWW
read -p "Enter Domain?  (urdomain.com) " DOMAIN
read -p "Debug mode? (y/N) " DEBUG

printf "\nProcessing ...\n\n"
DIR=$(pwd)/$DOMAIN
BIND="unix:"$DIR"/.gunicorn.sock"
GUNICORN=$DIR"/.gunicorn.sh"
GUNICORN_ACCESS=$DIR"/logs/gunicorn-access"
GUNICORN_ERROR=$DIR"/logs/gunicorn-errors"
NGINX_ACCESS=$DIR"/logs/nginx-access"
NGINX_ERROR=$DIR"/logs/nginx-errors"

mkdir $DIR && cd $DIR
wget -c -q https://github.com/koderstory/djangotemplate/raw/main/djangotemplate.tar.gz && tar -xzf djangotemplate.tar.gz && rm djangotemplate.tar.gz

KEY=$(openssl rand -base64 30)
sed -i "s~MYKEY~$KEY~g" example.env
sed -i "s/MYDOMAIN/$DOMAIN/g" example.env
if [ "$DEBUG" = "N" ]; then
    DEBUG="Production"
    sed -i 's/MYDEBUG/False/g' example.env
else
    DEBUG="Development"
    sed -i 's/MYDEBUG/True/g' example.env
fi
sed -i "s/MYDOMAIN/$DOMAIN/g" .gunicorn.sh
sed -i "s~MYDIR~$DIR~g" .gunicorn.sh
sed -i "s/MYUSER/$USER/g" .gunicorn.sh
sed -i "s~MYBIND~$BIND~g" .gunicorn.sh

sed -i "s/MYDOMAIN/$DOMAIN/g" supervisor.conf
sed -i "s~MYGUNICORN~$GUNICORN~g" supervisor.conf
sed -i "s~MYDIR~$DIR~g" supervisor.conf
sed -i "s/MYUSER/$USER/g" supervisor.conf
sed -i "s~MYLOG_ACCESS~$GUNICORN_ACCESS~g" supervisor.conf
sed -i "s~MYLOG_ERROR~$GUNICORN_ERROR~g" supervisor.conf

sed -i "s/MYDOMAIN/$DOMAIN/g" nginx.conf
sed -i "s~MYLOG_ACCESS~$NGINX_ACCESS~g" nginx.conf
sed -i "s~MYLOG_ERROR~$NGINX_ERROR~g" nginx.conf
sed -i "s~MYBIND~$BIND~g" nginx.conf
if [ "$WWW" = "N" ]; then
    sed -i 's/WWWDOMAIN/ /g' nginx.conf
else
    sed -i "s/WWWDOMAIN/www.$DOMAIN/g" nginx.conf
fi

chmod u+x .gunicorn.sh
mv nginx.conf $DOMAIN
mv supervisor.conf $DOMAIN".conf"
mv example.env .env
sudo mv $DOMAIN /etc/nginx/sites-available/
sudo mv $DOMAIN".conf" /etc/supervisor/conf.d/
sudo ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

sudo supervisorctl reread
sudo supervisorctl update
sudo systemctl reload nginx

pipenv install --dev
rintf "\n\n\n\nInstallation is finished! \n"
rm $0

