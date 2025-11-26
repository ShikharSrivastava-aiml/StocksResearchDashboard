"""
Earnings Call Viewer Page
View and analyze earnings call transcripts
"""

import streamlit as st
import pandas as pd
import json
import os
import requests
from components.stock_input import stock_input_with_suggestions
from components.metrics import display_sentiment_metrics, display_eps_metrics
from utils.text_processing import clean_text, split_into_paragraphs, highlight_search_term, extract_longest_sentence
from utils.helpers import infer_quarter, get_sentiment_color, get_sentiment_emoji
from utils.service_discovery import get_service_url


SERVICE_NAME = "Earnings_Service"

def render( symbols_df: pd.DataFrame):
    """Render Earnings Call Viewer page."""
    st.title("💼 Earnings Call Transcript Viewer")

    col1, col2 = st.columns([1, 2])

    with col1:
        render_earnings_selector( symbols_df)

    with col2:
        render_transcript_display()


def render_earnings_selector(symbols_df: pd.DataFrame):
    """Render earnings selection panel."""
    st.subheader("📊 Stock Selection")

    # Stock symbol input with suggestions
    symbol = stock_input_with_suggestions(
        "Enter Stock Symbol",
        "earnings_symbol",
        symbols_df,
        st.session_state.get("earnings_symbol", "")
    )

    # Load available quarters
    if symbol and st.button("📅 Load Available Quarters", use_container_width=True):
        with st.spinner(f"Loading earnings data for {symbol}..."):
            try:
                service_url = get_service_url(SERVICE_NAME)
                res = requests.get(f"{service_url}/earnings/{symbol}")
                if res.status_code == 200:
                    payload = res.json()
                    earnings_data = payload["earnings"]
                    if earnings_data and 'quarterlyEarnings' in earnings_data:
                        process_earnings_data(earnings_data, symbol)
                    else:
                        st.warning("No earnings data found for this symbol")
                elif res.status_code == 404:
                    st.warning("No earnings data found for this symbol")
                else:
                    st.error(f"Error from earnings service: {res.status_code} - {res.text}")
            except Exception as e:
                st.error(f"Error contacting earnings service: {e}")

    # Quarter selection
    selected_quarter = render_quarter_selector()

    # Fetch transcript
    if st.button("🔄 Fetch Transcript", use_container_width=True):
        if symbol and selected_quarter:
            fetch_transcript( symbol, selected_quarter)
        else:
            st.warning("Please select a stock symbol and quarter first.")


def process_earnings_data(earnings_data: dict, symbol: str):
    """Process and store earnings data."""
    quarterly_earnings = earnings_data['quarterlyEarnings']
    available_quarters = []
    earnings_info = {}

    for earning in quarterly_earnings:
        fiscal_date = earning.get('fiscalDateEnding', '')
        if fiscal_date:
            year = fiscal_date[:4]
            quarter = infer_quarter(fiscal_date)
            quarter_key = f"{year}{quarter}"

            eps = earning.get('reportedEPS', 'N/A')
            estimated_eps = earning.get('estimatedEPS', 'N/A')
            surprise = earning.get('surprise', 'N/A')
            surprise_pct = earning.get('surprisePercentage', 'N/A')

            display_text = f"{quarter_key} - EPS: {eps}"
            if surprise != 'N/A' and surprise_pct != 'N/A':
                display_text += f" (Surprise: {surprise}, {surprise_pct}%)"

            available_quarters.append((quarter_key, display_text))
            earnings_info[quarter_key] = {
                'eps': eps,
                'estimated_eps': estimated_eps,
                'surprise': surprise,
                'surprise_pct': surprise_pct,
                'fiscal_date': fiscal_date
            }

    st.session_state['available_quarters'] = available_quarters
    st.session_state['earnings_info'] = earnings_info
    st.session_state['earnings_symbol'] = symbol
    st.success(f"✅ Found {len(available_quarters)} quarters with earnings data")


def render_quarter_selector() -> str:
    """Render quarter selection dropdown and display EPS info."""
    if 'available_quarters' not in st.session_state or not st.session_state['available_quarters']:
        return None

    quarters_display = [q[1] for q in st.session_state['available_quarters']]
    quarters_keys = [q[0] for q in st.session_state['available_quarters']]

    selected_display = st.selectbox(
        "Select Quarter:",
        quarters_display,
        key="quarter_select"
    )

    if selected_display:
        selected_idx = quarters_display.index(selected_display)
        selected_quarter = quarters_keys[selected_idx]

        # Show EPS info for selected quarter
        if selected_quarter in st.session_state.get('earnings_info', {}):
            eps_info = st.session_state['earnings_info'][selected_quarter]

            with st.container():
                st.markdown("**📊 Earnings Details:**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Reported EPS", eps_info['eps'])
                    st.metric("Estimated EPS", eps_info['estimated_eps'])
                with col_b:
                    surprise_val = eps_info['surprise']
                    if surprise_val != 'N/A':
                        try:
                            surprise_float = float(surprise_val)
                            delta_color = "normal" if surprise_float >= 0 else "inverse"
                            st.metric("EPS Surprise", surprise_val, delta_color=delta_color)
                        except:
                            st.metric("EPS Surprise", surprise_val)
                    else:
                        st.metric("EPS Surprise", "N/A")
                    st.metric("Surprise %",
                              f"{eps_info['surprise_pct']}%" if eps_info['surprise_pct'] != 'N/A' else "N/A")

        return selected_quarter

    return None


