#!/bin/bash

sleep 7
mc alias set local http://${MINIO_HOST}:${MINIO_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
mc mb -p local/${MINIO_S3_BUCKET}
mc mb -p local/${MINIO_LOKI_BUCKET}
exit 0
