FROM python:3.9-slim-buster

RUN mkdir /open-genes-backend
COPY . /open-genes-backend
WORKDIR /open-genes-backend

ENV PYTHONPATH "${PYTHONPATH}:/open-genes-backend"

RUN pip install -r requirements.txt
