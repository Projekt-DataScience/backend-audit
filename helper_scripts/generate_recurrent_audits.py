"""
This script will trigger the endpoint for generating recurrent audits.
It will be called by a cronjob every day at 00:00 inside the docker container.
"""

import requests

URL = "http://localhost:8000/planned/generate_recurrent_audits"
response = requests.get(URL)
print(response.json())