FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for health check and network tools
RUN apt-get update && apt-get install -y curl iputils-ping dnsutils net-tools iproute2

# Copy source code
COPY . .

# Make sure we have the right directory structure
RUN mkdir -p /app/landing_zone

# Make start.sh and entrypoint.sh executable
RUN chmod +x start.sh entrypoint.sh

# Expose API port
EXPOSE 8000

# Command to run the API
CMD ["uvicorn", "data_ingestion_api:app", "--host", "0.0.0.0", "--port", "8000"]