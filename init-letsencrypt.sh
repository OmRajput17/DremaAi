#!/bin/bash

# Initialize Let's Encrypt SSL certificates for Drema AI
# This script should be run ONCE during initial setup on your EC2 instance

set -e

DOMAIN="api.simplifyingskills.live"
EMAIL="your-email@example.com"  # UPDATE THIS with your email
STAGING=0  # Set to 1 for testing, 0 for production certificates

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Let's Encrypt SSL Certificate Setup${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Check if domain is accessible
echo -e "${YELLOW}Checking if domain is accessible...${NC}"
if ! ping -c 1 "$DOMAIN" &> /dev/null; then
    echo -e "${RED}ERROR: Cannot reach $DOMAIN${NC}"
    echo -e "${RED}Please ensure DNS is configured correctly!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Domain is accessible${NC}"
echo ""

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p certbot/conf certbot/www dhparam nginx
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Generate Diffie-Hellman parameters if not exists
if [ ! -f "dhparam/dhparam.pem" ]; then
    echo -e "${YELLOW}Generating Diffie-Hellman parameters (this may take a few minutes)...${NC}"
    openssl dhparam -out dhparam/dhparam.pem 2048
    echo -e "${GREEN}✓ DH parameters generated${NC}"
    echo ""
else
    echo -e "${GREEN}✓ DH parameters already exist${NC}"
    echo ""
fi

# Check if certificate already exists
if [ -d "certbot/conf/live/$DOMAIN" ]; then
    echo -e "${YELLOW}Certificate already exists for $DOMAIN${NC}"
    read -p "Do you want to renew it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Exiting without changes${NC}"
        exit 0
    fi
    rm -rf certbot/conf/live/$DOMAIN
    rm -rf certbot/conf/archive/$DOMAIN
    rm -f certbot/conf/renewal/$DOMAIN.conf
fi

# Create temporary nginx config for certificate acquisition
echo -e "${YELLOW}Creating temporary Nginx configuration...${NC}"
cat > nginx/app.conf.temp << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name api.simplifyingskills.live;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'OK';
        add_header Content-Type text/plain;
    }
}
EOF

# Backup existing config if it exists
if [ -f "nginx/app.conf" ]; then
    mv nginx/app.conf nginx/app.conf.backup
fi

mv nginx/app.conf.temp nginx/app.conf
echo -e "${GREEN}✓ Temporary config created${NC}"
echo ""

# Start nginx temporarily
echo -e "${YELLOW}Starting Nginx...${NC}"
docker compose up -d nginx
sleep 5
echo -e "${GREEN}✓ Nginx started${NC}"
echo ""

# Request certificate
echo -e "${YELLOW}Requesting SSL certificate from Let's Encrypt...${NC}"
echo -e "${YELLOW}Domain: $DOMAIN${NC}"
echo -e "${YELLOW}Email: $EMAIL${NC}"
echo ""

CERTBOT_ARGS="certonly --webroot --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN"

if [ $STAGING -eq 1 ]; then
    echo -e "${YELLOW}Using staging server (test certificates)${NC}"
    CERTBOT_ARGS="$CERTBOT_ARGS --staging"
fi

if docker compose run --rm certbot $CERTBOT_ARGS; then
    echo -e "${GREEN}✓ Certificate obtained successfully!${NC}"
    echo ""
else
    echo -e "${RED}Failed to obtain certificate${NC}"
    echo -e "${RED}Please check the error messages above${NC}"
    
    # Restore backup if exists
    if [ -f "nginx/app.conf.backup" ]; then
        mv nginx/app.conf.backup nginx/app.conf
    fi
    
    docker compose down
    exit 1
fi

# Restore production nginx config
echo -e "${YELLOW}Restoring production Nginx configuration...${NC}"
if [ -f "nginx/app.conf.backup" ]; then
    mv nginx/app.conf.backup nginx/app.conf
else
    # If no backup exists, create production config
    echo -e "${YELLOW}Production config not found, please ensure nginx/app.conf exists${NC}"
fi
echo -e "${GREEN}✓ Configuration restored${NC}"
echo ""

# Restart nginx with SSL
echo -e "${YELLOW}Restarting Nginx with SSL...${NC}"
docker compose down
docker compose up -d
sleep 5
echo -e "${GREEN}✓ Services restarted${NC}"
echo ""

# Verify setup
echo -e "${YELLOW}Verifying setup...${NC}"
if docker compose ps | grep -q "nginx.*Up"; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${RED}✗ Nginx is not running${NC}"
fi

if docker compose ps | grep -q "drema-ai.*Up"; then
    echo -e "${GREEN}✓ Flask app is running${NC}"
else
    echo -e "${RED}✗ Flask app is not running${NC}"
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}SSL Setup Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${GREEN}Your API is now available at:${NC}"
echo -e "${GREEN}  https://$DOMAIN${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Test your API: curl https://$DOMAIN/api/boards"
echo -e "  2. Check certificate: openssl s_client -connect $DOMAIN:443 -servername $DOMAIN"
echo -e "  3. Certificates will auto-renew every 60 days"
echo ""
