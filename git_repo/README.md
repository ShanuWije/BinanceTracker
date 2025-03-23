# Cryptocurrency Volume Tracker

A Python-based Streamlit application that displays high-volume cryptocurrencies from Binance US with real-time market updates and interactive visualizations.

## Features

- Real-time data from Binance US API
- View top cryptocurrencies by trading volume
- Filter by time period (24h or 7d)
- Interactive visualizations with Plotly
- Auto-refresh functionality to keep data current

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Pip package manager

### Local Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd cryptocurrency-volume-tracker
   ```

2. Install the required dependencies:
   ```
   pip install streamlit pandas numpy plotly requests
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

The application will be available at http://localhost:8501

## Deployment

This application can be deployed to a VPS (Virtual Private Server) using various methods:

### Traditional Deployment

Follow the instructions in `deployment_guide.md` for a traditional setup using:
- Python virtual environment
- Systemd service
- Nginx reverse proxy (optional)

### Docker Deployment

Follow the instructions in `docker_deployment_guide.md` for a Docker-based deployment using:
- Docker
- Docker Compose
- Nginx reverse proxy (optional)
- HTTPS with Let's Encrypt (optional)

## Project Structure

- `app.py`: Main Streamlit application file
- `binance_api.py`: Functions for interacting with the Binance US API
- `data_processing.py`: Data processing and transformation functions
- `.streamlit/config.toml`: Streamlit configuration file
- `deploy.sh`: Deployment script for traditional setup
- `Dockerfile`: Docker configuration file
- `docker-compose.yml`: Docker Compose configuration file

## Auto-Refresh Functionality

The application features an auto-refresh function that updates the data at regular intervals:

1. Enable auto-refresh using the toggle in the sidebar
2. Set the refresh interval (in seconds)
3. The application will automatically fetch new data at the specified interval

## Data Source

This application uses the public Binance US API to fetch cryptocurrency market data:
- 24-hour ticker data for all trading pairs
- Weekly historical data for selected pairs

No API keys are required as the application uses only publicly available endpoints.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.