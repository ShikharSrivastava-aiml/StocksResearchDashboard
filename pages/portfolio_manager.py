"""
Portfolio Manager Page
Manage and track investment portfolio
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import requests  # NEW
from models.portfolio import Portfolio
from components.stock_input import stock_input_with_suggestions
from utils.helpers import format_currency, format_percentage
from utils.service_discovery import get_service_url

# # Load the configuration from config.json
# config_path = '/app/config.json'
#
# with open(config_path, 'r') as f:
#     config = json.load(f)
#

SERVICE_NAME = "Portfolio_Service"


def render(symbols_df: pd.DataFrame):
    """Render Portfolio Manager page."""
    st.title("💼 Portfolio Manager")

    username = st.session_state.get('username')
    portfolio = Portfolio(username)

    # Initialize portfolio in session state
    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = portfolio.get_all()

    col1, col2 = st.columns([1, 2])

    with col1:
        render_add_position(portfolio, symbols_df)

    with col2:
        render_portfolio_display( portfolio)


def render_add_position(portfolio: Portfolio, symbols_df: pd.DataFrame):
    """Render the add position form."""
    st.subheader("Add Stock to Portfolio")

    new_symbol = stock_input_with_suggestions(
        "Stock Symbol",
        "portfolio_symbol",
        symbols_df
    )

    shares = st.number_input("Number of Shares", min_value=1, value=1)
    purchase_price = st.number_input(
        "Purchase Price ($)",
        min_value=0.01,
        value=100.0,
        format="%.2f"
    )
    purchase_date = st.date_input("Purchase Date", value=datetime.now())

    if st.button("➕ Add to Portfolio", use_container_width=True):
        if new_symbol:
            if portfolio.add_position(
                    new_symbol,
                    shares,
                    purchase_price,
                    purchase_date.strftime('%Y-%m-%d')
            ):
                st.session_state['portfolio'] = portfolio.get_all()
                st.success(f"✅ Added {shares} shares of {new_symbol.upper()}")
                st.rerun()
            else:
                st.error("Failed to add position")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("💾 Save", use_container_width=True):
            if portfolio.save():
                st.success("✅ Portfolio saved!")
            else:
                st.error("Failed to save")

    with col_b:
        if st.button("🔄 Reload", use_container_width=True):
            st.session_state['portfolio'] = portfolio.get_all()
            st.success("✅ Reloaded")
            st.rerun()

    if st.button("🗑️ Clear Portfolio", use_container_width=True):
        if portfolio.clear():
            st.session_state['portfolio'] = []
            st.success("Portfolio cleared")
            st.rerun()

def render_portfolio_display(portfolio: Portfolio):
    """Render the portfolio display with current values."""
    positions = st.session_state.get('portfolio', [])

    if not positions:
        st.info("No stocks in portfolio. Add some stocks to get started!")
        st.write("Your portfolio is automatically saved to your encrypted account.")
        return

    st.subheader(f"Your Portfolio ({len(positions)} positions)")

    # Send positions to the portfolio microservice
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("Calculating portfolio metrics...")
    progress_bar.progress(0.2)

    # Build payload for service
    payload_positions = []
    for p in positions:
        payload_positions.append(
            {
                "symbol": p["symbol"],
                "shares": float(p["shares"]),
                "purchase_price": float(p["purchase_price"]),
                "date_added": p.get("date_added"),
            }
        )

    try:
        service_url = get_service_url(SERVICE_NAME)
        res = requests.post(
            f"{service_url}/portfolio/calculate",
            json=payload_positions,
        )
        progress_bar.progress(0.7)

        if res.status_code == 200:
            data = res.json()
            enriched_positions = data["positions"]
            summary = data["summary"]
        else:
            progress_bar.empty()
            status_text.empty()
            st.error(
                f"Error from portfolio service: {res.status_code} - {res.text}"
            )
            return
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Error contacting portfolio service: {e}")
        return

    progress_bar.progress(1.0)
    status_text.text("✅ Portfolio updated")
    progress_bar.empty()
    status_text.empty()

    # Build table data (with formatted values) for display
    portfolio_data = []

    for pos in enriched_positions:
        current_value = pos["current_value"]
        cost_basis = pos["cost_basis"]
        gain_loss = pos["gain_loss"]
        gain_loss_percent = pos["gain_loss_percent"]
        day_change_percent = pos["day_change_percent"]

        portfolio_data.append({
            'Symbol': pos['symbol'],
            'Shares': pos['shares'],
            'Purchase Date': pos.get('date_added', '-'),
            'Purchase Price': format_currency(pos['purchase_price']),
            'Current Price': format_currency(pos['current_price']),
            'Current Value': format_currency(current_value),
            'Cost Basis': format_currency(cost_basis),
            'Gain/Loss': format_currency(gain_loss),
            'Gain/Loss %': format_percentage(gain_loss_percent),
            'Day Change %': format_percentage(day_change_percent)
        })

    total_value = summary["total_value"]
    total_cost = summary["total_cost"]

    if portfolio_data:
        df = pd.DataFrame(portfolio_data)
        st.dataframe(df, use_container_width=True)

        # Remove stock functionality (unchanged)
        with st.expander("🗑️ Remove Stocks from Portfolio"):
            remove_symbol = st.selectbox(
                "Select stock to remove:",
                [s['symbol'] for s in positions]
            )
            if st.button("Remove Selected Stock"):
                if portfolio.remove_position(remove_symbol):
                    st.session_state['portfolio'] = portfolio.get_all()
                    st.success(f"Removed {remove_symbol} from portfolio")
                    st.rerun()

        # Portfolio summary
        render_portfolio_summary(portfolio_data, total_value, total_cost)


def render_portfolio_summary(portfolio_data: list, total_value: float, total_cost: float):
    """Render portfolio summary metrics and charts."""
    total_gain_loss = total_value - total_cost
    total_gain_loss_percent = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0

    st.markdown("---")
    st.subheader("📊 Portfolio Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Value", format_currency(total_value))
    with col2:
        st.metric("Total Cost", format_currency(total_cost))
    with col3:
        st.metric(
            "Total Gain/Loss",
            format_currency(total_gain_loss),
            format_percentage(total_gain_loss_percent)
        )
    with col4:
        st.metric("Positions", len(portfolio_data))

    # Portfolio allocation chart
    if portfolio_data:
        fig = go.Figure(data=[go.Pie(
            labels=[p['Symbol'] for p in portfolio_data],
            values=[float(p['Current Value'].replace('$', '').replace(',', '')) for p in portfolio_data],
            hole=.3
        )])

        fig.update_layout(
            title="Portfolio Allocation by Value",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Export portfolio
        if st.button("📥 Export Portfolio Data"):
            import json
            export_data = {
                'username': st.session_state.get('username'),
                'exported_at': datetime.now().isoformat(),
                'portfolio': st.session_state.get('portfolio', []),
                'summary': {
                    'total_value': total_value,
                    'total_cost': total_cost,
                    'total_gain_loss': total_gain_loss,
                    'total_gain_loss_percent': total_gain_loss_percent
                }
            }

            st.download_button(
                label="Download as JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"portfolio_{st.session_state.get('username')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )