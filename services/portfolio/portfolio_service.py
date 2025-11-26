# services/portfolio/portfolio_service.py

from typing import List, Optional

from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from data.api_client import APIClient

app = FastAPI(title="Portfolio Service")
api_client = APIClient()

# URL of our the Service Registry
SERVICE_REGISTRY_URL = "http://service_registry:8010"
# Service details
SERVICE_NAME = "Portfolio_Service"
SERVICE_HOST = "portfolio_service"  # Service container name
SERVICE_PORT = 8003


class Position(BaseModel):
    symbol: str
    shares: float
    purchase_price: float
    date_added: Optional[str] = None


class EnrichedPosition(Position):
    current_price: float
    current_value: float
    cost_basis: float
    gain_loss: float
    gain_loss_percent: float
    day_change_percent: float


class PortfolioSummary(BaseModel):
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_percent: float


class PortfolioResponse(BaseModel):
    positions: List[EnrichedPosition]
    summary: PortfolioSummary


@app.post("/portfolio/calculate", response_model=PortfolioResponse)
def calculate_portfolio(positions: List[Position]):
    """
    Take a list of positions, fetch quotes, and compute portfolio metrics.
    This replaces the loop in render_portfolio_display that called api_client.get_quote.
    """
    if not positions:
        raise HTTPException(status_code=400, detail="No positions provided")

    enriched_positions: List[EnrichedPosition] = []
    total_value = 0.0
    total_cost = 0.0

    for pos in positions:
        try:
            # Fetch the quote for the current symbol
            quote_data = api_client.get_quote(pos.symbol)

            if not quote_data or "Global Quote" not in quote_data or not quote_data["Global Quote"]:
                # Log the failure for the symbol and skip the current position
                print(f"Skipping {pos.symbol}: No valid quote data available.")
                continue  # Skip to the next position

            # Extract quote data
            quote = quote_data["Global Quote"]
            current_price = float(quote["05. price"])
            # "10. change percent" is like "1.23%"
            change_percent_str = quote.get("10. change percent", "0%").replace("%", "")
            day_change_percent = float(change_percent_str)

            # Calculate the values for the position
            current_value = current_price * pos.shares
            cost_basis = pos.purchase_price * pos.shares
            gain_loss = current_value - cost_basis
            gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis != 0 else 0.0

            # Add to the totals
            total_value += current_value
            total_cost += cost_basis

            # Append the enriched position to the list
            enriched_positions.append(
                EnrichedPosition(
                    symbol=pos.symbol,
                    shares=pos.shares,
                    purchase_price=pos.purchase_price,
                    date_added=pos.date_added,
                    current_price=current_price,
                    current_value=current_value,
                    cost_basis=cost_basis,
                    gain_loss=gain_loss,
                    gain_loss_percent=gain_loss_percent,
                    day_change_percent=day_change_percent,
                )
            )
        except Exception as e:
            # Log the exception and continue with the next position
            print(f"Error processing {pos.symbol}: {e}")
            continue

    total_gain_loss = total_value - total_cost
    total_gain_loss_percent = (
        total_gain_loss / total_cost * 100 if total_cost != 0 else 0.0
    )

    summary = PortfolioSummary(
        total_value=total_value,
        total_cost=total_cost,
        total_gain_loss=total_gain_loss,
        total_gain_loss_percent=total_gain_loss_percent,
    )

    return PortfolioResponse(positions=enriched_positions, summary=summary)


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
    return {"message": "Portfolio Service Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}