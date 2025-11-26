# stock_analysis_service.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from data.api_client import APIClient  # same APIClient you already use in your app
import requests


app = FastAPI(title="Stock Analysis Service")
api_client = APIClient()


# URL of our the Service Registry
SERVICE_REGISTRY_URL = "http://service_registry:8010"
# Service details
SERVICE_NAME = "Stock_Analysis_Service"
SERVICE_HOST = "stock_analysis_service"  # Service container name
SERVICE_PORT = 8004



class AnalysisResponse(BaseModel):
    symbol: str
    overview: dict
    daily: dict

@app.get("/analysis/{symbol}", response_model=AnalysisResponse)
def get_analysis(symbol: str):
    """
    Microservice endpoint for stock analysis.
    It uses APIClient internally and returns overview + daily data as JSON.
    """
    try:
        overview = api_client.get_company_overview(symbol)
        daily = api_client.get_daily_prices(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

    if not overview or not daily:
        raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")

    return AnalysisResponse(symbol=symbol, overview=overview, daily=daily)




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
    return {"message": "Stock Analysis Service Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


