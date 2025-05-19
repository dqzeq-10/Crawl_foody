#!/bin/sh

# Health check script for Data Ingestion API
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/status)

if [ "$response" = "200" ]; then
  echo "Data Ingestion API is healthy!"
  exit 0
else
  echo "Data Ingestion API is not healthy! HTTP status: $response"
  exit 1
fi