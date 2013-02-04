paste.pm
========

Paste.pm is a minimalistic code sharing website written in Python.

Installation
============

To install paste.pm, you should create a virtualenv and install the requirements there.

    $ virtualenv pastepm --no-site-packages

Then, activate the virtualenv and install the requirements.

    $ cd pastepm && source bin/activate
    $ pip install -r requirements.txt

After that, you should populate config.ini with your details. You will need to create a database to use psate.pm. When you have config.ini in place, creating the database is as simple as:

    $ python create-db.py

Deployment
==========

You can deploy your paste.pm instance however you like; I personally use gunicorn with supervisord. Here is my supervisor config file:

    [program:paste]
    command=/home/service/webapps/paste/bin/gunicorn app:app -b 127.0.0.11:8000
    directory=/home/service/webapps/paste
    user=service
    autorestart=true

And nginx acts as a reverse proxy:

    server {
            listen 80;
            server_name paste.pm;

            location / {
                    proxy_pass http://127.0.0.11:8000/;
            }
    }
