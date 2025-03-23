# Docker Deployment Guide for Cryptocurrency Volume Tracker

This guide explains how to deploy the Cryptocurrency Volume Tracker application using Docker and Docker Compose on a VPS.

## Prerequisites

- A VPS with SSH access
- Docker and Docker Compose installed on your VPS

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

3. Install Docker and Docker Compose if not already installed:
   ```
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Add your user to the Docker group
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo apt install docker-compose -y
   ```

4. Log out and log back in to apply the group changes:
   ```
   exit
   # Then reconnect via SSH
   ```

### 2. Deploy the Application

1. Create a new directory for your application:
   ```
   mkdir crypto-tracker && cd crypto-tracker
   ```

2. Upload the application files to your VPS using SCP or SFTP, or clone from your repository:
   ```
   git clone https://your-repository-url.git .
   ```

3. Start the application with Docker Compose:
   ```
   docker-compose up -d
   ```

   This will:
   - Build the Docker image based on the Dockerfile
   - Start the container in detached mode
   - Map port 5000 from the container to port 5000 on your host

4. Verify the application is running:
   ```
   docker-compose ps
   ```

Your application should now be running and accessible at `http://your-vps-ip:5000`.

### 3. Using Nginx as a Reverse Proxy (Optional)

For a more secure and professional setup, you can use Nginx as a reverse proxy:

1. Create the Nginx configuration directories:
   ```
   mkdir -p nginx/conf.d
   ```

2. Create an Nginx configuration file:
   ```
   nano nginx/conf.d/crypto-tracker.conf
   ```

3. Add the following configuration:
   ```
   server {
       listen 80;
       server_name your-domain.com;  # Replace with your domain or server IP

       location / {
           proxy_pass http://crypto-tracker:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

4. Uncomment the Nginx service in the `docker-compose.yml` file.

5. Restart the services:
   ```
   docker-compose down
   docker-compose up -d
   ```

Your application should now be accessible at `http://your-domain.com` or `http://your-vps-ip`.

### 4. Setting Up HTTPS with Let's Encrypt (Optional)

If you have a domain name pointing to your VPS, you can set up HTTPS:

1. Create directories for Let's Encrypt:
   ```
   mkdir -p nginx/ssl
   ```

2. Update the Nginx configuration:
   ```
   nano nginx/conf.d/crypto-tracker.conf
   ```

3. Add the following configuration:
   ```
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl;
       server_name your-domain.com;

       ssl_certificate /etc/nginx/ssl/fullchain.pem;
       ssl_certificate_key /etc/nginx/ssl/privkey.pem;

       location / {
           proxy_pass http://crypto-tracker:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

4. Use Certbot to obtain SSL certificates (do this before starting the Nginx container):
   ```
   sudo apt install certbot -y
   sudo certbot certonly --standalone -d your-domain.com
   ```

5. Copy the certificates to your Nginx SSL directory:
   ```
   sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
   sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
   sudo chmod 644 nginx/ssl/*.pem
   ```

6. Start the containers:
   ```
   docker-compose up -d
   ```

## Maintenance

### Viewing Logs

To view the logs of your containers:
```
docker-compose logs
```

To follow the logs in real-time:
```
docker-compose logs -f
```

### Updating the Application

1. Pull the latest changes from your repository:
   ```
   git pull
   ```

2. Rebuild and restart the containers:
   ```
   docker-compose down
   docker-compose up -d --build
   ```

### Stopping the Application

To stop the application:
```
docker-compose down
```

## Troubleshooting

1. If you can't access the application, check:
   - Firewall settings: `sudo ufw status` and `sudo ufw allow 5000` if needed
   - Docker container status: `docker-compose ps`
   - Container logs: `docker-compose logs`

2. If the Docker build fails, check:
   - Dockerfile syntax
   - Internet connectivity on your VPS
   - Docker daemon status: `sudo systemctl status docker`

3. If Nginx is not working, check:
   - Nginx container logs: `docker-compose logs nginx`
   - Nginx configuration syntax
   - Domain DNS settings (if using a domain)