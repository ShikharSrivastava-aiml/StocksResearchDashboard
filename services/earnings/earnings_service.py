from typing import Optional
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from data.api_client import APIClient

app = FastAPI(title="Earnings Service")
api_client = APIClient()

SERVICE_REGISTRY_URL = "http://service_registry:8010"
# Service details
SERVICE_NAME = "Earnings_Service"
SERVICE_HOST = "earnings_service"  # Service container name
SERVICE_PORT = 8001



class EarningsResponse(BaseModel):
    symbol: str
    earnings: dict  # whatever Alpha Vantage returns (quarterlyEarnings etc.)


class TranscriptResponse(BaseModel):
    symbol: str
    quarter: str
    transcript: dict  # raw transcript data from API


@app.get("/earnings/{symbol}", response_model=EarningsResponse)
def get_earnings(symbol: str):

    try:
        earnings_data = api_client.get_earnings(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching earnings: {e}")

    if not earnings_data:
        raise HTTPException(status_code=404, detail="No earnings data found")

    return EarningsResponse(symbol=symbol, earnings=earnings_data)


@app.get("/earnings/{symbol}/transcript", response_model=TranscriptResponse)
def get_transcript(
    symbol: str,
    quarter: str = Query(..., description="Quarter identifier, e.g. '2024-Q2'")
):

    try:
        transcript_data = api_client.get_earnings_transcript(symbol, quarter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transcript: {e}")

    if not transcript_data:
        raise HTTPException(status_code=404, detail="No transcript found")

    return TranscriptResponse(symbol=symbol, quarter=quarter, transcript=transcript_data)




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
    return {"message": "Earnings Service Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}