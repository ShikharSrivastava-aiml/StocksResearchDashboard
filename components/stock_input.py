"""
Stock Input Component
Reusable stock symbol input with suggestions
"""

import streamlit as st
import pandas as pd
from data.symbol_loader import get_stock_suggestions

def stock_input_with_suggestions(label: str,
                                 key: str,
                                 symbols_df: pd.DataFrame,
                                 default_value: str = "") -> str:
    """
    Create a stock input field with dynamic suggestions.

    Args:
        label: Input field label
        key: Unique key for the input
        symbols_df: DataFrame containing symbol data
        default_value: Default value for input

    Returns:
        User input (uppercase)
    """
    # Use a different key for the text input widget
    input_key = f"{key}_input"

    # Get the value from session state if it exists
    if key in st.session_state and key != input_key:
        default_value = st.session_state[key]

    user_input = st.text_input(
        label,
        value=default_value,
        key=input_key,
        placeholder="Type symbol or company name..."
    ).upper()

    # Show suggestions as user types
    if user_input and len(user_input) >= 1:
        suggestions = get_stock_suggestions(symbols_df, user_input, limit=10)

        if suggestions:
            st.write("**💡 Suggestions:**")

            # Display suggestions in columns
            num_cols = min(2, len(suggestions))
            cols = st.columns(num_cols)

            for i, suggestion in enumerate(suggestions[:10]):
                with cols[i % num_cols]:
                    symbol = suggestion.split(' - ')[0]
                    # Use a unique button key that includes the suggestion index
                    button_key = f"suggest_{key}_{symbol}_{i}"
                    if st.button(
                        suggestion,
                        key=button_key,
                        use_container_width=True
                    ):
                        # Store the selected symbol in a separate session state key
                        st.session_state[f"{key}_selected"] = symbol
                        st.rerun()

    # Check if a suggestion was selected
    if f"{key}_selected" in st.session_state:
        selected = st.session_state[f"{key}_selected"]
        # Clear the selection flag
        del st.session_state[f"{key}_selected"]
        return selected

    return user_input