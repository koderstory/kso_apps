#!/bin/bash
printf "\n==================\n SETUP\n==================\n"
read -p "1. Using subdomain www? (y/N) " WWW
read -p "2. Enter Domain?  (urdomain.com) " DOMAIN
while [ -z $DOMAIN ]; do
    printf "\nDOMAIN CAN'T BE BLANK ❌\n"
    read -p "2. Enter Domain?  (urdomain.com) " DOMAIN
done

read -p "3. Production Setting? (y/N) " DEBUG
read -p "4. Use local storage?  (y/N) " LOCAL_STORAGE
if [ "$LOCAL_STORAGE" = "N" ]; then
    printf "\nS3 Setup:\n"    
    read -p "4-1. S3 storage access key ID?" S3_ID
    read -p "4-2. S3 storage secret access key?" S3_SECRET
    read -p "4-3. S3 storage bucket name?" S3_BUCKET
    read -p "4-4. S3 storage region?" S3_REGION
    read -p "4-5. S3 storage endpoint?" S3_ENDPOINT

    sed -i 's/MYS3/True/g' example.env
    sed -i "s~S3_ID~$S3_ID~g" example.env
    sed -i "s~S3_SECRET~$S3_SECRET~g" example.env
    sed -i "s~S3_BUCKET~$S3_BUCKET~g" example.env
    sed -i "s~S3_REGION~$S3_REGION~g" example.env
    sed -i "s~S3_ENDPOINT~$S3_ENDPOINT~g" example.env
else
    sed -i 's/MYS3/False/g' example.env


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
    DEBUG="Development"
    sed -i 's/MYDEBUG/True/g' example.env
else
    DEBUG="Production"
    sed -i 's/MYDEBUG/False/g' example.env
    
fi
sed -i "s/MYDOMAIN/$DOMAIN/g" .gunicorn.sh
sed -i "s~MYDIR~$DIR~g" .gunicorn.sh
sed -i "s/MYUSER/$USER/g" .gunicorn.sh
sed -i "s~MYBIND~$BIND~g" .gunicorn.sh
sed -i "s/MYDEBUG/$DEBUG/g" .gunicorn.sh

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
printf "\n\n✨ ✨ Installation is finished! ✨ ✨\n"
rm ../dt

