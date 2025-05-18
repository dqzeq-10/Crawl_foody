FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for health check
RUN apt-get update && apt-get install -y curl

# Copy source code
COPY . .

# Create directory for output if it doesn't exist
RUN mkdir -p /app/landing_zone

# Make start.sh executable
RUN chmod +x start.sh

EXPOSE 8000

# Command to run the crawler API
CMD ["uvicorn", "crawler_api:app", "--host", "0.0.0.0", "--port", "8000"]