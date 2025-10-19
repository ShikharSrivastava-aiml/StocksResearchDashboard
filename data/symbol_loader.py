"""
Symbol Database Loader
Loads and manages stock symbols from CSV
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import List


@st.cache_data
def load_symbols_database(csv_path: str = "symbols_valid_meta.csv") -> pd.DataFrame:
    """
    Load symbols from CSV file.
    Cached to improve performance.
    """
    try:
        csv_file = Path(csv_path)
        if not csv_file.exists():
            st.warning(f"⚠️ {csv_path} not found. Using limited symbol suggestions.")
            return pd.DataFrame()

        df = pd.read_csv(csv_file)

        # Ensure required columns exist
        if 'Symbol' not in df.columns:
            st.error("❌ CSV file must contain 'Symbol' column")
            return pd.DataFrame()

        # Create a combined search field
        if 'Security Name' in df.columns:
            df['SearchText'] = df['Symbol'] + ' - ' + df['Security Name']
        else:
            df['SearchText'] = df['Symbol']

        return df

    except Exception as e:
        st.error(f"Error loading symbols database: {e}")
        return pd.DataFrame()


def get_stock_suggestions(symbols_df: pd.DataFrame,
                          input_text: str,
                          limit: int = 10) -> List[str]:
    """Get stock symbol suggestions based on user input."""
    if not input_text or symbols_df.empty:
        return []

    input_text = input_text.upper()
    suggestions = []

    if 'Symbol' in symbols_df.columns:
        # Exact match first
        exact_match = symbols_df[symbols_df['Symbol'] == input_text]
        if not exact_match.empty:
            for _, row in exact_match.iterrows():
                suggestions.append(row['SearchText'])

        # Partial matches
        if len(suggestions) < limit:
            partial_match = symbols_df[
                (symbols_df['Symbol'].str.contains(input_text, na=False, case=False)) |
                (symbols_df['SearchText'].str.upper().str.contains(input_text, na=False))
                ]

            for _, row in partial_match.head(limit - len(suggestions)).iterrows():
                search_text = row['SearchText']
                if search_text not in suggestions:
                    suggestions.append(search_text)

    return suggestions[:limit]