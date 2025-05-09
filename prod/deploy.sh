#!/bin/bash

set -e

echo "Pulling Docker images..."
docker compose -f docker-compose.cert.yml pull
docker compose -f docker-compose.prod.yml pull

echo "Starting services for certificate generation..."
docker compose -f docker-compose.cert.yml up -d

certbot_container=$(docker compose -f docker-compose.cert.yml ps -q certbot)
echo "Waiting for Certbot container to exit..."
docker wait "$certbot_container"

echo "Certbot logs:"
docker logs "$certbot_container"

echo "Stopping certificate services..."
docker compose -f docker-compose.cert.yml down

echo "Starting production version..."
docker compose -f docker-compose.prod.yml up -d

echo "Scheduling tasks for certificate renewal and cleanup..."
sudo chmod +x renew_cert.sh cleanup.sh
(crontab -l; echo "0 0 1 */2 * bash ./cloud_storage/renew_cert.sh"; echo "0 0 * * * bash ./cloud_storage/cleanup.sh") | crontab -

echo "Deployment complete!"
