FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for health check
RUN apt-get update && apt-get install -y curl

# Copy source code
COPY . .

# Make health check script executable
RUN chmod +x health_check.py

# Set environment variable to wait for database
ENV WAIT_FOR_DB=1

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["python", "db_api.py"]
