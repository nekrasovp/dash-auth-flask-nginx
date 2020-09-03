## Synopsis

This project ties together Flask, Dash, Docker and Nginx for bootstraping 
CI\CD pipelines of Flask \ Dash \ Plot.ly Applications.

## What is Dash? 

Dash Web Applications combine the full power and best features of Plot.ly, Python, React.js and Flask.

https://dash.plot.ly/gallery

## Quickstart

Clone the repository, cd into it and run
```bash
docker-compose build
docker-compose up -d
```

### Preview

Point your browser to http://localhost:8000

## Docker containers

For each component of this project a separate docker container is afforded, 
controlled ("orchestrated") by docker-compose.

For the sake of simplicity, the same image is used for the separate containers. 
The image stems from python:3.8-stretch, which contains a debian linux. Instead of debian a
 more lightweight image like alpine could also be used.

The are two containers in this project at work.

dash-auth-flask: where are Dash\Flask web application runs
nginx: containing the nginx server
The image is build from dash-auth-flask/Dockerfile. This one Dockerfile includes all the necessary
python components and their dependencies from dash-auth-flask/requirements.txt. 
Because we're using the same image for multiple purposes like different flask applications it 
has to contain all of these components. 
In an advanced use case you want to build different images which are tailored to their 
individual purposes.

For the nginx server container is out-of-the-box nginx image which re-write conf files.

## docker-compose in development and production

To give an example of a development workflow with docker-compose two configuration files are used. 
A feature of docker-compose is to have multiple configuration files layered on top of each other 
where later files override settings from previous ones.

In this project the default __docker-compose.yml__ runs the application in a production like manner 
while the additional __docker-compose-development.yml__ runs the application in a way more suitable 
for development. "Production like" does actual mean that you can run it like this on the
internet, check nginx configuration files included.

To run the application in a production like manner:
```bash
docker-compose up -d
```
This will start the docker containers defined in docker-compose.yml. It is equivalent to running 
```bash
docker-compose -f docker-compose.yml up -d
```
To start the application in a development manner:
```bash
docker-compose -f docker-compose.yml -f docker-compose-development.yml up --build -d dash-auth-flask 
```
This will read the configuration from __docker-compose.yml__ and include the changes stated in 
__docker-compose-development.yml__ before running the containers. 
By this way we alter the configuration given in the first file by the configuration 
from the second.  
Suppress --build option in various development scenarios:
```bash
docker-compose -f docker-compose.yml -f docker-compose-development.yml up -d dash-auth-flask
```
To kill all running docker processes:
```bash
docker-compose rm -fs
```

## Networking

docker-compose automatically sets up local network for our service where the containers can talk 
to each other; usually in the 172.x.x.x range. It also ensures that containers can address each 
other by their names.