FROM docker.io/library/python:3.9

RUN mkdir -p /app/src
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY controller.py /app/controller.py
COPY src /app/src

ENV LOGGING_LEVEL=INFO

CMD ["kopf", "run", "-A", "--liveness=http://0.0.0.0:8080/healthz", "controller.py"]
