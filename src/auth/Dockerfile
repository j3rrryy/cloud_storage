FROM python:3.12-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /src/auth
COPY requirements.txt .

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

COPY . .
