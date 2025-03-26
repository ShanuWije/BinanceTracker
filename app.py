import streamlit as st
import pandas as pd
import plotly.express as px
import time
import logging
from datetime import datetime
from data_processing import DataProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Binance High Volume Coins",
    page_icon="📈",
    layout="wide"
)

# App title and description
st.title("📊 Binance US High Volume Cryptocurrencies")
st.markdown("""
This app displays real-time data for the highest volume cryptocurrencies on Binance US spot market.
Data is automatically refreshed every minute.
""")

# Sidebar for filters
st.sidebar.header("Filters")

# Tab selector
view_mode = st.sidebar.radio(
    "Select View:",
    options=["Top Volume", "High Volume Movers"],
    index=0
)

# Time period selector - only show for Top Volume view
if view_mode == "Top Volume":
    period = st.sidebar.radio(
        "Select Time Period:",
        options=["24h", "7d"],
        index=0
    )
else:
    period = "24h"  # Default for High Volume Movers

# Number of coins to display
num_coins = st.sidebar.slider(
    "Number of coins to display:",
    min_value=5,
    max_value=50,
    value=20,
    step=5
)

# Function to load data
@st.cache_data(ttl=60)  # Cache data for 60 seconds
def load_data(period, limit, view_mode):
    try:
        if view_mode == "Top Volume":
            df = DataProcessor.get_top_volume_coins(period=period, limit=limit)
        else:  # High Volume Movers
            df = DataProcessor.get_high_volume_change_coins(min_volume=100000000.0, limit=limit)
        return df, None
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return pd.DataFrame(), str(e)

# Main app container
main_container = st.container()

# Function to display data
def display_data():
    with main_container:
        # Show a spinner while loading data
        with st.spinner("Fetching latest data from Binance US..."):
            df, error = load_data(period, num_coins, view_mode)
        
        # Display last updated time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.text(f"Last updated: {current_time}")
        
        # Check if we have data
        if error:
            st.error(f"Failed to fetch data: {error}")
            return
            
        if df.empty:
            st.warning("No data available. Please try again later.")
            return
        
        # Display data in two columns
        col1, col2 = st.columns([3, 2])
        
        with col1:
            if view_mode == "Top Volume":
                st.subheader(f"Top {len(df)} Coins by Volume ({period})")
            else:
                st.subheader(f"Top {len(df)} High Volume Movers (>100M USDT)")
            
            # Format and display the table
            display_df = df.copy()
            
            # Add styling for price change
            if 'Change 24h (%)' in display_df.columns:
                display_df['Change 24h (%)'] = display_df['Change 24h (%)'].apply(
                    lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"
                )
            elif 'Change 7d (%)' in display_df.columns:
                display_df['Change 7d (%)'] = display_df['Change 7d (%)'].apply(
                    lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"
                )
            
            # Format price with appropriate precision
            if 'Price (USDT)' in display_df.columns:
                display_df['Price (USDT)'] = display_df['Price (USDT)'].apply(
                    lambda x: f"{float(x):.8f}" if float(x) < 0.1 else f"{float(x):.2f}"
                )
            
            # Format volume columns
            for col in display_df.columns:
                if 'Volume' in col and 'USDT' in col:
                    display_df[col] = display_df[col].apply(
                        lambda x: f"{int(x):,}" if pd.notnull(x) else "N/A"
                    )
            
            # Display the table
            st.dataframe(
                display_df.set_index('Coin'),
                use_container_width=True,
                height=600
            )
        
        with col2:
            if view_mode == "Top Volume":
                st.subheader("Volume Comparison")
                chart_title = f"Top 10 Coins by Volume ({period})"
                y_axis_title = "Volume (USDT)"
            else:
                st.subheader("Price Change Comparison")
                chart_title = "Top 10 High Volume Movers (>100M USDT)"
                y_axis_title = "Price Change (%)"
            
            # Prepare data for the chart
            chart_df = df.copy().head(10)  # Top 10 for chart
            volume_col = 'Volume (USDT)' if 'Volume (USDT)' in chart_df.columns else 'Volume 7d (USDT)'
            change_col = 'Change 24h (%)' if 'Change 24h (%)' in chart_df.columns else 'Change 7d (%)'
            
            # First chart - either volume or price change depending on view
            if view_mode == "Top Volume":
                # Create volume bar chart
                fig1 = px.bar(
                    chart_df,
                    x='Coin',
                    y=volume_col,
                    title=chart_title,
                    color=change_col,
                    color_continuous_scale=['red', 'lightgrey', 'green'],
                    color_continuous_midpoint=0
                )
                fig1.update_layout(
                    xaxis_title="Coin",
                    yaxis_title=y_axis_title,
                    coloraxis_colorbar_title="Price Change (%)"
                )
            else:
                # Create price change bar chart for high volume movers
                fig1 = px.bar(
                    chart_df,
                    x='Coin',
                    y=change_col,
                    title=chart_title,
                    color=change_col,
                    color_continuous_scale=['red', 'lightgrey', 'green'],
                    color_continuous_midpoint=0
                )
                fig1.update_layout(
                    xaxis_title="Coin",
                    yaxis_title=y_axis_title
                )
            
            st.plotly_chart(fig1, use_container_width=True)
            
            # Second chart - either price change or volume depending on view
            if view_mode == "Top Volume":
                # Create price change comparison chart
                fig2 = px.bar(
                    chart_df,
                    x='Coin',
                    y=change_col,
                    title=f"Price Change ({period})",
                    color=change_col,
                    color_continuous_scale=['red', 'lightgrey', 'green'],
                    color_continuous_midpoint=0
                )
                fig2.update_layout(
                    xaxis_title="Coin",
                    yaxis_title="Price Change (%)"
                )
            else:
                # Create volume comparison chart for high volume movers
                fig2 = px.bar(
                    chart_df,
                    x='Coin',
                    y=volume_col,
                    title="Volume Comparison",
                    color=change_col,
                    color_continuous_scale=['red', 'lightgrey', 'green'],
                    color_continuous_midpoint=0
                )
                fig2.update_layout(
                    xaxis_title="Coin",
                    yaxis_title="Volume (USDT)",
                    coloraxis_colorbar_title="Price Change (%)"
                )
            
            st.plotly_chart(fig2, use_container_width=True)

# Initial data display
display_data()

# Auto-refresh functionality
auto_refresh = st.sidebar.checkbox("Auto-refresh (every 60 seconds)", value=True)

if auto_refresh:
    refresh_interval = 60  # seconds
    
    # Create a placeholder for the countdown
    countdown_placeholder = st.sidebar.empty()
    
    # Main app loop for auto-refresh
    if not st.session_state.get('first_run', False):
        st.session_state['first_run'] = True
    else:
        # Start countdown
        for remaining in range(refresh_interval, 0, -1):
            countdown_placeholder.text(f"Refreshing in {remaining} seconds...")
            time.sleep(1)
        
        # Clear cache and refresh data
        st.cache_data.clear()
        countdown_placeholder.empty()
        st.rerun()
else:
    # Manual refresh button
    if st.sidebar.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Add some information in the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
### About
This app displays cryptocurrencies with the highest trading volume on Binance US spot market.

#### Views:
- **Top Volume**: Shows coins with highest trading volume
- **High Volume Movers**: Shows coins with highest price change % that have >100M USDT in 24h volume

#### Time Periods (for Top Volume view):
- **24h**: Shows data for the last 24 hours
- **7d**: Shows data for the last 7 days

Data is fetched directly from the Binance US API.
""")
