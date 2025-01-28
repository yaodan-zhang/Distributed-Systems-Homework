#!/bin/bash

set -e

IMAGE_NAME="mnist-trainer"
CONTAINER_NAME="mnist-container"
CONTAINER_IMAGES_DIR="/HW2/images"

# Resolve the current directory and validate it
CURRENT_DIR="$(pwd)"
if [ -z "$CURRENT_DIR" ]; then
    echo "Error: Unable to resolve the current working directory."
    exit 1
fi

# Define the host and container image directories
HOST_IMAGES_DIR="$CURRENT_DIR/images"
CONTAINER_IMAGES_DIR="/HW2/images"

# Ensure the host images directory exists
if [ ! -d "$HOST_IMAGES_DIR" ]; then
    echo "Creating images directory at $HOST_IMAGES_DIR..."
    mkdir -p "$HOST_IMAGES_DIR"
fi

#Run the Docker container persistently with the images directory mounted
echo "Running the Docker container '$CONTAINER_NAME'..."

docker run -dit --name "$CONTAINER_NAME" \
    -v "$HOST_IMAGES_DIR":"$CONTAINER_IMAGES_DIR" \
    "$IMAGE_NAME"


echo "Docker container '$CONTAINER_NAME' is now running persistently."
echo "Host images directory '$HOST_IMAGES_DIR' is mounted to '$CONTAINER_IMAGES_DIR' inside the container."
