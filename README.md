# Cloud Storage

<p align="center">
  <a href="https://www.python.org/downloads/release/python-3120/">
    <img src="https://img.shields.io/badge/Python-3.12-FFD64E.svg" alt="Python 3.12">
  </a>
  <a href="https://github.com/j3rrryy/school_464/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black formatter">
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

- Logs processing - Graylog, Elasticsearch, MongoDB
- Metrics processing - Prometheus, Grafana
- Сontainer orchestration - Kubernetes

![Architecture](https://github.com/j3rrryy/cloud_storage/blob/main/images/architecture.webp?raw=true)

> [!NOTE]
> API located at `/api`
> 
> Docs located at `/api/docs`, but Swagger does not support MessagePack, so use another tool to send requests with this content type

## :computer: Requirements

- Docker

## :hammer_and_wrench: Getting started

- Copy `.env.dev` file from `examples/env/` to `docker/env/` folder and fill it in
- Copy `redis.conf` file from `examples/redis/dev/` to `docker/redis/dev/` folder and fill it in

### :rocket: Start

- Run the **dev build**

    ```shell
    docker compose up --build -d
    ```

### :x: Stop

- Stop the **dev build**

  ```shell
  docker compose stop
  ```
