from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import time
from typing import Optional

# ── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="🏠 Housing Price Predictor API",
    description=(
        "Predict California housing prices using a Linear Regression model "
        "trained on the California Housing dataset. Supports single and batch predictions."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Schemas ──────────────────────────────────────────────────────────
FEATURE_DESCRIPTIONS = {
    "median_income": "Median income in block group (×$10,000)",
    "house_age": "Median house age in block group",
    "avg_rooms": "Average number of rooms per household",
    "avg_bedrooms": "Average number of bedrooms per household",
    "population": "Block group population",
    "avg_occupancy": "Average number of household members",
    "latitude": "Block group latitude",
    "longitude": "Block group longitude",
}


class PredictionRequest(BaseModel):
    """Input features for a single house price prediction."""
    median_income: float = Field(..., description=FEATURE_DESCRIPTIONS["median_income"], examples=[3.5])
    house_age: float = Field(..., description=FEATURE_DESCRIPTIONS["house_age"], examples=[20.0], ge=0, le=100)
    avg_rooms: float = Field(..., description=FEATURE_DESCRIPTIONS["avg_rooms"], examples=[6.0], gt=0)
    avg_bedrooms: float = Field(..., description=FEATURE_DESCRIPTIONS["avg_bedrooms"], examples=[1.0], ge=0)
    population: float = Field(..., description=FEATURE_DESCRIPTIONS["population"], examples=[1200.0], ge=0)
    avg_occupancy: float = Field(..., description=FEATURE_DESCRIPTIONS["avg_occupancy"], examples=[3.0], gt=0)
    latitude: float = Field(..., description=FEATURE_DESCRIPTIONS["latitude"], examples=[37.5], ge=25, le=50)
    longitude: float = Field(..., description=FEATURE_DESCRIPTIONS["longitude"], examples=[-122.0], ge=-130, le=-110)

    model_config = {"json_schema_extra": {"examples": [
        {
            "median_income": 3.5, "house_age": 20.0, "avg_rooms": 6.0,
            "avg_bedrooms": 1.0, "population": 1200.0, "avg_occupancy": 3.0,
            "latitude": 37.5, "longitude": -122.0,
        }
    ]}}


class BatchPredictionRequest(BaseModel):
    """A batch of house feature sets for bulk prediction."""
    houses: list[PredictionRequest] = Field(
        ..., min_length=1, max_length=100,
        description="List of house feature sets (max 100 per batch)"
    )


class PredictionResponse(BaseModel):
    predicted_price: float = Field(..., description="Predicted median house value (in $100,000s)")
    predicted_usd: float = Field(..., description="Approximate price in US dollars")
    note: str = "Values are in units of $100,000 (e.g. 2.5 = $250,000)"


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
    count: int
    avg_price: float
    avg_usd: float


class HealthResponse(BaseModel):
    status: str
    model_trained: bool
    features: list[str]
    uptime_seconds: float


class ModelInfoResponse(BaseModel):
    model_type: str
    features: list[dict]
    target: str
    dataset: str
    training_samples: int
    model_version: str


# ── Model Training at Startup ─────────────────────────────────────────────────
scaler = StandardScaler()
model = LinearRegression()
FEATURE_NAMES: list[str] = []
model_ready = False
start_time: float = 0.0


@app.on_event("startup")
def train_model():
    global model_ready, FEATURE_NAMES, start_time
    start_time = time.time()

    housing = fetch_california_housing()
    FEATURE_NAMES = list(housing.feature_names)

    X = scaler.fit_transform(housing.data)
    y = housing.target

    model.fit(X, y)
    model_ready = True


def _predict_single(req: PredictionRequest) -> PredictionResponse:
    features = np.array([[
        req.median_income, req.house_age, req.avg_rooms,
        req.avg_bedrooms, req.population, req.avg_occupancy,
        req.latitude, req.longitude,
    ]])
    scaled = scaler.transform(features)
    prediction = model.predict(scaled)[0]
    return PredictionResponse(
        predicted_price=round(float(prediction), 4),
        predicted_usd=round(float(prediction) * 100_000, 2),
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "🏠 Housing Price Predictor API v2.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "predict": "POST /predict",
        "batch_predict": "POST /predict/batch",
        "model_info": "GET /model/info",
        "health": "GET /health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    return HealthResponse(
        status="healthy" if model_ready else "loading",
        model_trained=model_ready,
        features=FEATURE_NAMES,
        uptime_seconds=round(time.time() - start_time, 2),
    )


@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
def model_info():
    """Get detailed information about the trained model."""
    housing = fetch_california_housing()
    return ModelInfoResponse(
        model_type="Linear Regression",
        features=[
            {"name": name, "description": FEATURE_DESCRIPTIONS.get(name, "N/A")}
            for name in FEATURE_NAMES
        ],
        target="Median house value (×$100,000)",
        dataset="California Housing (sklearn)",
        training_samples=int(housing.data.shape[0]),
        model_version="2.0.0",
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(req: PredictionRequest):
    """Predict the price of a single house."""
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model is still training, try again shortly.")
    return _predict_single(req)


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
def predict_batch(req: BatchPredictionRequest):
    """Predict prices for multiple houses in a single request (max 100)."""
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model is still training, try again shortly.")

    predictions = [_predict_single(house) for house in req.houses]
    avg_price = round(float(np.mean([p.predicted_price for p in predictions])), 4)

    return BatchPredictionResponse(
        predictions=predictions,
        count=len(predictions),
        avg_price=avg_price,
        avg_usd=round(avg_price * 100_000, 2),
    )
