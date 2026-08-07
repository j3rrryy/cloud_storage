#!/bin/bash

set -e

sleep 7
mc alias set local http://${MINIO_HOST}:${MINIO_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

mc mb -p local/${MINIO_S3_BUCKET} || true
mc mb -p local/${MINIO_LOKI_BUCKET} || true

mc admin config set local api stale_uploads_expiry=24h
mc admin service restart local --json

exit 0
