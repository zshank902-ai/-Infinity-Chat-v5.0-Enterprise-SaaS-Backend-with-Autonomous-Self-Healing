#!/bin/bash
# Infinity Chat VPS Auto-Setup Script (Optimized for Oracle Cloud ARM)

echo "Starting VPS Hardening and Setup..."

# 1. Update and Install Dependencies
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y docker.io docker-compose nginx git ufw

# 2. Setup Firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 3. Docker Configuration
sudo systemctl enable docker
sudo systemctl start docker

# 4. Create Project Directory
mkdir -p ~/infinity_chat
cd ~/infinity_chat

# 5. Nginx Config for Reverse Proxy
cat <<EOF | sudo tee /etc/nginx/sites-available/infinity_chat
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/infinity_chat /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "VPS SETUP COMPLETE!"
echo "Now just copy your .env file and run: docker-compose up -d"
