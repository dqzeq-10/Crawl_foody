#!/bin/sh

# Health check script for API Gateway
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)

if [ "$response" = "200" ]; then
  echo "API Gateway is healthy!"
  exit 0
else
  echo "API Gateway is not healthy! HTTP status: $response"
  exit 1
fi