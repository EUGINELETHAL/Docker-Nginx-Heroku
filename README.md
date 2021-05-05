
This is search app built with django, postgres


   Project workflow;
   
    - Dockerize a Django app
    - Deploy and run a Django app in a Docker container on Heroku
    - Configure GitLab CI to deploy Docker images to Heroku
    - Manage static assets with WhiteNoise
    - Configure Postgres to run on Heroku
    - Create a production Dockerfile that uses multistage Docker builds
    - Use the Heroku Container Registry and Build Manifest for deploying Docker to Heroku
    <ul>
<li>First item</li>
<li>Second item</li>
<li>Third item</li>
<li>Fourth item</li>
</ul> 
    
```sh
# pull official base image
FROM python:3.8-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# add and run as non-root user
RUN adduser -D myuser
USER myuser

# run gunicorn
CMD gunicorn hello_django.wsgi:application --bind 0.0.0.0:$PORT
```





# 

Uses the Build Manifest approach for Heroku deployments.

## Want to learn how to build this?


# Deployment  Process
## Deploying Django to Heroku With Docker

### Development

Run locally:

```sh
$ docker build -t web:latest .
$ docker run -d --name django-heroku -e "PORT=8765" -e "DEBUG=1" -p 8007:8765 web:latest
```

Verify [http://localhost:8007/ping/](http://localhost:8007/) works as expected:

`

Stop then remove the running container once done:

```sh
$ docker stop django-heroku
$ docker rm django-heroku
```

### Production


