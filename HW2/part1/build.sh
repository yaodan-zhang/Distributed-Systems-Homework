#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the image name
IMAGE_NAME="mnist-trainer"

# Build the Docker image
echo "Building the Docker image: $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

echo "Docker image '$IMAGE_NAME' built successfully!"
