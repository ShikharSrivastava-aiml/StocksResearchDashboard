"""
Portfolio Manager Page
Manage and track investment portfolio
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from data.api_client import APIClient
from models.portfolio import Portfolio
from components.stock_input import stock_input_with_suggestions
from utils.helpers import format_currency, format_percentage


def render(api_client: APIClient, symbols_df: pd.DataFrame):
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
        render_portfolio_display(api_client, portfolio)


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


def render_portfolio_display(api_client: APIClient, portfolio: Portfolio):
    """Render the portfolio display with current values."""
    positions = st.session_state.get('portfolio', [])

    if not positions:
        st.info("No stocks in portfolio. Add some stocks to get started!")
        st.write("Your portfolio is automatically saved to your encrypted account.")
        return

    st.subheader(f"Your Portfolio ({len(positions)} positions)")

    # Fetch current prices
    portfolio_data = []
    total_value = 0
    total_cost = 0

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, stock in enumerate(positions):
        status_text.text(f"Fetching data for {stock['symbol']}... ({idx + 1}/{len(positions)})")
        progress_bar.progress((idx + 1) / len(positions))

        quote_data = api_client.get_quote(stock['symbol'])

        if quote_data and 'Global Quote' in quote_data:
            try:
                current_price = float(quote_data['Global Quote']['05. price'])
                change_percent = float(quote_data['Global Quote']['10. change percent'].replace('%', ''))

                current_value = current_price * stock['shares']
                cost_basis = stock['purchase_price'] * stock['shares']
                gain_loss = current_value - cost_basis
                gain_loss_percent = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0

                portfolio_data.append({
                    'Symbol': stock['symbol'],
                    'Shares': stock['shares'],
                    'Purchase Date': stock['date_added'],
                    'Purchase Price': format_currency(stock['purchase_price']),
                    'Current Price': format_currency(current_price),
                    'Current Value': format_currency(current_value),
                    'Cost Basis': format_currency(cost_basis),
                    'Gain/Loss': format_currency(gain_loss),
                    'Gain/Loss %': format_percentage(gain_loss_percent),
                    'Day Change %': format_percentage(change_percent)
                })

                total_value += current_value
                total_cost += cost_basis
            except Exception as e:
                st.warning(f"Error processing {stock['symbol']}: {e}")

    progress_bar.empty()
    status_text.empty()

    if portfolio_data:
        df = pd.DataFrame(portfolio_data)
        st.dataframe(df, use_container_width=True)

        # Remove stock functionality
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