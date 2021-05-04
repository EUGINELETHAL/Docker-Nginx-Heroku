# Deploying Django to Heroku With Docker

Uses the Build Manifest approach for Heroku deployments.

## Want to learn how to build this?

Check out the [post](https://testdriven.io/blog/deploying-django-to-heroku-with-docker/).

## Want to use this project?

### Development

Run locally:

```sh
$ docker build -t web:latest .
$ docker run -d --name django-heroku -e "PORT=8765" -e "DEBUG=1" -p 8007:8765 web:latest
```

Verify [http://localhost:8007/ping/](http://localhost:8007/ping/) works as expected:

```json
{
  "ping": "pong!"
}
```

Stop then remove the running container once done:

```sh
$ docker stop django-heroku
$ docker rm django-heroku
```

### Production

See the blog [post](https://testdriven.io/blog/deploying-django-to-heroku-with-docker/).
