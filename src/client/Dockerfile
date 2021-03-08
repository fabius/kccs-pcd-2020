FROM python:3.9
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY lib/ /app/lib/
COPY config.yaml main.py requirements.txt /app/
RUN pip install -r requirements.txt
ENTRYPOINT python3 main.py
