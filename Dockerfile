#sentry-cli releases -o sentry-internal new -p bitpoll $VERSION
# Dockerfile
FROM python:3.12-slim as common-base

#ENV DJANGO_SETTINGS_MODULE foo.settings
ENV UID=2008
ENV PATH="/opt/bitpoll/.venv/bin:$PATH"

RUN usermod -u $UID -g nogroup -d /opt/bitpoll www-data

RUN mkdir -p /opt/bitpoll

WORKDIR /opt/bitpoll

RUN URLLIB3_NO_OVERRIDE=1 apt update && apt install -y --no-install-recommends libldap2 libsasl2-2 libexpat1&& rm -rf /var/lib/apt/lists/*

FROM common-base as base-builder

RUN pip install -U pip setuptools

FROM base-builder as dependencies

RUN apt-get update && apt-get -y --no-install-recommends install g++ wget python3-pip make gettext gcc python3-dev libldap2-dev gpg gpg-agent curl libsasl2-dev npm && \
    pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md .

RUN uv sync --locked --no-dev --extra production --no-install-project

FROM dependencies as collect-static


RUN npm install cssmin uglify-js -g

COPY manage.py .
COPY bitpoll bitpoll
COPY locale locale
COPY docker_files/config/settings.py bitpoll/settings_local.py

# Dependencies are installed in /opt/bitpoll/.venv by uv in the previous stage.
RUN uv run --locked /opt/bitpoll/manage.py collectstatic --noinput && \
    uv run --locked manage.py compilemessages &&\
    rm bitpoll/settings_local.py

FROM common-base

#RUN apt-get -y --no-install-recommends install python3-psycopg2 python3-ldap3 gettext

COPY --from=dependencies /opt/bitpoll/.venv /opt/bitpoll/.venv
COPY --from=collect-static /opt/bitpoll .

COPY docker_files/run /usr/local/bin
COPY docker_files/uwsgi-bitpoll.ini /etc/uwsgi/bitpoll.ini

RUN chown $UID -R _static
RUN chmod o+r -R .

RUN ln -sf /opt/config/settings.py /opt/bitpoll/bitpoll/settings_local.py
RUN ln -sf /opt/storage/media /opt/bitpoll/_media

ARG RELEASE_VERSION=2026.05.20
RUN echo $RELEASE_VERSION > /opt/bitpoll/.releaseversion

ENV LANG=C.UTF-8
EXPOSE 3008/tcp
EXPOSE 3009/tcp
VOLUME /opt/static
VOLUME /opt/config
VOLUME /opt/log

ENTRYPOINT /usr/local/bin/run
