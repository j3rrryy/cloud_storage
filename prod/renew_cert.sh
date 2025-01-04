#!/bin/bash

cd ./cloud_storage/
docker compose -f docker-compose.cert.yml run --rm -d certbot renew
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
