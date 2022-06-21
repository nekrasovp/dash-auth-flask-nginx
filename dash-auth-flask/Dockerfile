FROM python:3.9.13
LABEL maintainer="Nekrasov Pavel <nekrasovp@gmail.com>"

# Run application as 'app' user from 'app group.
# A system user is acceptable and we do not need a home.
RUN adduser --system --group --no-create-home app
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
