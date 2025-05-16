FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install fastapi uvicorn mysql-connector-python

EXPOSE 8000

CMD ["python", "db_api.py"] 