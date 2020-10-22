FROM python:3.7-stretch

WORKDIR app

RUN apt-get update && \
    apt-get install -y g++ make python3-psycopg2 python3-ldap3 gettext gcc python3-dev libldap2-dev libsasl2-dev

ADD requirements-production.txt src/

RUN pip install -r ./src/requirements-production.txt

ADD . src/
ADD bitpoll/settings_local.docker.py src/bitpoll/settings_local.py

RUN mkdir _data

EXPOSE 8000
VOLUME ["/app/_data"]

WORKDIR src
CMD ./entrypoint.sh