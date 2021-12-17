FROM docker.io/library/python:3.9.7

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY controller.py .
COPY src .

ENV LOGGING_LEVEL=INFO

CMD ["kopf", "run", "controller.py"]
