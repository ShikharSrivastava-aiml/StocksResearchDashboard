"""
Custom CSS Styles
"""


def get_custom_css():
    """Return custom CSS to hide Streamlit elements and improve styling."""
    return """
    <style>
    /* Hide Streamlit branding and navigation */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hide the multi-page navigation */
    [data-testid="stSidebarNav"] {display: none;}

    /* Adjust sidebar spacing */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #1e1e1e;
    }

    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

    /* Improve button styling */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Improve metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: bold;
    }

    /* Improve expander styling */
    .streamlit-expanderHeader {
        font-weight: bold;
        font-size: 1.1rem;
    }
    </style>
    """