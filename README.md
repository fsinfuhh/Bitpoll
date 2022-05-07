# Bitpoll

Bitpoll is a software to conduct polls about Dates, Times or general Questions.


This is a new version of the Dudel from opatut (<https://github.com/opatut/dudel>) used on <mafiasi.de>, rewritten using the Django framework as a backend.

# Using Docker

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

# Manual Install

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

# Production

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

# Management of Dependencies

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
