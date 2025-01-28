#!/bin/bash

set -e  # Exit on error

# Define the container and images directory
CONTAINER_NAME="mnist-container"
HOST_IMAGES_DIR="$(pwd)/images"
CONTAINER_IMAGES_DIR="/HW2/images"

# Ensure the images directory exists and is not empty
if [ ! -d "$HOST_IMAGES_DIR" ] || [ -z "$(ls -A "$HOST_IMAGES_DIR")" ]; then
    echo "Error: The images directory at $HOST_IMAGES_DIR does not exist or is empty."
    exit 1
fi

# Randomly choose an image from the images directory
RANDOM_IMAGE=$(find "$HOST_IMAGES_DIR" -type f | gshuf -n 1)

if [ -z "$RANDOM_IMAGE" ]; then
    echo "Error: No image was selected. Check the images directory."
    exit 1
fi

# Extract the image filename for reference
IMAGE_FILENAME=$(basename "$RANDOM_IMAGE")

# Copy the selected image to the container's directory
echo "Copying $RANDOM_IMAGE to the container..."
docker cp "$RANDOM_IMAGE" "$CONTAINER_NAME":"$CONTAINER_IMAGES_DIR/$IMAGE_FILENAME"

# Run the classification script inside the container
echo "Running classification for $IMAGE_FILENAME..."
docker exec "$CONTAINER_NAME" python3 pt_classify.py --input "$CONTAINER_IMAGES_DIR/$IMAGE_FILENAME"

# Output the expected and predicted classification
echo "Classification complete for $IMAGE_FILENAME."
