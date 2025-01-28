# Use the specified ARM64 base image with Python 3.9 slim bullseye
FROM python:3

WORKDIR /HW2

# Update package list and install Python 3 along with necessary tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip

# Install PyTorch (CPU version) and torchvision using pip
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the Python script into the container
COPY pt_train.py .
COPY pt_classify.py .

# Command to run the training script
CMD ["python3", "pt_train.py"]
