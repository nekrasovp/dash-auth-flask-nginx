# Run application as 'app' user from 'app group.
# A system user is acceptable and we do not need a home.

# For python:3.9.13
# FROM python:3.9.13
# LABEL maintainer="Nekrasov Pavel <nekrasovp@gmail.com>"
# RUN adduser --system --group --no-create-home app  

# For python:3.9.13-alpine
FROM python:3.9.13-alpine
LABEL maintainer="Nekrasov Pavel <nekrasovp@gmail.com>"
RUN addgroup app
RUN adduser -S -G app -H app
# For asteroid using Alpine. Can comment out for non alpine
RUN apk add --no-cache --update python3-dev gcc build-base

RUN /usr/local/bin/python -m pip install --upgrade pip

# Place the application in a /app dir
COPY . /app

# Make the directory the working directory for subsequent commands
WORKDIR /app

# Install from the requirements.txt
RUN pip install -r requirements.txt

# Кestrict rights to the 'app' user
RUN chown -R app:app /app

# In this Dockerfile and in a docker-compose.yml, run as user 'app'
USER app

# As this image is used for different
# purposes and processes no CMD or ENTRYPOINT is specified here,
# this is done in docker-compose.yml.
