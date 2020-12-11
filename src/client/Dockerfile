FROM python:3.8 as base
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1
RUN pip3 install pipenv --upgrade
WORKDIR /app
COPY lib/ /app/lib/
COPY config.yaml main.py Pipfile Pipfile.lock /app/
RUN pipenv install
ENTRYPOINT pipenv run python3 main.py
