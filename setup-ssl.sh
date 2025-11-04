#!/bin/bash
# Setup Let's Encrypt SSL for SourceCheck Web
# Usage: sudo ./setup-ssl.sh yourdomain.com your@email.com

set -e

DOMAIN=$1
EMAIL=$2

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Usage: sudo ./setup-ssl.sh yourdomain.com your@email.com"
    exit 1
fi

echo "Setting up SSL for $DOMAIN..."

# Install certbot and nginx
apt update
apt install -y certbot python3-certbot-nginx nginx

# Create nginx config for SourceCheck
cat > /etc/nginx/sites-available/sourcecheck << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for long-running validations
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/sourcecheck /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx

# Get SSL certificate
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect

# Setup auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "✅ SSL setup complete!"
echo ""
echo "Your site is now available at: https://$DOMAIN"
echo ""
echo "Next steps:"
echo "1. Make sure your FastAPI app is running on port 8000"
echo "2. Test: curl https://$DOMAIN/health"
echo ""
echo "SSL certificate will auto-renew via certbot.timer"
