# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the entire project structure (from root) into the container
COPY ../.. /app

# Set the PYTHONPATH to include /app (the root directory)
ENV PYTHONPATH=/app

# Install the required dependencies from requirements.txt for the Service Registry
RUN pip install --no-cache-dir -r /app/services/registry/requirements.txt

# Expose the port that the service will run on
EXPOSE 8010

# Command to run the service using uvicorn
CMD ["uvicorn", "services.registry.service_registry:app", "--host", "0.0.0.0", "--port", "8010"]
