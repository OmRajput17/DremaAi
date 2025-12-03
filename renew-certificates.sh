#!/bin/bash

# Renew Let's Encrypt SSL certificates
# This script can be run manually or via cron

set -e

echo "==================================="
echo "SSL Certificate Renewal"
echo "==================================="
echo ""

# Attempt renewal
echo "Attempting to renew certificates..."
if docker compose run --rm certbot renew; then
    echo "✓ Certificate renewal successful or not needed"
    
    # Reload nginx to pick up new certificates
    echo "Reloading Nginx..."
    docker compose exec nginx nginx -s reload
    echo "✓ Nginx reloaded"
else
    echo "✗ Certificate renewal failed"
    exit 1
fi

echo ""
echo "Certificate renewal process completed!"
echo ""
