# backend-audit

This repository contains the code for the serivce to handle everything related to LPA Audits.

# Getting Started
This chapter describes how you can get started developping. 

## Structure
The backend-audit service is implemented in FastAPI. The code can be found under `/app`. That directory also contains the Dockerfile to build a docker image of the service. For convenience, you can also you docker-compose, but the docker-compose file is located in the root of the repository. The base Docker image used, is a Python 3.10 Debian image.

The root directory of repository contains the docker-compose.yml file, which can be used to start the service in a docker container.

## Cloning the repository

1. Clone the Repository
```
git clone https://github.com/Projekt-DataScience/backend-audit.git
```

2. Change your wokring directory into the cloned repository
```
cd backend-audit
```

## Starting the docker container
The service can be started inside a docker container. You can use docker-compose for this. The repository contains a docker-compose file in the root of the repository. You can start the container with the following command:
```
docker-compose up
```

After the container is booted up, your version of backend-audit will run on port 8000. You can access the API on http://localhost:8000

