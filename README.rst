


Technical Overview
------------------

There are many ways to containerize a Python/Django app, no one of which could be considered "the best." That being said, I think the following approach provides a good balance of simplicity, configurability, and container size. The specific tools I use are: `Docker <https://www.docker.com/>`_ (of course), the `python:3.7-slim <https://hub.docker.com/_/python/>`_ Docker image (based on Debian Stretch), and `uWSGI <https://uwsgi-docs.readthedocs.io/>`_.

I

The Dockerfile
--------------
here's the production-ready ``Dockerfile`` (it should be added in your top level project directory, next to the ``manage.py`` script provided by your Django project):

.. code-block:: docker

    FROM python:3.7-slim

    # Create a group and user to run our app
    ARG APP_USER=appuser
    RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

    # Install packages needed to run your application (not build deps):
    #   mime-support -- for mime types when serving static files
    #   postgresql-client -- for running database commands
    # We need to recreate the /usr/share/man/man{1..8} directories first because
    # they were clobbered by a parent image.
    RUN set -ex \
        && RUN_DEPS=" \
        libpcre3 \
        mime-support \
        postgresql-client \
        " \
        && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
        && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
        && rm -rf /var/lib/apt/lists/*

    # Copy in your requirements file
    ADD requirements.txt /requirements.txt

    # OR, if you're using a directory for your requirements, copy everything (comment out the above and uncomment this if so):
    # ADD requirements /requirements

    # Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
    # Correct the path to your production requirements file, if needed.
    RUN set -ex \
        && BUILD_DEPS=" \
        build-essential \
        libpcre3-dev \
        libpq-dev \
        " \
        && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
        && pip install --no-cache-dir -r /requirements.txt \
        \
        && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
        && rm -rf /var/lib/apt/lists/*

    # Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
    RUN mkdir /code/
    WORKDIR /code/
    ADD . /code/

    # uWSGI will listen on this port
    EXPOSE 8000

    # Add any static environment variables needed by Django or your settings file here:
    ENV DJANGO_SETTINGS_MODULE=my_project.settings.deploy

    # Call collectstatic (customize the following line with the minimal environment variables needed for manage.py to run):
    RUN DATABASE_URL='' python manage.py collectstatic --noinput

    # Tell uWSGI where to find your wsgi file (change this):
    ENV UWSGI_WSGI_FILE=my_project/wsgi.py

    # Base uWSGI configuration (you shouldn't need to change these):
    ENV UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_HTTP_AUTO_CHUNKED=1 UWSGI_HTTP_KEEPALIVE=1 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy

    # Number of uWSGI workers and threads per worker (customize as needed):
    ENV UWSGI_WORKERS=2 UWSGI_THREADS=4

    # uWSGI static file serving configuration (customize or comment out if not needed):
    ENV UWSGI_STATIC_MAP="/static/=/code/static/" UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|ico|woff|ttf|otf|svg|scss|map|txt) 315360000"

    # Deny invalid hosts before they get to Django (uncomment and change to your hostname(s)):
    # ENV UWSGI_ROUTE_HOST="^(?!localhost:8000$) break:400"

    # Change to a non-root user
    USER ${APP_USER}:${APP_USER}

    # Uncomment after creating your docker-entrypoint.sh
    # ENTRYPOINT ["/code/docker-entrypoint.sh"]

    # Start uWSGI
    CMD ["uwsgi", "--show-config"]

We extend from the "slim" flavor of the official Docker image for Python 3.7, install a few dependencies for running our application (i.e., that we want to keep in the final version of the image), copy the folder containing our requirements files to the container, and then, in a single line, (a) install the build dependencies needed, (b) ``pip install`` the requirements themselves (edit this line to match the location of your requirements file, if needed), (c) remove the C compiler and any other OS packages no longer needed, and (d) remove the package lists since they're no longer needed. It's important to keep this all on one line so that Docker will cache the entire operation as a single layer.

Next, we copy our application code to the image, set some default environment variables, and run ``collectstatic``. Be sure to change the values for ``DJANGO_SETTINGS_MODULE`` and ``UWSGI_WSGI_FILE`` to the correct paths for your application (note that the former requires a Python package path, while the latter requires a file system path).

A few notes about other aspects of this Dockerfile:

 I've added ``UWSGI_LAZY_APPS=1`` and ``UWSGI_WSGI_ENV_BEHAVIOR=holy`` to the uWSGI configuration to provide a more stable uWSGI experience.
* The ``UWSGI_HTTP_AUTO_CHUNKED`` and ``UWSGI_HTTP_KEEPALIVE`` options to uWSGI are needed in the event the container will be hosted behind an Amazon Elastic Load Balancer (ELB), because Django doesn't set a valid ``Content-Length`` header by default, unless the ``ConditionalGetMiddleware`` is enabled. See `the note <http://uwsgi-docs.readthedocs.io/en/latest/HTTP.html#can-i-use-uwsgi-s-http-capabilities-in-production>`_ at the end of the uWSGI documentation on HTTP support for further detail.


Requirements and Settings Files
-------------------------------

Production-ready requirements and settings files are outside the scope of this post, but you'll need to include a few things in your requirements file(s), if they're not there already::

    Django>=2.2,<2.3
    uwsgi>=2.0,<2.1
    dj-database-url>=0.5,<0.6
    psycopg2>=2.8,<2.9

I didn't pin these to specific versions here to help future-proof this post somewhat, but you'll likely want to pin these (and other) requirements to specific versions so things don't suddenly start breaking in production. Of course, you don't have to use any of these packages, but you'll need to adjust the corresponding code elsewhere in this post if you don't.

My ``deploy.py`` settings file looks like this:

.. code-block:: python

    import os

    import dj_database_url

    from . import *  # noqa: F403

    # This is NOT a complete production settings file. For more, see:
    # See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

    DEBUG = False

    ALLOWED_HOSTS = ['localhost']

    DATABASES['default'] = dj_database_url.config(conn_max_age=600)  # noqa: F405

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # noqa: F405

    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

This bears repeating: This is **not** a production-ready settings file, and you should review `the checklist <https://docs.djangoproject.com/en/dev/howto/deployment/checklist/>`_ in the Django docs (and run ``python manage.py check --deploy --settings=my_project.settings.deploy``) to ensure you've properly secured your production settings file.


Building and Testing the Container
----------------------------------

Now that you have the essentials in place, you can build your Docker image locally as follows:

.. code-block:: bash

    docker build -t my-app .

This will go through all the commands in your Dockerfile, and if successful, store an image with your local Docker server that you could then run:

.. code-block:: bash

    docker run -e DATABASE_URL='' -t my-app

This command is merely a smoke test to make sure uWSGI runs, and won't connect to a database or any other external services.


Running Commands During Container Start-Up
------------------------------------------

As a final step, I recommend creating an ``ENTRYPOINT`` script to run commands as needed during container start-up. This will let us accomplish any number of things, such as making sure Postgres is available or running ``migrate`` during container start-up. Save the following to a file named ``docker-entrypoint.sh`` in the same directory as your ``Dockerfile``:

.. code-block:: bash

    #!/bin/sh
    set -e

    until psql $DATABASE_URL -c '\l'; do
        >&2 echo "Postgres is unavailable - sleeping"
        sleep 1
    done

    >&2 echo "Postgres is up - continuing"

    if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
        python manage.py migrate --noinput
    fi

    exec "$@"

Make sure this file is executable, i.e.:

.. code-block:: bash

    chmod a+x docker-entrypoint.sh

Next, uncomment the following line to your ``Dockerfile``, just above the ``CMD`` statement:

.. code-block:: docker

    ENTRYPOINT ["/code/docker-entrypoint.sh"]

This will (a) make sure a database is available (usually only needed when used with Docker Compose) and (b) run outstanding migrations, if any, if the ``DJANGO_MANAGEPY_MIGRATE`` is set to ``on`` in your environment. Even if you add this entrypoint script as-is, you could still choose to run ``migrate`` or ``collectstatic`` in separate steps in your deployment before releasing the new container. The only reason you might not want to do this is if your application is highly sensitive to container start-up time, or if you want to avoid any database calls as the container starts up (e.g., for local testing). If you do rely on these commands being run during container start-up, be sure to set the relevant variables in your container's environment.


Creating a Production-Like Environment Locally with Docker Compose
------------------------------------------------------------------

To run a complete copy of production services locally, you can use `Docker Compose <https://docs.docker.com/compose/>`_. The following ``docker-compose.yml`` will create a barebones, ephemeral, AWS-like container environment with Postgres for testing your production environment locally.

*This is intended for local testing of your production environment only, and will not save data from stateful services like Postgres upon container shutdown.*

.. code-block:: yaml

    version: "2"

    services:
      db:
        environment:
          POSTGRES_DB: app_db
          POSTGRES_USER: app_user
          POSTGRES_PASSWORD: changeme
        restart: always
        image: postgres:12
        expose:
          - "5432"
      app:
        environment:
          DATABASE_URL: postgres://app_user:changeme@db/app_db
          DJANGO_MANAGEPY_MIGRATE: "on"
        build:
          context: .
          dockerfile: ./Dockerfile
        links:
          - db:db
        ports:
          - "8000:8000"

Copy this into a file named ``docker-compose.yml`` in the same directory as your ``Dockerfile``, and then run:

.. code-block:: bash

    docker-compose up --build -d

This downloads (or builds) and starts the two containers listed above. You can view output from the containers by running:

.. code-block:: bash

    docker-compose logs

If all services launched successfully, you should now be able to access your application at http://localhost:8000/ in a web browser.

If you need to debug your application container, a handy way to launch an instance it and poke around is:

.. code-block:: bash

    docker-compose run app /bin/bash


Static Files
------------
Nginx

Next, let's add Nginx into the mix to act as a reverse proxy for Gunicorn to handle client requests as well as serve up static files.

Add the service to docker-compose.prod.yml:

nginx:
  build: ./nginx
  ports:
    - 1337:80
  depends_on:
    - web

Then, in the local project root, create the following files and folders:

    
```sh
└── nginx
    ├── Dockerfile
    └── nginx.conf
    
```
Dockerfile:

FROM nginx:1.19.0-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

nginx.conf:

upstream my_project {
    server app:8000;
}

server {

    listen 80;
    server_name localhost;

   
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;
    location / {
        proxy_pass http://my_project;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
    location /staticfiles/ {
        alias /code/staticfiles/;
    }

    
}
    Review Using NGINX and NGINX Plus as an Application Gateway with uWSGI and Django for more info on configuring Nginx to work with Django.



Summary
-------

