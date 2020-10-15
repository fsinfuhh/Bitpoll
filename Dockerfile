FROM python:3.7-stretch

WORKDIR app

RUN apt-get update && \
    apt-get install -y g++ make python3-psycopg2 python3-ldap3 gettext gcc python3-dev libldap2-dev libsasl2-dev

ADD requirements-production.txt .

RUN pip install -r requirements-production.txt

ADD . .
ADD bitpoll/settings_local.docker.py bitpoll/settings_local.py

RUN mkdir _data

CMD ./entrypoint.sh