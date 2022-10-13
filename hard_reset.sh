#!/bin/bash
echo "Closing docker containers..."
sudo docker-compose down -v --remove-orphans
echo "Opening docker containers in a daemon..."
sudo docker-compose up -d --build
echo "Writing new permissions..."
sudo bash set_write_permissions.sh
echo "Waiting for database creation..."
sleep 15
echo "Creating dev users..."
docker-compose exec report django-admin quickstart_dev
docker-compose exec admin django-admin quickstart_dev
echo "Hard reset completed."
