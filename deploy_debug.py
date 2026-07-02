import urllib.request
import json
import sys

API_KEY = "rnd_oiIkVUckgnBBk30cejMCa8wl5hfC"
OWNER_ID = "tea-d92tbijtqb8s73cpugg0"

# Try format 1: repo as object inside serviceDetails
payload = {
    "name": "housing-price-predictor",
    "type": "web_service",
    "ownerId": OWNER_ID,
    "serviceDetails": {
        "env": "python",
        "repo": "https://github.com/shekharmayank214-debug/housing-price-predictor-api",
        "branch": "master",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
        "envVars": [
            {"key": "PYTHON_VERSION", "value": "3.11.11"}
        ]
    }
}

data = json.dumps(payload).encode("utf-8")
print("=== Format 1: repo inside serviceDetails ===")
print("Payload bytes length:", len(data))
print("First 200 bytes:", data[:200])
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
    print("SUCCESS!")
    print(json.dumps(result, indent=2))
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP {e.code}: {body}")
    print()

# Try format 2: flat structure with ownerId
payload2 = {
    "name": "housing-price-predictor",
    "type": "web_service",
    "ownerId": OWNER_ID,
    "repo": "https://github.com/shekharmayank214-debug/housing-price-predictor-api",
    "branch": "master",
    "buildCommand": "pip install -r requirements.txt",
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "env": "python",
    "envVars": [
        {"key": "PYTHON_VERSION", "value": "3.11.11"}
    ]
}

data2 = json.dumps(payload2).encode("utf-8")
print("=== Format 2: flat with ownerId ===")

req2 = urllib.request.Request(
    "https://api.render.com/v1/services",
    data=data2,
    headers={
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    resp2 = urllib.request.urlopen(req2)
    result2 = json.loads(resp2.read().decode("utf-8"))
    print("SUCCESS!")
    print(json.dumps(result2, indent=2))
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP {e.code}: {body}")
