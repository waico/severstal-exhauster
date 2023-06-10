FROM python:3-slim

RUN pip install mlflow boto3 psycopg2-binary

ADD . /app
WORKDIR /app