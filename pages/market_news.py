"""
Market News and Sentiment Page
Display market news with sentiment analysis
"""

import streamlit as st
import pandas as pd
import json
import os
import requests  # NEW – to call the microservice
from components.stock_input import stock_input_with_suggestions
from utils.helpers import get_sentiment_color
from utils.service_discovery import get_service_url

SERVICE_NAME = "Market_News_Service"


def render(symbols_df: pd.DataFrame):
    """Render Market News and Sentiment page."""
    st.title("📰 Market News and Sentiment")

    col1, col2 = st.columns([1, 2])

    with col1:
        render_news_settings(symbols_df)

    with col2:
        render_news_feed()


def render_news_settings(symbols_df: pd.DataFrame):
    """Render news settings panel."""
    st.subheader("News Settings")

    # Option to search by topic or specific ticker
    search_type = st.radio("Search by:", ["Topic", "Specific Stock"])

    if search_type == "Topic":
        topics = st.selectbox("Select Topic", [
            "technology", "earnings", "ipo", "mergers_and_acquisitions",
            "financial_markets", "economy_fiscal", "economy_monetary",
            "economy_macro", "energy_transportation", "finance", "life_sciences",
            "manufacturing", "real_estate", "retail_wholesale"
        ])
        ticker_symbol = None
    else:
        ticker_symbol = stock_input_with_suggestions(
            "Enter Stock Symbol",
            "news_symbol",
            symbols_df
        )
        topics = None

    sort_by = st.selectbox("Sort By", ["LATEST", "EARLIEST", "RELEVANCE"])
    limit = st.slider("Number of articles", 5, 50, 20)

    if st.button("📡 Fetch News", use_container_width=True):
        with st.spinner("Fetching news."):

            # Build query params for the microservice
            if search_type == "Topic":
                params = {
                    "mode": "topic",
                    "topic": topics,
                    "sort": sort_by,
                    "limit": limit,
                }
            else:
                if not ticker_symbol:
                    st.warning("Please enter a stock symbol")
                    return

                params = {
                    "mode": "ticker",
                    "ticker": ticker_symbol,
                    "sort": sort_by,
                    "limit": limit,
                }

            try:
                service_url = get_service_url(SERVICE_NAME)
                res = requests.get(f"{service_url}/news", params=params)

                if res.status_code == 200:
                    payload = res.json()
                    # 'news' field contains the raw Alpha Vantage-style response
                    st.session_state['news_data'] = payload['news']
                    st.success("✅ News loaded successfully")
                elif res.status_code == 404:
                    st.warning("No news articles found for this query.")
                else:
                    st.error(f"Error from news service: {res.status_code} - {res.text}")

            except Exception as e:
                st.error(f"Error contacting news service: {e}")


def render_news_feed():
    """Render news articles feed."""
    if 'news_data' not in st.session_state:
        st.info("Configure settings and click 'Fetch News' to get started.")
        return

    news_data = st.session_state['news_data']

    if 'feed' not in news_data or not news_data['feed']:
        st.warning("No news articles found.")
        return

    st.subheader(f"Latest News ({len(news_data['feed'])} articles)")

    # Overall sentiment summary
    sentiments = []
    for article in news_data['feed']:
        try:
            sentiment_score = float(article.get('overall_sentiment_score', 0))
            sentiments.append(sentiment_score)
        except:
            pass

    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
        from utils.helpers import get_sentiment_label
        sentiment_label = get_sentiment_label(avg_sentiment)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Sentiment", sentiment_label)
        with col2:
            st.metric("Average Score", f"{avg_sentiment:.3f}")
        with col3:
            positive_count = sum(1 for s in sentiments if s > 0.1)
            st.metric("Positive Articles", f"{positive_count}/{len(sentiments)}")

    # Sentiment filter
    sentiment_filter = st.selectbox("Filter by sentiment:", [
        "All", "Positive (>0.1)", "Negative (<-0.1)", "Neutral"
    ])

    # Filter articles
    filtered_articles = news_data['feed']
    if sentiment_filter == "Positive (>0.1)":
        filtered_articles = [a for a in news_data['feed']
                             if float(a.get('overall_sentiment_score', 0)) > 0.1]
    elif sentiment_filter == "Negative (<-0.1)":
        filtered_articles = [a for a in news_data['feed']
                             if float(a.get('overall_sentiment_score', 0)) < -0.1]
    elif sentiment_filter == "Neutral":
        filtered_articles = [a for a in news_data['feed']
                             if -0.1 <= float(a.get('overall_sentiment_score', 0)) <= 0.1]

    st.info(f"Showing {len(filtered_articles)} of {len(news_data['feed'])} articles")

    # Display articles
    for article in filtered_articles:
        render_news_article(article)


def render_news_article(article: dict):
    """Render a single news article."""
    with st.expander(f"📄 {article.get('title', 'No Title')}"):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"**Source:** {article.get('source', 'Unknown')}")

            # Format time published
            time_pub = article.get('time_published', 'Unknown')
            if len(time_pub) == 15:
                formatted_time = f"{time_pub[0:4]}-{time_pub[4:6]}-{time_pub[6:8]} {time_pub[9:11]}:{time_pub[11:13]}"
                st.write(f"**Published:** {formatted_time}")
            else:
                st.write(f"**Published:** {time_pub}")

            st.write(article.get('summary', 'No summary available'))

            if article.get('url'):
                st.markdown(f"[Read Full Article]({article['url']})")

        with col2:
            # Sentiment analysis
            sentiment_score = article.get('overall_sentiment_score', 0)
            sentiment_label = article.get('overall_sentiment_label', 'Neutral')

            color = get_sentiment_color(sentiment_score)

            st.markdown(
                f"**Sentiment:** <span style='color:{color}'>{sentiment_label}</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"**Score:** {sentiment_score}")

            # Ticker mentions
            if 'ticker_sentiment' in article and article['ticker_sentiment']:
                st.write("**Mentioned Stocks:**")
                for ticker in article['ticker_sentiment'][:5]:
                    ticker_symbol = ticker.get('ticker', 'N/A')
                    ticker_sentiment = ticker.get('ticker_sentiment_label', 'N/A')
                    ticker_relevance = ticker.get('relevance_score', 'N/A')
                    st.write(f"• {ticker_symbol} - {ticker_sentiment} ({ticker_relevance})")
