"""
Reusable Metric Components
Common metric displays used across pages
"""

import streamlit as st
from typing import Optional
from utils.helpers import get_sentiment_color, get_sentiment_label


def display_sentiment_metrics(sentiments: list):
    """Display sentiment analysis metrics."""
    if not sentiments:
        return

    avg_sentiment = sum(sentiments) / len(sentiments)
    sentiment_label = get_sentiment_label(avg_sentiment)
    positive_count = sum(1 for s in sentiments if s > 0.2)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Sentiment", sentiment_label)
    with col2:
        st.metric("Average Score", f"{avg_sentiment:.3f}")
    with col3:
        st.metric("Positive Segments", f"{positive_count}/{len(sentiments)}")


def display_eps_metrics(eps_data: dict):
    """Display EPS performance metrics."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Reported EPS", eps_data.get('eps', 'N/A'))

    with col2:
        st.metric("Estimated EPS", eps_data.get('estimated_eps', 'N/A'))

    with col3:
        surprise = eps_data.get('surprise', 'N/A')
        if surprise != 'N/A':
            try:
                surprise_val = float(surprise)
                delta_color = "normal" if surprise_val >= 0 else "inverse"
                st.metric("EPS Surprise", f"${surprise:.4f}", delta_color=delta_color)
            except:
                st.metric("EPS Surprise", surprise)
        else:
            st.metric("EPS Surprise", "N/A")

    with col4:
        surprise_pct = eps_data.get('surprise_pct', 'N/A')
        st.metric("Surprise %", f"{surprise_pct}%" if surprise_pct != 'N/A' else "N/A")


def display_company_header(overview: dict):
    """Display company header with basic info."""
    st.subheader(f"{overview.get('Name', 'N/A')} ({overview.get('Symbol', 'N/A')})")
    st.write(f"**Sector:** {overview.get('Sector', 'N/A')}")
    st.write(f"**Industry:** {overview.get('Industry', 'N/A')}")
    st.write(f"**Market Cap:** {overview.get('MarketCapitalization', 'N/A')}")


def display_key_metrics(overview: dict):
    """Display key financial metrics."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("P/E Ratio", overview.get('PERatio', 'N/A'))
    with col2:
        st.metric("EPS", overview.get('EPS', 'N/A'))
    with col3:
        st.metric("Dividend Yield", overview.get('DividendYield', 'N/A'))