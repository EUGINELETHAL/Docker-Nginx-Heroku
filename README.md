
This is search app built with django, postgres

## Want to learn how to build this?

   Project workflow;
   
    - Dockerize a Django app
    - Deploy and run a Django app in a Docker container on Heroku
    - Configure GitLab CI to deploy Docker images to Heroku
    - Manage static assets with WhiteNoise
    - Configure Postgres to run on Heroku
    - Create a production Dockerfile that uses multistage Docker builds
    - Use the Heroku Container Registry and Build Manifest for deploying Docker to Heroku
    
    
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




# Deployment  Process
## Deploying Django to Heroku With Docker

### Development

Run locally:

```sh
$ docker build -t web:latest .
$ docker run -d --name django-heroku -e "PORT=8765" -e "DEBUG=1" -p 8007:8765 web:latest
```

Verify [http://localhost:8007/](http://localhost:8007/) works as expected:

This project uses the trigram similarity search approach which is supported by Postgres
consecutive characters. You can measure the similarity of two strings by counting
the number of trigrams that they share. This approach turns out to be very effective
for measuring the similarity of words in many languages.
In order to use trigrams in PostgreSQL, you will need to install the pg_trgm
extension first. Execute the following command from the shell to connect to your
database:
```sh
psql cities
```
Then, execute the following command to install the pg_trgm extension:
```
CREATE EXTENSION pg_trgm;
```

Let's edit your view and modify it to search for trigrams. 

```sh
class SearchResultsView(ListView):
    model = City
    template_name = 'search_results.html'
    
    def get_queryset(self): 
        query = self.request.GET.get('q')
        object_list1= City.objects.annotate(similarity=TrigramSimilarity('name', query),).filter(similarity__gt=0.1).order_by('-similarity')
        object_list2=City.objects.annotate(similarity=TrigramSimilarity('state', query),).filter(similarity__gt=0.1).order_by('-similarity')
        object_list= object_list1|object_list2   # merge querysets
        return object_list
```
        
Open http://127.0.0.1:8000/ in your browser and test different
searches for trigrams. The following example displays a hypothetical typo in the
django term which exists in my database, showing search results for yango :
 Search results for the term "yango"
Now you have a powerful search engine built into your project. You can find more
information about full-text search at https://docs.djangoproject.com/en/3.0/
ref/contrib/postgres/search/ .

`

Stop then remove the running container once done:

```sh
$ docker stop django-heroku
$ docker rm django-heroku
```

### Production


