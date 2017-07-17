# Bitpoll

Bitpoll is a software to conduct polls about Dates, Times or general Questions.


This is a new version of the Dudel from opatut (https://github.com/opatut/dudel) used on mafiasi.de, rewritten using the Django framework as a backend.

# Install

Install the System Dependencies:

```
    apt install coffeescript ruby-sass python3-dev
```

Generate a Python Virtualenviroment and install dependencies:

```
    virtualenv -p $(which python3) .pyenv
    source .pyenv/bin/activate
    pip install -r requirements.txt
    git submodule init
    git submodule update
```

Customize the local settings in settings_local.py

Initialise Database:

```
    ./manage.py migrate
```

Run Testserver:

```
    ./manage.py runserver
```

In production Senty is used for errorreporting:

```
   pip install raven
```

for usage with LDAP install django-auth-ldap and configure it (example in settings_locale.py)
