# Bitpoll

Bitpoll is a software to conduct polls about Dates, Times or general Questions.


This is a new version of the Dudel from opatut (<https://github.com/opatut/dudel>) used on <mafiasi.de>, rewritten using the Django framework as a backend.


# Features
 * set if anonymous votes are casted or if the user must provide it's name
 * set if registration is required for voting
 * allow the creation of private event only accessible to thoses invited
 * Poll can be created for full day event or just a few hours. Custom classes can also be defined
 * URL can be set manually or randomly choosen

# GUI

Poll creation pannel
![image](https://user-images.githubusercontent.com/15912256/190876284-ac6dd2e0-04c6-4d44-a53d-7dd72263a109.png)
![image](https://user-images.githubusercontent.com/15912256/190876419-d129d3c2-cda0-4da6-8b7a-7a30bf5d83e9.png)
![image](https://user-images.githubusercontent.com/15912256/190876455-55d8dc36-a117-4c41-b4ce-5184f5db8bc5.png)
What the user see when choosing a combination
![image](https://user-images.githubusercontent.com/15912256/190876484-a5b3cb2c-db77-4c5f-b1f2-43b5106c4691.png)
and here are the result being displayed 
![image](https://user-images.githubusercontent.com/15912256/190876528-178ace35-a3b8-4a55-8bf6-5c5afe0662c9.png)

# Installation
you can deploy this tool on your server either by manually clonning the repo and setting it up or you can run a docker image.

## Using Docker

~~~
docker build --tag <imagename>
cd <workdir>
mkdir -p run/{log,static,config}
cp <original_dir>/bitpoll/settings_local.py run/config/settings.py
vim run/config/settings.py
docker run -a stdout -a stderr --rm --name bitpoll -p 3008:3008 -p 3009:3009 --volume `pwd`/run/static:/opt/static --volume `pwd`/run/config:/opt/config --volume `pwd`/run/log/:/opt/log <image_name>
~~~
The Static assets from <workdir>/run/static have to be served from the Webserver at /static/.
The Container listens for uwsgi traffic on Port 3008 and for HTTP traffic on Port 8009

TODO: add example nginx Config

## Manual Install

Get the code:

~~~
git clone https://github.com/fsinfuhh/Bitpoll
~~~

Generate a Python virtualenv and install dependencies:

```
virtualenv -p $(which python3) .pyenv
source .pyenv/bin/activate
pip install -r requirements.txt
```

Copy `bitpoll/settings_local.sample.py` to `bitpoll/settings_local.py` and customize the local settings.

Initialise Database:

```
./manage.py migrate
```

Run Testserver:

```
./manage.py runserver
```

## Production

In production Senty is used for error reporting.
django-auth-ldap is used vor login via ldap
uwsgi to serve the app

Install Dependencies for Production:

```bash
sudo apt install g++ make python3-psycopg2 python3-ldap3 gettext gcc python3-dev libldap2-dev libsasl2-dev
```

Install Python Dependencies

```
pip install -r requirements-production.txt
```

Configure examples are in `settings_local.py`

our used uwsgi config can be found at
<https://github.com/fsinfuhh/mafiasi-rkt/blob/master/bitpoll/uwsgi-bitpoll.ini>

For Production systems it is nessesarry to run

```bash
./manage.py compilemessages
./manage.py collectstatic
```

## Management of Dependencies

We use pip-tools to manage the dependencies.
After modification or the requirements*.in files or for updates of packages run

```bash
pip-compile --upgrade --output-file requirements.txt requirements.in
pip-compile --upgrade --output-file requirements-production.txt  requirements-production.in requirements.in
```

to sync your enviroment with the requirements.txt just run

```bash
pip-sync
```

this will install/deinstall dependencies so that the virtualenv is matching the requirements file