def fetch_transcript(symbol: str, quarter: str):
    """Fetch earnings call transcript via microservice."""
    st.session_state["transcript_symbol"] = symbol
    st.session_state["transcript_quarter"] = quarter

    with st.spinner(f"Fetching transcript for {symbol} ({quarter})..."):
        try:
            # Call the earnings microservice instead of api_client directly
            service_url = get_service_url(SERVICE_NAME)
            res = requests.get(
                f"{service_url}/earnings/{symbol}/transcript",
                params={"quarter": quarter},
            )

            if res.status_code == 200:
                payload = res.json()
                # Our service returns: {"symbol": ..., "quarter": ..., "transcript": {...}}
                data = payload["transcript"]

                if not data or "transcript" not in data or not data["transcript"]:
                    st.error("⚠️ No transcript data found for this quarter.")
                else:
                    st.session_state["transcript_data"] = data
                    st.success(
                        f"✅ Loaded transcript for {data.get('symbol')} – {data.get('quarter')}"
                    )

            elif res.status_code == 404:
                st.error("⚠️ No transcript found for this symbol/quarter.")

            else:
                st.error(
                    f"🌐 Error from earnings service: {res.status_code} - {res.text}"
                )

        except Exception as e:
            st.error(f"🌐 Error contacting earnings service: {e}")


def render_transcript_display():
    """Render transcript display with filters and search."""
    if "transcript_data" not in st.session_state:
        st.info("Enter a stock symbol and load available quarters to get started.")
        render_help_section()
        return

    data = st.session_state["transcript_data"]
    transcript = data.get("transcript", [])

    if not transcript:
        st.warning("No transcript segments available.")
        return

    # Header with company info and EPS
    render_transcript_header(data, transcript)

    # Search and filter controls
    search_term, sentiment_filter, speaker_filter = render_transcript_controls(transcript)

    # Raw JSON viewer
    with st.expander("📄 Raw JSON Response"):
        st.code(json.dumps(data, indent=2, ensure_ascii=False), language="json")

    st.subheader("📝 Transcript Segments")

    # Apply filters
    filtered_transcript = apply_filters(
        transcript,
        search_term,
        sentiment_filter,
        speaker_filter
    )

    if not filtered_transcript:
        st.warning("No transcript segments match your filters.")
        return

    st.info(f"Showing {len(filtered_transcript)} of {len(transcript)} segments")

    # Export option
    if st.button("📥 Export Filtered Transcript"):
        export_transcript(data, filtered_transcript)

    # Display segments
    for i, entry in enumerate(filtered_transcript):
        render_transcript_segment(entry, i, search_term)


def render_transcript_header(data: dict, transcript: list):
    """Render transcript header with metrics."""
    # Company and quarter info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Company", data.get('symbol', 'N/A'))
    with col2:
        st.metric("Quarter", data.get('quarter', 'N/A'))
    with col3:
        st.metric("Speakers", len(transcript))
    with col4:
        # Show EPS for this quarter if available
        current_quarter = data.get('quarter', '')
        if current_quarter in st.session_state.get('earnings_info', {}):
            eps_data = st.session_state['earnings_info'][current_quarter]
            st.metric("EPS", eps_data['eps'])

    # Sentiment summary
    if transcript:
        sentiments = []
        for entry in transcript:
            try:
                sentiment = float(entry.get("sentiment", 0))
                sentiments.append(sentiment)
            except:
                pass

        if sentiments:
            display_sentiment_metrics(sentiments)

    # EPS Performance Details
    current_quarter = data.get('quarter', '')
    if current_quarter in st.session_state.get('earnings_info', {}):
        eps_data = st.session_state['earnings_info'][current_quarter]
        with st.expander("📊 Earnings Performance Details", expanded=True):
            display_eps_metrics(eps_data)


def render_transcript_controls(transcript: list) -> tuple:
    """Render search and filter controls."""
    # Search
    search_term = st.text_input(
        "🔍 Search in transcript:",
        placeholder="Enter keywords to search..."
    )

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        sentiment_filter = st.selectbox("Filter by sentiment:", [
            "All", "Positive (>0.2)", "Negative (<-0.2)", "Neutral (-0.2 to 0.2)"
        ])

    with col2:
        # Get unique speakers
        speakers = list(set([entry.get("speaker", "Unknown") for entry in transcript]))
        speakers.insert(0, "All Speakers")
        speaker_filter = st.selectbox("Filter by speaker:", speakers)

    return search_term, sentiment_filter, speaker_filter


