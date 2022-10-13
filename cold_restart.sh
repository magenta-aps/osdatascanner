#!/bin/bash
echo "Closing docker containers..."
sudo docker-compose down
echo "Opening docker containers in a daemon..."
sudo docker-compose up -d
echo "Writing new permissions..."
sudo bash set_write_permissions.sh
echo "Cold restart completed."
