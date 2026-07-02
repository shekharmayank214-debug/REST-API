# 🏠 Housing Price Predictor API

A REST API that predicts California housing prices using Linear Regression, trained on the [California Housing dataset](https://scikit-learn.org/stable/datasets/real_world.html#california-housing-dataset).

## Live API

Once deployed, access:
- **Interactive Docs (Swagger):** `https://<your-url>/docs`
- **ReDoc:** `https://<your-url>/redoc`
- **Health Check:** `https://<your-url>/health`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info and links |
| GET | `/health` | Health check & model status |
| GET | `/model/info` | Model metadata & feature descriptions |
| POST | `/predict` | Single house price prediction |
| POST | `/predict/batch` | Batch predictions (up to 100 houses) |

## Example: Single Prediction

```bash
curl -X POST https://<your-url>/predict \
  -H "Content-Type: application/json" \
  -d '{
    "median_income": 3.5,
    "house_age": 20.0,
    "avg_rooms": 6.0,
    "avg_bedrooms": 1.0,
    "population": 1200.0,
    "avg_occupancy": 3.0,
    "latitude": 37.5,
    "longitude": -122.0
  }'
```

**Response:**
```json
{
  "predicted_price": 2.1847,
  "predicted_usd": 218470.0,
  "note": "Values are in units of $100,000 (e.g. 2.5 = $250,000)"
}
```

## Example: Batch Prediction

```bash
curl -X POST https://<your-url>/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "houses": [
      {"median_income": 3.5, "house_age": 20, "avg_rooms": 6, "avg_bedrooms": 1, "population": 1200, "avg_occupancy": 3, "latitude": 37.5, "longitude": -122},
      {"median_income": 8.0, "house_age": 5, "avg_rooms": 8, "avg_bedrooms": 2, "population": 800, "avg_occupancy": 2.5, "latitude": 37.8, "longitude": -122.3}
    ]
  }'
```

## Features

- **Single & Batch Predictions** — predict one or up to 100 houses per request
- **Input Validation** — Pydantic validates all inputs with bounds checking
- **CORS Enabled** — accessible from any frontend
- **Auto-trained Model** — trains on startup, ready in seconds
- **Health & Model Info** — monitor model status and metadata

## Tech Stack

- **FastAPI** — modern Python web framework
- **scikit-learn** — Linear Regression on California Housing data
- **Pydantic** — request/response validation
- **Render** — deployment platform

## Run Locally

```bash
cd housing-api
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` for the interactive Swagger UI.
