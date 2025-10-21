# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN apt-get update && \
    apt-get install -y default-mysql-client tar curl unzip && \
    curl https://rclone.org/install.sh | bash && \
    apt-get purge -y --auto-remove curl unzip && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory as a package
COPY ./app ./app

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]