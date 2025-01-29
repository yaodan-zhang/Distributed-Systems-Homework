# Use an official Python runtime as a parent image
FROM python:3.9-slim

WORKDIR /

# Copy required files into the container
COPY map.py reduce.py ./

# Create counts directory (this will be mounted as a shared volume)
RUN mkdir -p /counts
RUN mkdir -p /titles

# Set default command to bash so we can run scripts dynamically
CMD ["/bin/bash"]
