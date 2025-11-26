# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the entire project structure (from root) into the container
COPY . /app

# Set the PYTHONPATH to include /app (the root directory)
ENV PYTHONPATH=/app


# Install the required dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port that Streamlit will run on (default is 8501)
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]
