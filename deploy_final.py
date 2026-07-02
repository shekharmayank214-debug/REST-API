import urllib.request
import json
import sys
import time

API_KEY = "rnd_oiIkVUckgnBBk30cejMCa8wl5hfC"
OWNER_ID = "tea-d92tbijtqb8s73cpugg0"

payload = {
    "name": "housing-price-predictor",
    "type": "web_service",
    "ownerId": OWNER_ID,
    "repo": "https://github.com/shekharmayank214-debug/housing-price-predictor-api",
    "branch": "master",
    "serviceDetails": {
        "env": "python",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
        "envVars": [
            {"key": "PYTHON_VERSION", "value": "3.11.11"}
        ]
    }
}

data = json.dumps(payload).encode("utf-8")
print("Sending request...")
print("Payload:", json.dumps(payload, indent=2))
print()

req = urllib.request.Request(
    "https://api.render.com/v1/services",
    data=data,
    headers={
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode("utf-8"))
    print("SUCCESS! Service created:")
    print(json.dumps(result, indent=2))
    if "id" in result:
        print(f"\nService ID: {result['id']}")
    if "serviceDetails" in result and "url" in result.get("serviceDetails", {}):
        print(f"URL: {result['serviceDetails']['url']}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP {e.code}: {body}")
    for h in e.headers:
        if "rate" in h.lower() or "retry" in h.lower() or "limit" in h.lower():
            print(f"  {h}: {e.headers[h]}")
    sys.exit(1)
