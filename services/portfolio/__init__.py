# services/portfolio/portfolio_service.py

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from data.api_client import APIClient

app = FastAPI(title="Portfolio Service")
api_client = APIClient()


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
        quote_data = api_client.get_quote(pos.symbol)

        if not quote_data or "Global Quote" not in quote_data:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch quote for {pos.symbol}",
            )

        try:
            quote = quote_data["Global Quote"]
            current_price = float(quote["05. price"])
            # "10. change percent" is like "1.23%"
            change_percent_str = quote.get("10. change percent", "0%").replace("%", "")
            day_change_percent = float(change_percent_str)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error parsing quote for {pos.symbol}: {e}",
            )

        current_value = current_price * pos.shares
        cost_basis = pos.purchase_price * pos.shares
        gain_loss = current_value - cost_basis
        gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis != 0 else 0.0

        total_value += current_value
        total_cost += cost_basis

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
