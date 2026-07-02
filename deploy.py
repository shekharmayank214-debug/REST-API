import urllib.request
import json
import sys

API_KEY = "rnd_oiIkVUckgnBBk30cejMCa8wl5hfC"
OWNER_ID = "tea-d92tbijtqb8s73cpugg0"

payload = {
    "name": "housing-price-predictor",
    "type": "web_service",
    "ownerId": OWNER_ID,
    "repo": {
        "url": "https://github.com/shekharmayank214-debug/housing-price-predictor-api",
        "branch": "master"
    },
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
print("Payload:", json.dumps(payload, indent=2))
print()

req = urllib.request.Request(
    "https://api.render.com/v1/services",
    data=data,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode("utf-8"))
    print("SUCCESS! Service created:")
    print(json.dumps(result, indent=2))
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP {e.code}: {body}")
    sys.exit(1)
