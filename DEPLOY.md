# EC2 Deployment Guide with SSL

Complete guide to deploy SourceCheck Web on EC2 with Let's Encrypt SSL.

## Prerequisites

1. **EC2 Instance**: t3.medium (4GB RAM minimum for torch)
2. **Domain**: Point your domain A record to EC2 public IP
3. **Security Group**: Open ports 80 (HTTP) and 443 (HTTPS)

## Step 1: Initial Setup

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-venv git

# Clone repository
cd ~
git clone <your-repo-url> sourcecheck
cd sourcecheck/sourcecheck-web
```

## Step 2: Install Application

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Test the app
uvicorn api.main:app --host 127.0.0.1 --port 8000
# Ctrl+C to stop
```

## Step 3: Setup SSL with Let's Encrypt

```bash
# Make script executable
chmod +x setup-ssl.sh

# Run SSL setup (replace with your domain and email)
sudo ./setup-ssl.sh yourdomain.com your@email.com
```

This script will:
- Install nginx and certbot
- Configure nginx as reverse proxy
- Get SSL certificate from Let's Encrypt
- Setup auto-renewal

## Step 4: Setup Systemd Service

```bash
# Edit service file if needed (change password!)
nano sourcecheck.service

# Copy service file
sudo cp sourcecheck.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable sourcecheck
sudo systemctl start sourcecheck

# Check status
sudo systemctl status sourcecheck
```

## Step 5: Verify Deployment

```bash
# Check if app is running
curl http://localhost:8000/health

# Check SSL
curl https://yourdomain.com/health

# View logs
sudo journalctl -u sourcecheck -f
```

## Updating the Application

```bash
# Pull latest changes
cd ~/sourcecheck
git pull

# Restart service
sudo systemctl restart sourcecheck
```

## Troubleshooting

### App won't start
```bash
# Check logs
sudo journalctl -u sourcecheck -n 50

# Check if port 8000 is in use
sudo lsof -i :8000

# Test manually
cd ~/sourcecheck/sourcecheck-web
source venv/bin/activate
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

### SSL issues
```bash
# Check nginx status
sudo systemctl status nginx

# Test nginx config
sudo nginx -t

# Check certbot
sudo certbot certificates

# Renew manually
sudo certbot renew --dry-run
```

### Out of memory
```bash
# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Security Notes

1. **Change default password** in `sourcecheck.service`
2. **Restrict security group** to only your IP if possible
3. **Keep system updated**: `sudo apt update && sudo apt upgrade`
4. **Monitor logs**: `sudo journalctl -u sourcecheck -f`

## Cost Optimization

- **Use spot instance**: ~70% savings (~$20/month instead of $60)
- **Stop when not in use**: Only pay for storage (~$5/month)
- **Downgrade after demo**: Switch to t3.small if possible

## Access Your Demo

Your SourceCheck Web is now available at:
- **URL**: https://yourdomain.com
- **Username**: demo (or what you set in service file)
- **Password**: changeme (CHANGE THIS!)

🎉 Demo ready!
