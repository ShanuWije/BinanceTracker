#!/bin/bash

# Cryptocurrency Volume Tracker - Deployment Script
# This script automates the setup process for deploying the app to a VPS

echo "Setting up Cryptocurrency Volume Tracker..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required system dependencies..."
sudo apt install python3 python3-pip python3-venv nginx -y

# Create virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install streamlit pandas numpy plotly requests

# Create systemd service file
echo "Creating systemd service file..."
cat > streamlit-crypto.service << EOL
[Unit]
Description=Streamlit Crypto Tracker
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/streamlit run app.py --server.port 5000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOL

# Move service file to systemd directory
echo "Installing systemd service..."
sudo mv streamlit-crypto.service /etc/systemd/system/

# Create Nginx configuration
echo "Creating Nginx configuration..."
cat > streamlit-crypto << EOL
server {
    listen 80;
    server_name \$host;  # Will use the server's IP address or domain if configured

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOL

# Move Nginx config to appropriate directory
sudo mv streamlit-crypto /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/streamlit-crypto /etc/nginx/sites-enabled

# Test Nginx configuration
echo "Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    # Restart Nginx
    echo "Restarting Nginx..."
    sudo systemctl restart nginx

    # Start and enable Streamlit service
    echo "Starting Streamlit service..."
    sudo systemctl daemon-reload
    sudo systemctl start streamlit-crypto
    sudo systemctl enable streamlit-crypto

    # Configure firewall if ufw is active
    if command -v ufw &> /dev/null && sudo ufw status | grep -q "active"; then
        echo "Configuring firewall..."
        sudo ufw allow 80
        sudo ufw allow 5000
    fi

    echo "--------------------------------------"
    echo "Deployment completed successfully!"
    echo "Your app should be accessible at:"
    echo "http://$(curl -s ifconfig.me)"
    echo "--------------------------------------"
    echo "To check service status: sudo systemctl status streamlit-crypto"
    echo "To view logs: sudo journalctl -u streamlit-crypto"
else
    echo "Nginx configuration test failed. Please check the configuration."
fi