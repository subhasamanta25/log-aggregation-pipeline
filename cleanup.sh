#!/bin/bash

echo "Cleaning up...."

docker-compose down -v

rm -rf logs
rm -rf processed
rm -rf reports

echo "Cleanup complete"
