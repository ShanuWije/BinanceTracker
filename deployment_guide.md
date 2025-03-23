# Cryptocurrency Volume Tracker - Deployment Guide

This guide will help you deploy the Cryptocurrency Volume Tracker app to a VPS (Virtual Private Server).

## Required Dependencies

Make sure to install these packages on your VPS:
```
streamlit==1.31.0  # Or latest version
pandas==2.1.4      # Or latest version
numpy==1.26.3      # Or latest version
plotly==5.18.0     # Or latest version
requests==2.31.0   # Or latest version
```

## Deployment Steps

### 1. Set Up Your VPS

1. Connect to your VPS via SSH:
   ```
   ssh username@your-vps-ip
   ```

2. Update your system:
   ```
   sudo apt update && sudo apt upgrade -y
   ```

3. Install Python and pip if not already installed:
   ```
   sudo apt install python3 python3-pip python3-venv -y
   ```

### 2. Clone Your Repository

1. Install Git if not already installed:
   ```
   sudo apt install git -y
   ```

2. Clone your repository:
   ```
   git clone https://your-repository-url.git
   cd your-repository-name
   ```

   Or alternatively, create a new directory and upload your files via SFTP/SCP.

### 3. Set Up a Virtual Environment

1. Create a virtual environment:
   ```
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install streamlit pandas numpy plotly requests
   ```

### 4. Configure Streamlit

1. Make sure your `.streamlit/config.toml` file has the proper server settings:
   ```toml
   [server]
   headless = true
   address = "0.0.0.0"
   port = 5000
   ```

### 5. Start the Application

1. For a quick test, run:
   ```
   streamlit run app.py --server.port 5000
   ```

2. For production deployment, use a process manager like systemd or Supervisor:

   Example systemd service file (`/etc/systemd/system/streamlit-crypto.service`):
   ```
   [Unit]
   Description=Streamlit Crypto Tracker
   After=network.target

   [Service]
   User=your-username
   WorkingDirectory=/path/to/your/app
   ExecStart=/path/to/your/app/venv/bin/streamlit run app.py --server.port 5000
   Restart=on-failure
   RestartSec=5s

   [Install]
   WantedBy=multi-user.target
   ```

3. Start and enable the service:
   ```
   sudo systemctl daemon-reload
   sudo systemctl start streamlit-crypto
   sudo systemctl enable streamlit-crypto
   ```

### 6. Configure Firewall (if needed)

1. Allow the Streamlit port:
   ```
   sudo ufw allow 5000
   ```

### 7. Set Up a Reverse Proxy (Optional but Recommended)

For a more secure and professional setup, consider using Nginx as a reverse proxy:

1. Install Nginx:
   ```
   sudo apt install nginx -y
   ```

2. Create a Nginx configuration file:
   ```
   sudo nano /etc/nginx/sites-available/streamlit-crypto
   ```

3. Add the following configuration:
   ```
   server {
       listen 80;
       server_name your-domain.com;  # Replace with your domain or server IP

       location / {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

4. Enable the site:
   ```
   sudo ln -s /etc/nginx/sites-available/streamlit-crypto /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. Set up SSL with Certbot for HTTPS (optional but recommended):
   ```
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

## Maintenance Tips

1. To update your application:
   ```
   cd /path/to/your/app
   git pull  # If using git
   sudo systemctl restart streamlit-crypto
   ```

2. View application logs:
   ```
   sudo journalctl -u streamlit-crypto
   ```

3. Monitor system resources:
   ```
   htop
   ```

## Troubleshooting

1. If the app isn't accessible, check:
   - Firewall settings
   - Service status: `sudo systemctl status streamlit-crypto`
   - Logs: `sudo journalctl -u streamlit-crypto`
   - Nginx configuration (if using)

2. If you see dependency errors, activate your virtual environment and install any missing packages:
   ```
   source venv/bin/activate
   pip install missing-package
   ```