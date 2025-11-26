"""
Stock Analysis Report Page
Comprehensive stock analysis with charts and metrics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests  # NEW: to call the microservice
import json
import os
from components.stock_input import stock_input_with_suggestions
from components.metrics import display_company_header, display_key_metrics
from utils.service_discovery import get_service_url  # Importing the service discovery utility



SERVICE_NAME = "Stock_Analysis_Service"

def render(symbols_df: pd.DataFrame):
    """Render Stock Analysis Report page."""
    st.title("📊 Stock Analysis Report")

    col1, col2 = st.columns([1, 2])

    with col1:
        symbol = stock_input_with_suggestions(
            "Enter Stock Symbol",
            "analysis_symbol",
            symbols_df,
            st.session_state.get("analysis_symbol", "")
        )

        if st.button("🔍 Analyze Stock", use_container_width=True):
            if symbol:
                with st.spinner(f"Analyzing {symbol}..."):
                    try:
                        service_url = get_service_url(SERVICE_NAME)
                        res = requests.get(f"{service_url}/analysis/{symbol}")
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state['analysis_data'] = {
                                'overview': data['overview'],
                                'daily': data['daily'],
                                'symbol': data['symbol'],
                            }
                            st.success(f"✅ Analysis complete for {symbol}")
                        else:
                            st.error(f"Failed to analyze {symbol}: {res.text}")
                    except Exception as e:
                        st.error(f"Error contacting analysis service: {e}")
            else:
                st.warning("Please enter a stock symbol.")

    with col2:
        if 'analysis_data' in st.session_state:
            data = st.session_state['analysis_data']
            overview = data['overview']
            daily = data['daily']

            # Display company info
            display_company_header(overview)

            # Display key metrics
            display_key_metrics(overview)

            # Price chart
            if 'Time Series (Daily)' in daily:
                df = pd.DataFrame(daily['Time Series (Daily)']).T
                df.index = pd.to_datetime(df.index)
                df = df.astype(float)
                df = df.sort_index()
                df = df.tail(50)  # Last 50 days

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['4. close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='blue', width=2)
                ))

                fig.update_layout(
                    title=f"{data['symbol']} Stock Price (Last 50 Days)",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

                # Additional metrics
                latest_price = df.iloc[-1]['4. close']
                price_change = df.iloc[-1]['4. close'] - df.iloc[0]['4. close']
                price_change_pct = (price_change / df.iloc[0]['4. close']) * 100

                col3, col4, col5 = st.columns(3)
                with col3:
                    st.metric("Latest Price", f"${latest_price:.2f}")
                with col4:
                    st.metric("50-Day Change", f"${price_change:.2f}", f"{price_change_pct:.2f}%")
                with col5:
                    high_52w = overview.get('52WeekHigh', 'N/A')
                    low_52w = overview.get('52WeekLow', 'N/A')
                    st.metric("52W High", high_52w)
                    st.metric("52W Low", low_52w)
            else:
                st.info("No daily price data available.")
        else:
            st.info("Enter a stock symbol and click 'Analyze Stock' to begin.")



