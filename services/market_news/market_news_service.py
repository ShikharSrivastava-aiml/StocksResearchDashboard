import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from data.api_client import APIClient

app = FastAPI(title="Market News Service")
api_client = APIClient()

# URL of our the Service Registry
SERVICE_REGISTRY_URL = "http://service_registry:8010"
# Service details
SERVICE_NAME = "Market_News_Service"
SERVICE_HOST = "market_news_service"  # Service container name
SERVICE_PORT = 8002

class NewsResponse(BaseModel):
    mode: str
    symbol: Optional[str] = None
    topic: Optional[str] = None
    sort: str
    limit: int
    news: dict


@app.get("/news", response_model=NewsResponse)
def get_news(
    mode: str = Query(..., description="topic or ticker"),
    topic: Optional[str] = None,
    ticker: Optional[str] = None,
    sort: str = "LATEST",
    limit: int = 20
):
    """
    Microservice that wraps your EXACT existing logic from market_news.py
    """

    mode = mode.lower()

    # Validate
    if mode == "topic":
        if not topic:
            raise HTTPException(400, "topic is required when mode='topic'")

        # From your real code:
        news_data = api_client.get_news_sentiment(
            topics=topic,
            sort=sort,
            limit=limit
        )

    elif mode == "ticker":
        if not ticker:
            raise HTTPException(400, "ticker is required when mode='ticker'")

        # From your real code:
        news_data = api_client.get_news_sentiment(
            tickers=ticker,
            sort=sort,
            limit=limit
        )

    else:
        raise HTTPException(400, "mode must be 'topic' or 'ticker'")

    if not news_data:
        raise HTTPException(404, "No news returned")

    return NewsResponse(
        mode=mode,
        symbol=ticker,
        topic=topic,
        sort=sort,
        limit=limit,
        news=news_data
    )




# Register the service with the Service Registry
def register_service_with_registry():
    payload = {
        "service_name": SERVICE_NAME,
        "service_url": SERVICE_HOST,  # Service URL (container name)
        "port": SERVICE_PORT,
    }
    try:
        response = requests.post(f"{SERVICE_REGISTRY_URL}/register", json=payload)
        if response.status_code == 200:
            print(f"Service {SERVICE_NAME} registered with Service Registry.")
        else:
            print(f"Failed to register {SERVICE_NAME} with Service Registry.")
    except Exception as e:
        print(f"Error registering service with Service Registry: {e}")

# Deregister the service from the Service Registry
def deregister_service_from_registry():
    try:
        response = requests.delete(f"{SERVICE_REGISTRY_URL}/deregister/{SERVICE_NAME}")
        if response.status_code == 200:
            print(f"Service {SERVICE_NAME} deregistered from Service Registry.")
        else:
            print(f"Failed to deregister {SERVICE_NAME} from Service Registry.")
    except Exception as e:
        print(f"Error deregistering service from Service Registry: {e}")



@app.on_event("startup")
async def startup_event():
    # Register the service with the Service Registry during startup
    register_service_with_registry()

@app.on_event("shutdown")
async def shutdown_event():
    # Deregister the service from the Service Registry during shutdown
    deregister_service_from_registry()


@app.get("/")
def read_root():
    return {"message": "Market News Service Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}