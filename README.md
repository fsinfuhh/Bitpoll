# Bitpoll

Bitpoll is a software to conduct polls about Dates, Times or general Questions.

This is a new version of the Dudel from opatut (<https://github.com/opatut/dudel>) used on <https://bitpoll.de>, rewritten using the Django framework as a backend.

## Features
 * set if anonymous votes are casted or if the user must provide it's name
 * set if registration is required for voting
 * allow the creation of private event only accessible to thoses invited
 * Poll can be created for full day event or just a few hours. Custom classes can also be defined
 * URL can be set manually or randomly choosen

## Demo

https://bitpoll.de 

## GUI

### Poll Creation Panel

![image](https://user-images.githubusercontent.com/15912256/190876284-ac6dd2e0-04c6-4d44-a53d-7dd72263a109.png)
![image](https://user-images.githubusercontent.com/15912256/190876419-d129d3c2-cda0-4da6-8b7a-7a30bf5d83e9.png)
![image](https://user-images.githubusercontent.com/15912256/190876455-55d8dc36-a117-4c41-b4ce-5184f5db8bc5.png)

### Voting View

![image](https://user-images.githubusercontent.com/15912256/190876484-a5b3cb2c-db77-4c5f-b1f2-43b5106c4691.png)

### Poll Results

![image](https://user-images.githubusercontent.com/15912256/190876528-178ace35-a3b8-4a55-8bf6-5c5afe0662c9.png)

## Installation

You can deploy this tool on your server either by manually cloning the repo and setting it up or you can run a docker image.

### Using Docker

The docker image is built automatically from the current master branch.
You can use the following commands to set up the docker container:

Create a directory for static and config files:

```bash
mkdir -p run/{log,static,config}
```

Get the example settings file and adapt it according to your needs:

```bash
wget https://raw.githubusercontent.com/fsinfuhh/Bitpoll/master/bitpoll/settings_local.sample.py -O run/config/settings.py
```

It is important to change at least the database settings, secret key, and allowed hosts.

Start the docker container:

```bash
docker run -a stdout -a stderr --rm --name bitpoll -p 3008:3008 -p 3009:3009 --volume ./run/static:/opt/static --volume ./run/config:/opt/config ghcr.io/fsinfuhh/bitpoll
```

The container is reachable on port 3009.
If you use an external web server, you can use uwsgi traffic on port 3008 and serve the static
assets from `run/static` at `/static/`.

### Manual Install

Get the code:

```bash
git clone https://github.com/fsinfuhh/Bitpoll
```

Generate a Python virtualenv and install dependencies:

```bash
virtualenv -p $(which python3) .pyenv
source .pyenv/bin/activate
pip install -r requirements.txt
```

Copy `bitpoll/settings_local.sample.py` to `bitpoll/settings_local.py` and customize the local settings.

Initialise Database:

```bash
./manage.py migrate
```

Run Testserver:

```bash
./manage.py runserver
```

### Production

In production Senty is used for error reporting.
django-auth-ldap is used vor login via ldap
uwsgi to serve the app

Install Dependencies for Production:

```bash
sudo apt install g++ make python3-psycopg2 python3-ldap3 gettext gcc python3-dev libldap2-dev libsasl2-dev
```

Install Python Dependencies

```bash
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
