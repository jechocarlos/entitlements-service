# Start with the official Python image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any, e.g., for psycopg2 if not using -binary)
# RUN apt-get update && apt-get install -y some-package

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt ./

# Install project dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./app /app/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# The --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
