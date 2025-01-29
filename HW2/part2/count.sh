#!/bin/bash

echo "Starting 9 mapper containers..."

# Start 9 mapper containers
for i in {1..9}
do
    docker run --rm -v "$(pwd)/counts:/counts" -v "$(pwd)/titles:/titles" wordcount-image python map.py $i &
done

# Wait for all background processes (mappers) to finish
wait

echo "All mappers are done. Starting reducer..."

# Start reducer container
docker run --rm -v "$(pwd)/counts:/counts" wordcount-image python reduce.py

# Copy result file to host
cp counts/total_counts.json .

echo "Processing complete. total_counts.json copied to host."

# Cleanup
rm -rf counts
