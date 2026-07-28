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
- Multipart file upload & download
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

- Docker **(dev)**
- Kubernetes **(dev + prod)**

- **(For k8s)** Install NGINX Ingress Controller

  ```shell
  helm install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx --namespace ingress-nginx --create-namespace --set controller.allowSnippetAnnotations=true --set controller.config.annotations-risk-level=Critical
  ```

- **(For prod-k8s)** Install cert-manager and configure a ClusterIssuer

  ```shell
  helm install cert-manager jetstack/cert-manager --repo https://charts.jetstack.io --namespace cert-manager --create-namespace --set installCRDs=true
  kubectl apply -f - <<EOF
  apiVersion: cert-manager.io/v1
  kind: ClusterIssuer
  metadata:
    name: letsencrypt-prod
  spec:
    acme:
      server: https://acme-v02.api.letsencrypt.org/directory
      email: <your_email>
      privateKeySecretRef:
        name: letsencrypt-prod
      solvers:
        - http01:
            ingress:
              class: nginx
  EOF
  ```

## :hammer_and_wrench: Getting started

- **(For dev-docker)** Copy `.env` file from `examples/` to `docker/` folder and fill it in

- **(For dev-docker)** Copy `redis.conf` file from `examples/` to `docker/` folder and fill it in

- **(For dev-k8s/prod-k8s)** Copy `values-<dev/prod>.yaml` file from `examples/` to `k8s/` folder and fill it in

### :rocket: Start

- Run the **dev ver.**

  - Only API

    ```shell
    docker compose --profile api up --build -d
    ```

  - API + monitoring

    ```shell
    docker compose --profile all up --build -d
    ```

  - Using Kubernetes

    ```shell
    helm dependency update ./k8s
    helm upgrade --install cloud-storage ./k8s -f ./k8s/values-dev.yaml --namespace cloud-storage --create-namespace
    ```

- Run the **prod ver.**

  ```shell
  helm dependency update ./k8s
  helm upgrade --install cloud-storage ./k8s -f ./k8s/values-prod.yaml --namespace cloud-storage --create-namespace
  ```

### :x: Stop

- Using Docker

  ```shell
  docker compose stop
  ```

- Using Kubernetes

  ```shell
  helm uninstall cloud-storage --namespace cloud-storage
  ```

### :chart_with_upwards_trend: Load testing

- Install Locust

```shell
pip install locust
```

- Run the script

```shell
locust --host localhost -f ./load_testing/load_test.py
```

- Open the [console](http://localhost:8089)
