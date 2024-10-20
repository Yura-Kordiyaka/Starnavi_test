FROM python:3.12

WORKDIR /test_app

RUN apt update && apt -qy upgrade

COPY ../../requirements.txt test_app/requirements.txt

RUN pip install -r test_app/requirements.txt

COPY ../.. /test_app/

WORKDIR /test_app/