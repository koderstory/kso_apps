REFERENCE:
https://hiteshmishra708.medium.com/deploy-django-app-with-nginx-and-gunicorn-37916ede7db

# Installation libraries

```
sudo apt install build-essential zlib1g-dev libbz2-dev \
libssl-dev libsqlite3-dev  libpq-dev libreadline-dev \
libncurses5-dev libncursesw5-dev libffi-dev liblzma-dev \
wget curl llvm xz-utils tk-dev git \
python3-dev python3-venv python3-pip pipenv \
postgresql postgresql-contrib nginx -y

```

# Install pip libraries
```
pip install wheel
pip install --upgrade pip
```

# set directory /srv

```
sudo chown -R $USER:$USER /srv
mkdir /srv/your_domain.com/
cd /srv/your_domain.com/
cd .venv
pipenv install django
```

# Create socket file and socket

Create systemd socket file.
`sudo nano /etc/systemd/system/your_domain.com.socket`

```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/your_domain.com.sock

[Install]
WantedBy=sockets.target
```

# Create service

`sudo nano /etc/systemd/system/your_domain.com.service`

```
[Unit]
Description=gunicorn daemon
Requires=your_domain.com.socket
After=network.target

[Service]
User=dev
Group=www-data
WorkingDirectory=/srv/your_domain.com/src
ExecStart=/srv/your_domain.com/.venv/bin/gunicorn \
--access-logfile - \
--workers 3 \
--bind unix:/run/your_domain.com.sock \
--chdir /srv/your_domain.com/src \
config.wsgi:application

[Install]
WantedBy=multi-user.target
```

# Turn on socket connection

```
curl --unix-socket /run/your_domain.com.sock localhost
sudo systemctl reload-daemon
sudo systemctl restart your_domain.com
```

# Set nginx

`sudo nano /etc/nginx/sites-available/your_domain.com`

```
server {
        listen 80;
        server_name your_domain.com www.your_domain.com;
        location = /favicon.ico {  access_log off; log_not_found off;}

        location /static {
                alias /srv/your_domain.com/public/static;
        }

        location /media {
                alias /srv/your_domain.com/public/media;
        }

        location / {
                include proxy_params;
                proxy_pass http://unix:/run/your_domain.com.sock;
        }
}
```
` sudo ln -s /etc/nginx/sites-available/your_domain.com /etc/nginx/sites-enabled/`

# set permissions
`sudo chmod -R 755 /srv/your_domain.com/public/`