def apply_filters(transcript: list, search_term: str,
                  sentiment_filter: str, speaker_filter: str) -> list:
    """Apply all filters to transcript."""
    filtered = transcript.copy()

    # Apply sentiment filter
    if sentiment_filter == "Positive (>0.2)":
        filtered = [e for e in filtered if float(e.get("sentiment", 0)) > 0.2]
    elif sentiment_filter == "Negative (<-0.2)":
        filtered = [e for e in filtered if float(e.get("sentiment", 0)) < -0.2]
    elif sentiment_filter == "Neutral (-0.2 to 0.2)":
        filtered = [e for e in filtered if -0.2 <= float(e.get("sentiment", 0)) <= 0.2]

    # Apply speaker filter
    if speaker_filter != "All Speakers":
        filtered = [e for e in filtered if e.get("speaker", "Unknown") == speaker_filter]

    # Apply search filter
    if search_term:
        import re
        search_pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        filtered = [
            e for e in filtered
            if search_pattern.search(e.get("content", "")) or
               search_pattern.search(e.get("speaker", "")) or
               search_pattern.search(e.get("title", ""))
        ]

    return filtered


def render_transcript_segment(entry: dict, index: int, search_term: str):
    """Render a single transcript segment."""
    speaker = entry.get("speaker", "Unknown Speaker")
    title = entry.get("title", "")
    content = clean_text(entry.get("content", ""))
    sentiment = entry.get("sentiment", "N/A")

    # Sentiment indicators
    color = get_sentiment_color(sentiment)
    emoji = get_sentiment_emoji(sentiment)

    # Highlight search terms
    display_content = highlight_search_term(content, search_term) if search_term else content

    with st.expander(f"{emoji} {speaker} – {title or 'No Title'} (Segment {index + 1})"):
        col_left, col_right = st.columns([3, 1])

        with col_left:
            # Display content in paragraphs
            paragraphs = split_into_paragraphs(display_content)
            for p in paragraphs:
                if p:
                    st.write(p)

        with col_right:
            st.markdown(
                f"**Sentiment:** <span style='color:{color}'>{sentiment}</span>",
                unsafe_allow_html=True
            )

            # Word and character count
            word_count = len(content.split())
            st.write(f"**Words:** {word_count}")
            st.write(f"**Characters:** {len(content)}")

            # Key quote
            longest_sentence = extract_longest_sentence(content, max_length=100)
            if longest_sentence:
                st.write(f"**Key Quote:** *{longest_sentence}*")


def export_transcript(data: dict, filtered_transcript: list):
    """Export filtered transcript to text file."""
    export_text = f"Earnings Call Transcript\n"
    export_text += f"Company: {data.get('symbol', 'N/A')}\n"
    export_text += f"Quarter: {data.get('quarter', 'N/A')}\n"
    export_text += f"=" * 80 + "\n\n"

    for entry in filtered_transcript:
        speaker = entry.get("speaker", "Unknown Speaker")
        content = clean_text(entry.get("content", ""))
        sentiment = entry.get("sentiment", "N/A")

        export_text += f"\n{speaker} (Sentiment: {sentiment}):\n"
        export_text += f"{content}\n"
        export_text += f"-" * 80 + "\n"

    st.download_button(
        label="Download as Text",
        data=export_text,
        file_name=f"{data.get('symbol')}_{data.get('quarter')}_transcript.txt",
        mime="text/plain"
    )


def render_help_section():
    """Render help and instructions."""
    with st.expander("ℹ️ How to use the Enhanced Earnings Call Viewer"):
        st.write("""
        **Step-by-Step Guide:**

        1. **Enter Stock Symbol:** Type a stock symbol (suggestions will appear from our database)
        2. **Load Quarters:** Click "Load Available Quarters" to see all quarters with earnings data
        3. **Select Quarter:** Choose from the dropdown which shows:
           - Quarter (e.g., 2024Q3)
           - Reported EPS
           - EPS Surprise and percentage
        4. **Fetch Transcript:** Get the actual earnings call transcript for that quarter

        **Features:**
        - 🎯 **Smart Stock Suggestions:** Get recommendations from comprehensive database
        - 📅 **Dynamic Quarter Selection:** Only see quarters with actual earnings data
        - 📊 **EPS Performance:** View earnings per share, surprises, and performance metrics
        - 🔍 **Advanced Search:** Find specific topics or keywords in transcripts
        - 👤 **Speaker Filter:** Filter by specific speakers in the call
        - 📈 **Sentiment Analysis:** See overall sentiment and filter by positive/negative segments
        - 💡 **Key Insights:** Extract important quotes and track speaker sentiment
        - 📥 **Export:** Download filtered transcripts as text files

        **Popular Stocks with Earnings Data:**
        - **Tech:** AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA
        - **Finance:** JPM, BAC, V, MA, BRK.B
        - **Healthcare:** JNJ, PFE, UNH
        - **Consumer:** KO, WMT, DIS, NKE
        """)