#sentry-cli releases -o sentry-internal new -p bitpoll $VERSION
# Dockerfile
FROM python:slim as common-base

#ENV DJANGO_SETTINGS_MODULE foo.settings
ENV UID=2008

RUN usermod -u $UID -g nogroup -d /opt/bitpoll www-data

RUN mkdir -p /opt/bitpoll

WORKDIR /opt/bitpoll

RUN apt update && apt install -y --no-install-recommends libldap-2.5-0 libsasl2-2 uwsgi uwsgi-plugin-python3 && rm -rf /var/lib/apt/lists/*

FROM common-base as base-builder

RUN pip install -U pip setuptools

FROM base-builder as dependencies

RUN apt-get update && apt-get -y --no-install-recommends install g++ wget python3-pip make gettext gcc python3-dev libldap2-dev gpg gpg-agent curl libsasl2-dev npm

COPY requirements-production.txt .

RUN pip install --no-warn-script-location --prefix=/install -U -r requirements-production.txt

FROM dependencies as collect-static


RUN npm install cssmin uglify-js -g

COPY manage.py .
COPY bitpoll bitpoll
COPY locale locale
COPY docker_files/config/settings.py bitpoll/settings_local.py

# Set Pythonpath tro the packages installed with pip bevore so they are aviable in this step
RUN export PYTHONPATH=/install/lib/python$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)/site-packages && \
    python3 /opt/bitpoll/manage.py collectstatic --noinput && \
    python3 manage.py compilemessages &&\
    rm bitpoll/settings_local.py

FROM common-base

#RUN apt-get -y --no-install-recommends install python3-psycopg2 python3-ldap3 gettext

COPY --from=dependencies /install /usr/local
COPY --from=collect-static /opt/bitpoll .

COPY docker_files/run /usr/local/bin
COPY docker_files/uwsgi-bitpoll.ini /etc/uwsgi/bitpoll.ini

RUN chown $UID -R _static
RUN chmod o+r -R .

RUN ln -sf /opt/config/settings.py /opt/bitpoll/bitpoll/settings_local.py
RUN ln -sf /opt/storage/media /opt/bitpoll/_media

ARG RELEASE_VERSION=2022.05.22
RUN echo $RELEASE_VERSION > /opt/bitpoll/.releaseversion

ENV LANG=C.UTF-8
EXPOSE 3008/tcp
EXPOSE 3009/tcp
VOLUME /opt/static
VOLUME /opt/config
VOLUME /opt/log

ENTRYPOINT /usr/local/bin/run
