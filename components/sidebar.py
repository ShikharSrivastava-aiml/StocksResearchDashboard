"""
Sidebar Components
Shared sidebar elements across all pages
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from auth.authentication import logout
from models.user import User
from data.symbol_loader import get_stock_suggestions

def render_sidebar(symbols_df: pd.DataFrame) -> str:
    """
    Render sidebar with navigation and common elements.

    Returns:
        Selected page name
    """
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.title("📈 StockAnalysisDashboard")

    # Navigation
    page = st.sidebar.selectbox("Choose a service:", [
        "Stock Analysis Report",
        "Portfolio Manager",
        "Market News and Sentiment",
        "Earnings Call Viewer"
    ])

    # Quick stock lookup
    render_quick_lookup(symbols_df, page)

    # User account info
    render_account_info()

    # Database statistics
    render_database_stats(symbols_df)

    # Footer
    render_footer()

    return page


def render_quick_lookup(symbols_df: pd.DataFrame, current_page: str):
    """Render quick stock lookup section."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Quick Stock Lookup")

    # Initialize quick search state
    if "quick_search_value" not in st.session_state:
        st.session_state["quick_search_value"] = ""

    quick_symbol = st.sidebar.text_input(
        "Quick Symbol Search:",
        value=st.session_state["quick_search_value"],
        key="quick_search_input",
        placeholder="Type symbol..."
    ).upper()

    # Update state
    st.session_state["quick_search_value"] = quick_symbol

    if quick_symbol and len(quick_symbol) >= 1:
        quick_suggestions = get_stock_suggestions(symbols_df, quick_symbol.upper(), limit=5)

        if quick_suggestions:
            st.sidebar.write("**Suggestions:**")
            for i, suggestion in enumerate(quick_suggestions):
                symbol_only = suggestion.split(' - ')[0]
                company_name = suggestion.split(' - ')[1] if ' - ' in suggestion else symbol_only

                if st.sidebar.button(
                        f"➤ {symbol_only}",
                        key=f"quick_btn_{symbol_only}_{i}",
                        help=company_name
                ):
                    # Set the symbol for the current page using state_key pattern
                    if current_page == "Stock Analysis Report":
                        st.session_state["analysis_symbol_value"] = symbol_only
                    elif current_page == "Portfolio Manager":
                        st.session_state["portfolio_symbol_value"] = symbol_only
                    elif current_page == "Earnings Call Viewer":
                        st.session_state["earnings_symbol_value"] = symbol_only

                    # Clear quick search
                    st.session_state["quick_search_value"] = ""
                    st.rerun()
def render_account_info():
    """Render user account information."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Account Info")

    username = st.session_state.get('username')
    if username:
        user = User(username)
        user_data = user.get_data()

        created_date = user.get_created_at()
        if created_date != 'Unknown':
            try:
                created_datetime = datetime.fromisoformat(created_date)
                created_str = created_datetime.strftime('%Y-%m-%d')
            except:
                created_str = created_date
        else:
            created_str = 'Unknown'

        portfolio_count = len(user_data.get('portfolio', []))

        st.sidebar.info(f"""
        **Username:** {username}  
        **Member Since:** {created_str}  
        **Portfolio Items:** {portfolio_count}
        """)

def render_database_stats(symbols_df: pd.DataFrame):
    """Render database statistics."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Database Stats")

    if not symbols_df.empty:
        st.sidebar.success(f"✅ {len(symbols_df)} symbols loaded")

        # Show sample of available symbols
        if st.sidebar.checkbox("Show sample symbols"):
            sample = symbols_df.head(10)
            if 'Symbol' in sample.columns:
                for _, row in sample.iterrows():
                    st.sidebar.text(row['SearchText'] if 'SearchText' in row else row['Symbol'])
    else:
        st.sidebar.warning("⚠️ Symbol database not loaded")

def render_footer():
    """Render sidebar footer."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("📈 **StockAnalysisDashboard**")
    st.sidebar.markdown("Powered by Alpha Vantage API")

    # API info
    try:
        from data.api_client import APIClient
        # Try to create client to check if API key is valid
        APIClient()
        st.sidebar.markdown("API Key: ✅ Connected")
    except:
        st.sidebar.markdown("API Key: ❌ Missing")

    # Help and rate limits
    with st.sidebar.expander("ℹ️ Help & Rate Limits"):
        st.info("""
        **API Rate Limits:**
        - Free: 25 requests/day
        - Premium: 75+ requests/minute
        
        **Tips:**
        - Use quarter loading to preview data
        - Your portfolio is auto-saved
        - Use filters to reduce API calls
        
        **Navigation:**
        - Use quick lookup to jump to stocks
        - Portfolio is saved automatically
        - Search across 1000+ symbols
        """)

    # Account settings
    render_account_settings()

def render_account_settings():
    """Render account settings section."""
    st.sidebar.markdown("---")

    if st.sidebar.button("⚙️ Account Settings", use_container_width=True):
        st.session_state['show_settings'] = not st.session_state.get('show_settings', False)

    if st.session_state.get('show_settings', False):
        with st.sidebar.expander("Account Management", expanded=True):
            st.write("**Change Password**")
            new_password = st.text_input("New Password", type="password", key="new_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pass")

            if st.button("Update Password", key="update_pass_btn"):
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            from auth.authentication import hash_password, load_users, save_users
                            users = load_users()
                            users[st.session_state['username']]['password'] = hash_password(new_password)
                            save_users(users)
                            st.success("Password updated successfully!")
                        else:
                            st.error("Password must be at least 6 characters")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.warning("Please fill in both fields")

            st.markdown("---")
            st.write("**Export Portfolio Data**")
            if st.button("📥 Export Portfolio", key="export_port_btn"):
                import json
                from models.portfolio import Portfolio
                portfolio = Portfolio(st.session_state['username'])
                portfolio_data = {
                    'username': st.session_state['username'],
                    'exported_at': datetime.now().isoformat(),
                    'portfolio': portfolio.get_all()
                }
                st.download_button(
                    label="Download Portfolio",
                    data=json.dumps(portfolio_data, indent=2),
                    file_name=f"portfolio_{st.session_state['username']}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    key="download_port_btn"
                )