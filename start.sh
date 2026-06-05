#!/bin/bash

cleanup() {

	echo ""
	echo "Stopping Pipeline"

	docker-compose down
	exit 0
}

trap cleanup SIGINT

echo "Starting Log Aggregation Pipeline...."

docker-compose up --build
