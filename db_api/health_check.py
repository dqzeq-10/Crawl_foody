#!/usr/bin/env python3
# Health check script for db_api

import requests
import sys

try:
    response = requests.get('http://localhost:8000/')
    if response.status_code == 200:
        print("DB API is healthy!")
        sys.exit(0)
    else:
        print(f"DB API returned status code {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"Error when checking DB API health: {str(e)}")
    sys.exit(1)
