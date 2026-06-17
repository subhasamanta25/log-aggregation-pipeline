#!/bin/bash

echo "Pipeline Monitoring..."
while true
do
	echo "======================="
	echo "Docker Containers..."
	echo "======================="

	docker-compose ps

	echo " "
	echo "======================="
	echo "Volume Usage..."
	echo "======================="

	du -sh logs/* processed/* reports/* 2>/dev/null

	echo " "
	echo "======================="
	echo "Recent Logs..."
	echo "======================="

	tail -5 processed/clean.log 2>/dev/null || \

	echo "No processed logs yet"

	echo " "
	echo "Refreshing in 5 seconds..."

	sleep 5
done
