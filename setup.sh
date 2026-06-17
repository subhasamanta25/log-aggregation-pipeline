#!/bin/bash

echo "=========================="
echo "Log Aggregation Pipeline Setup"
echo "=========================="

mkdir -p logs processed reports
chmod 777 logs processed reports

echo " "
echo "Checking Docker..."

docker --version || {
	echo "Docker not Installed!!"
	exit 1
}

echo " "
echo "Checking Docker Compose..."

docker-compose --version || {
	echo "Docker Compose not Installed!!"
	exit 1
}

echo " "
echo "Setup Complete..."
