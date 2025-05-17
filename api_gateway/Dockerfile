FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose the port that API Gateway will run on
EXPOSE 8080

# Command to run the API Gateway
CMD ["python", "app.py"]
