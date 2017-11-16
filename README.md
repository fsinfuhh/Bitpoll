# Bitpoll

Bitpoll is a software to conduct polls about Dates, Times or general Questions.


This is a new version of the Dudel from opatut (<https://github.com/opatut/dudel>) used on <mafiasi.de>, rewritten using the Django framework as a backend.

# Install

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

In production Senty is used for error reporting:

```
pip install raven
```

for usage with LDAP install django-auth-ldap and configure it (example in `settings_local.py`)
