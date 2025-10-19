"""
General Helper Functions
Utility functions used across the application
"""

from datetime import datetime
from typing import Optional

def format_currency(value: float, decimals: int = 2) -> str:
    """Format number as currency."""
    return f"${value:,.{decimals}f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format number as percentage."""
    return f"{value:.{decimals}f}%"

def format_large_number(value: float) -> str:
    """Format large numbers with K, M, B suffixes."""
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.2f}K"
    else:
        return f"${value:.2f}"


def infer_quarter(date_str: str) -> str:
    """Infer quarter (Q1-Q4) from fiscal date ending."""
    if not date_str or len(date_str) < 7:
        return "Q?"

    try:
        month = int(date_str[5:7])
        if month <= 3:
            return "Q1"
        elif month <= 6:
            return "Q2"
        elif month <= 9:
            return "Q3"
        else:
            return "Q4"
    except:
        return "Q?"


def format_date(date_str: str, format_out: str = '%Y-%m-%d') -> str:
    """Format ISO date string to desired format."""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime(format_out)
    except:
        return date_str


def get_sentiment_color(sentiment_score: float) -> str:
    """Get color based on sentiment score."""
    try:
        score = float(sentiment_score)
        if score > 0.2:
            return "green"
        elif score < -0.2:
            return "red"
        else:
            return "gray"
    except:
        return "gray"


def get_sentiment_emoji(sentiment_score: float) -> str:
    """Get emoji based on sentiment score."""
    try:
        score = float(sentiment_score)
        if score > 0.2:
            return "😊"
        elif score < -0.2:
            return "😟"
        else:
            return "😐"
    except:
        return "😐"


def get_sentiment_label(sentiment_score: float) -> str:
    """Get text label based on sentiment score."""
    try:
        score = float(sentiment_score)
        if score > 0.2:
            return "Positive 📈"
        elif score < -0.2:
            return "Negative 📉"
        else:
            return "Neutral ➡️"
    except:
        return "Neutral ➡️"