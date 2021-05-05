# Deploying Django to Heroku With Docker

Uses the Build Manifest approach for Heroku deployments.

## Want to learn how to build this?



## Want to use this project?

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


