# Cloud Storage

<p align="center">
  <a href="https://github.com/j3rrryy/cloud_storage/actions/workflows/main.yml">
    <img src="https://github.com/j3rrryy/cloud_storage/actions/workflows/main.yml/badge.svg" alt="СI/CD">
  </a>
  <a href="https://codecov.io/gh/j3rrryy/cloud_storage">
    <img src="https://codecov.io/gh/j3rrryy/cloud_storage/graph/badge.svg?token=T84VVOKWC8" alt="Codecov">
  </a>
  <a href="https://www.python.org/downloads/release/python-3120/">
    <img src="https://img.shields.io/badge/Python-3.12-FFD64E.svg" alt="Python 3.12">
  </a>
  <a href="https://github.com/j3rrryy/cloud_storage/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
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
- S3 for files and logs - MinIO
- Message broker between Gateway and Mail service - Apache Kafka
- Monitoring - Prometheus & Grafana
- Log aggregation - Promtail & Loki & Grafana

![Architecture](https://github.com/j3rrryy/cloud_storage/blob/main/images/architecture.webp?raw=true)

> [!NOTE]
> API located at `/api`
>
> Docs located at `/api/docs`, but Swagger does not support MessagePack, so use another tool to send requests with this content type
>
> Grafana located at `/admin/grafana`

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

  - Only API

    ```shell
    docker compose -f docker-compose.dev.yml --profile api up --build -d
    ```

  - API + monitoring

    ```shell
    docker compose -f docker-compose.dev.yml --profile all up --build -d
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
