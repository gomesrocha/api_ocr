# pull official base image
FROM python:3.11.2-slim-bookworm

# set working directory
WORKDIR /usr/src/app
RUN mkdir -p /usr/src/app/images
VOLUME /usr/src/app/images

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc tesseract-ocr python3-pip \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
COPY ./requirements-dev.txt .
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

# add app
COPY . .