# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY src/ .

COPY trained_models .

# Precompile python code for performance
RUN python3 -m compileall .

ENV TZBACKEND_URL=http://localhost:8989/api

ENV ML_MODELS_DIR=/app/trained_models

EXPOSE 5000

# command to run on container start
CMD [ "python3", "./run.py" ]
