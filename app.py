"""
StockAnalysisDashboard - Main Application
Multi-page Streamlit application with user authentication
"""

import streamlit as st
from auth.authentication import check_authentication, show_login_page
from components.sidebar import render_sidebar
from pages import stock_analysis, portfolio_manager, market_news, earnings_viewer
from data.symbol_loader import load_symbols_database
from utils.service_discovery import get_available_services,deregister_service

# Page configuration
st.set_page_config(
    page_title="StockAnalysisDashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit's default navigation (the "app" button)
hide_streamlit_style = """
    <style>
    /* Hide the top-right menu and navigation */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hide the page navigation if using multi-page */
    [data-testid="stSidebarNav"] {display: none;}

    /* Optional: Adjust sidebar spacing */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None

# Load symbols database (cached)
SYMBOLS_DF = load_symbols_database()

# Authentication check
if not check_authentication():
    show_login_page()
    st.stop()

# Main application (user is logged in)
st.sidebar.title(f"👤 Welcome, {st.session_state['username']}")

# Fetch available services from the service registry
available_services = get_available_services()
service_names = available_services.keys()  # Assuming the service names are keys in the returned dictionary

# Render sidebar dynamically
page = st.sidebar.selectbox("Choose a Service", list(service_names))

# Route to appropriate page
if page == "Stock Analysis Service":
    stock_analysis.render( SYMBOLS_DF)
elif page == "Portfolio Service":
    portfolio_manager.render(SYMBOLS_DF)
elif page == "Market News Service":
    market_news.render( SYMBOLS_DF)
elif page == "Earnings Service":
    earnings_viewer.render(SYMBOLS_DF)

# Remove service functionality (for demonstration)
# st.sidebar.subheader("Service Management")

# Option to remove a service from the registry
# service_to_remove = st.sidebar.selectbox("Select Service to Remove from Service Registry", [""] + list(service_names))  # List of services
# if service_to_remove:
#     remove_button = st.sidebar.button(f"Remove {service_to_remove}")
#     if remove_button:
#         # Call the deregister function to remove the selected service from the registry
#         deregister_service(service_to_remove)
#         st.success(f"Service {service_to_remove} removed from the registry.")