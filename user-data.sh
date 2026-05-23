#!/bin/bash
# user-data.sh - Bootstrap script for EC2 instance (AWS Academy)
# OS: Ubuntu 22.04 LTS
# Purpose: Automatically provision Docker, clone repo, and start CellHub stack
#
# Usage: 
#   1. Create EC2 instance in AWS Academy (t2.micro or larger)
#   2. Paste this script into "User data" field when launching instance
#   3. Instance will auto-configure and start services
#   4. Access via http://EC2_PUBLIC_IP once services are ready

set -e  # Exit on error
set -x  # Print commands (for debugging)

# Update system packages
apt-get update
apt-get upgrade -y

# Install Docker and Docker Compose plugin
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    build-essential \
    python3-pip

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker and docker-compose plugin
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add ubuntu user to docker group (permission management)
usermod -aG docker ubuntu

# Enable Docker service
systemctl enable docker
systemctl start docker

# Create deployment directory
mkdir -p /opt/cellhub
cd /opt/cellhub

# Clone repository (using HTTPS; requires personal access token or public repo)
# For private repo: use git clone https://[TOKEN]@github.com/[USER]/cellhub.git
# Or set up SSH key in .ssh/config beforehand
git clone https://github.com/[YOUR_GITHUB_USER]/cellhub.git . || \
  git clone https://github.com/user/cellhub.git .

# Set permissions
chown -R ubuntu:ubuntu /opt/cellhub

# Create .env file for production settings (customize as needed)
cat > /opt/cellhub/.env << 'EOF'
# Production environment variables for CellHub on EC2
DEBUG=False
SECRET_KEY=change-this-to-a-real-secret-key-in-aws-secrets-manager
ALLOWED_HOSTS=*
CELERY_BROKER_URL=redis://redis:6379/0
DATABASE_URL=sqlite:///db.sqlite3
# For production: use RDS
# DATABASE_URL=postgresql://user:password@rds-endpoint:5432/cellhub_db
EOF

# Build and start services
cd /opt/cellhub
docker compose build 2>&1 | tee build.log
docker compose up -d 2>&1 | tee deploy.log

# Wait for Django service to be ready
sleep 10

# Run migrations
docker compose exec -T django_web python manage.py migrate 2>&1 | tee migrate.log || true

# Load sample data (optional)
docker compose exec -T django_web python seed_data.py 2>&1 | tee seed.log || true

# Create superuser (manual input required, so commented for now)
# docker compose exec django_web python manage.py createsuperuser

# Health check
sleep 5
curl -s http://localhost/health/ || echo "Health check endpoint not available yet"
curl -s http://localhost/api/v1/system/info/ || echo "System info endpoint not available yet"

# Log completion
echo "CellHub stack deployment completed at $(date)" >> /var/log/cellhub-bootstrap.log

# Additional setup (optional) 
# - Configure CloudWatch logging
# - Setup auto-scaling
# - Attach IAM roles for S3, Secrets Manager, etc.

exit 0
