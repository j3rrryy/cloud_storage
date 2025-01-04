# Cloud Storage

<p align="center">
  <img src="https://github.com/j3rrryy/cloud_storage/actions/workflows/main.yml/badge.svg">
  <a href="https://www.python.org/downloads/release/python-3120/">
    <img src="https://img.shields.io/badge/Python-3.12-FFD64E.svg" alt="Python 3.12">
  </a>
  <a href="https://github.com/j3rrryy/school_464/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
</p>

## :book: Key features

- Microservice architecture
- gRPC between services
- Fast serialization with MessagePack
- Access and refresh JWT tokens
- Active sessions control
- Fast file upload/downolad
- Emails with new login info
- Main DB - PostgreSQL
- DB for cache - Redis
- S3 for files - MinIO
- Message broker between Gateway and Mail service - Apache Kafka

## :memo: To-Do list

- Tests
- Logs processing - Graylog, Elasticsearch, MongoDB
- Metrics processing - Prometheus, Grafana

![Architecture](https://github.com/j3rrryy/cloud_storage/blob/main/images/architecture.webp?raw=true)

> [!NOTE]
> API located at `/api`
>
> Docs located at `/api/docs`, but Swagger does not support MessagePack, so use another tool to send requests with this content type

## :computer: Requirements

- Docker

## :hammer_and_wrench: Getting started

- Copy `.env` file from `examples/dev/` to `dev/` folder and fill it in

- **(For dev/prod)** Copy `redis.conf` file from `examples/` to `dev/` or `prod/` folder and fill it in

- **(For prod)** Copy `.env` file from `examples/prod/` to `prod/` folder and fill it in

- **(For prod)** Copy `nginx.conf` file from `examples/prod/` to `prod/` folder and fill it in

- **(For prod)** Copy `docker-compose.cert.yml` file from `examples/prod/` to `prod/` folder and fill it in

### :rocket: Start

- Run the **dev ver.**

  ```shell
  docker compose -f docker-compose.dev.yml up --build -d
  ```

- Run the **prod ver.** and get a SSL certificate

  - Create the directory on the server

    ```shell
    mkdir -p /cloud_storage/
    ```

  - Use SCP to copy the prod files to the server

    ```shell
    scp -r ./prod/* <username>@<host>:/cloud_storage/
    ```

  - Run the deploy script

    ```shell
    bash deploy.sh
    ```

### :x: Stop

```shell
docker compose -f docker-compose.<dev/prod>.yml stop
```
