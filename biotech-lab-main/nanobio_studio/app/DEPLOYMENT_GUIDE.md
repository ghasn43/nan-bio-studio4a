# ML Module Deployment Guide

Complete instructions for deploying the ML Module in development, staging, and production environments.

## Table of Contents
1. [Local Development](#local-development)
2. [Staging Deployment](#staging-deployment)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Setup

```bash
# 1. Navigate to project
cd d:\nano_bio_studio_last\biotech-lab-main

# 2. Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn sqlalchemy pydantic

# 4. Create .env file
cat > .env << EOF
ENV=development
DATABASE_URL=sqlite:///ml_module.db
API_TITLE=NanoBio ML API
API_PREFIX=/api/v1
MODELS_DIR=models_store
LOG_LEVEL=INFO
EOF

# 5. Create necessary directories
mkdir -p models_store
mkdir -p .cache

# 6. Initialize database
python -c "from nanobio_studio.app.db.database import get_db; get_db().init_db()"
```

### Running the API

```bash
# Method 1: Direct uvicorn
uvicorn nanobio_studio.app.main:app --reload --host 127.0.0.1 --port 8000

# Method 2: Using Python
python -m uvicorn nanobio_studio.app.main:app --reload

# Access
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/api/v1/ml/health
```

### Running Alongside Streamlit

```bash
# Terminal 1: API
uvicorn nanobio_studio.app.main:app --port 8001

# Terminal 2: Streamlit
streamlit run App.py --server.port 8000
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Specific test file
pytest tests/test_ml_service.py -v

# With coverage
pytest tests/ --cov=nanobio_studio.app --cov-report=html
```

---

## Staging Deployment

### Environment Setup

```bash
# 1. Use PostgreSQL for staging
pip install psycopg2-binary

# 2. Create .env for staging
cat > .env.staging << EOF
ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/nanobio_ml_staging
API_TITLE=NanoBio ML API (Staging)
API_PREFIX=/api/v1
MODELS_DIR=/var/ml_models
LOG_LEVEL=DEBUG
LOG_FILE=/var/log/ml_module.log
EOF

# 3. Initialize database
export DATABASE_URL=postgresql://user:password@localhost:5432/nanobio_ml_staging
python -c "from nanobio_studio.app.db.database import get_db; get_db().init_db()"
```

### Running with Gunicorn

```bash
# 1. Install production server
pip install gunicorn

# 2. Create startup script (run.sh)
cat > run.sh << 'EOF'
#!/bin/bash
export ENV=development
export DATABASE_URL=postgresql://user:password@localhost:5432/nanobio_ml_staging
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    nanobio_studio.app.main:app
EOF

chmod +x run.sh
./run.sh
```

### Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/nanobio-ml
upstream ml_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name ml-staging.nanobio.local;

    client_max_body_size 100M;

    location / {
        proxy_pass http://ml_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://ml_api/docs;
    }

    location /openapi.json {
        proxy_pass http://ml_api/openapi.json;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/nanobio-ml /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    supervisor \
    git

# Create app user
sudo useradd -m -s /bin/bash nanobio
sudo usermod -aG www-data nanobio
```

### 2. Application Setup

```bash
# Clone/pull latest code
sudo -u nanobio git clone /path/to/repo /home/nanobio/app
cd /home/nanobio/app

# Create virtual environment
sudo -u nanobio python3.9 -m venv venv
sudo -u nanobio venv/bin/pip install --upgrade pip setuptools wheel
sudo -u nanobio venv/bin/pip install -r requirements.txt
sudo -u nanobio venv/bin/pip install gunicorn psycopg2-binary
```

### 3. Production Environment

```bash
cat | sudo tee /home/nanobio/app/.env.production << 'EOF'
ENV=production
DEBUG=False
DATABASE_URL=postgresql://nanobio:$STRONG_PASSWORD@localhost:5432/nanobio_ml_prod
API_TITLE=NanoBio ML API
API_PREFIX=/api/v1
MODELS_DIR=/data/ml_models
LOG_LEVEL=INFO
LOG_FILE=/var/log/nanobio/ml_module.log
EOF

sudo chmod 600 /home/nanobio/app/.env.production
```

### 4. PostgreSQL Setup

```bash
sudo -u postgres psql << EOF
CREATE USER nanobio WITH PASSWORD '$STRONG_PASSWORD';
CREATE DATABASE nanobio_ml_prod OWNER nanobio;
GRANT ALL PRIVILEGES ON DATABASE nanobio_ml_prod TO nanobio;
\connect nanobio_ml_prod
GRANT ALL ON SCHEMA public TO nanobio;
EOF

# Initialize schema
cd /home/nanobio/app
source venv/bin/activate
export DATABASE_URL=postgresql://nanobio:$STRONG_PASSWORD@localhost:5432/nanobio_ml_prod
python -c "from nanobio_studio.app.db.database import get_db; get_db().init_db()"
```

### 5. Supervisor Configuration

```ini
# /etc/supervisor/conf.d/nanobio-ml.conf
[program:nanobio-ml]
user=nanobio
directory=/home/nanobio/app
command=/home/nanobio/app/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/nanobio/ml_access.log \
    --error-logfile /var/log/nanobio/ml_error.log \
    --log-level info \
    nanobio_studio.app.main:app

autostart=true
autorestart=true
startsecs=10
stopwaitsecs=10
stdout_logfile=/var/log/nanobio/ml_stdout.log
stderr_logfile=/var/log/nanobio/ml_stderr.log
```

Enable:
```bash
sudo mkdir -p /var/log/nanobio
sudo chown nanobio:nanobio /var/log/nanobio
sudo supervisorctl update
sudo supervisorctl status nanobio-ml
```

### 6. Production Nginx Config

```nginx
# /etc/nginx/sites-available/nanobio-ml-prod
upstream ml_api {
    server 127.0.0.1:8000;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/s;

server {
    listen 443 ssl http2;
    server_name api.nanobio.com;

    ssl_certificate /etc/letsencrypt/live/api.nanobio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.nanobio.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 100M;

    location / {
        limit_req zone=api_limit burst=50 nodelay;

        proxy_pass http://ml_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Disable access to docs in production
    location /docs {
        return 404;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.nanobio.com;
    return 301 https://$server_name$request_uri;
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/nanobio-ml-prod /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn uvicorn sqlalchemy pydantic

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/ml/health')"

# Expose port
EXPOSE 8000

# Start application
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "nanobio_studio.app.main:app"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  # PostgreSQL
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: nanobio
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: nanobio_ml
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # ML API
  api:
    build: .
    environment:
      DATABASE_URL: postgresql://nanobio:${DB_PASSWORD}@db:5432/nanobio_ml
      ENV: production
      LOG_LEVEL: INFO
      MODELS_DIR: /data/ml_models
    volumes:
      - ./models_store:/data/ml_models
      - ./logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: unless-stopped

  # Nginx (optional)
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

```bash
# .env.docker
DB_PASSWORD=secure_password_here
```

```bash
# Deploy
docker-compose -f docker-compose.yml up -d

# Monitor
docker-compose logs -f api

# Stop
docker-compose down
```

---

## Monitoring & Logging

### Application Logs

```bash
# Tail logs
tail -f /var/log/nanobio/ml_module.log

# Search for errors
grep ERROR /var/log/nanobio/ml_module.log

# View supervisor logs
sudo supervisorctl tail nanobio-ml
```

### Health Monitoring

```bash
# Manual check
curl http://localhost:8000/api/v1/ml/health

# Continuous monitoring
watch -n 5 'curl -s http://localhost:8000/api/v1/ml/health | jq'
```

### Performance Monitoring

```bash
# Using htop
htop -p $(pgrep -f gunicorn)

# Database connections
psql -U nanobio -d nanobio_ml_prod -c "SELECT count(*) FROM pg_stat_activity;"

# Disk usage
du -sh /data/ml_models
du -sh /var/log/nanobio/
```

### Backup Strategy

```bash
# Database backup
sudo -u postgres pg_dump nanobio_ml_prod | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Models backup
tar -czf models_backup_$(date +%Y%m%d_%H%M%S).tar.gz /data/ml_models

# Automated daily backup
cat > /etc/cron.daily/nanobio-ml-backup << 'EOF'
#!/bin/bash
BACKUP_DIR=/backups/nanobio_ml
mkdir -p $BACKUP_DIR
sudo -u postgres pg_dump nanobio_ml_prod | gzip > $BACKUP_DIR/db_$(date +\%Y\%m\%d).sql.gz
tar -czf $BACKUP_DIR/models_$(date +\%Y\%m\%d).tar.gz /data/ml_models
find $BACKUP_DIR -type f -mtime +7 -delete  # Keep 7 days
EOF

chmod +x /etc/cron.daily/nanobio-ml-backup
```

---

## Troubleshooting

### Common Issues

#### API Won't Start

```bash
# Check logs
sudo supervisorctl tail nanobio-ml stderr

# Verify port is free
lsof -i :8000

# Test import
source venv/bin/activate
python -c "from nanobio_studio.app.main import app; print('OK')"
```

#### Database Connection Issues

```bash
# Test connection
psql -U nanobio -h localhost -d nanobio_ml_prod -c "SELECT 1;"

# Check credentials
grep DATABASE_URL /home/nanobio/app/.env.production

# View active connections
psql -U postgres -d nanobio_ml_prod -c "SELECT * FROM pg_stat_activity;"
```

#### High Memory Usage

```bash
# Check worker processes
ps aux | grep gunicorn

# Reduce workers
# Edit supervisor config, change "-w 4" to "-w 2"
sudo supervisorctl restart nanobio-ml

# Monitor memory
watch -n 2 'free -h'
```

#### Slow Model Training

```bash
# Check CPU usage
top

# Check I/O
iostat -x 2 5

# Reduce model types or dataset size in config
# Increase n_jobs if available cores
```

### Rollback Procedure

```bash
# 1. Stop application
sudo supervisorctl stop nanobio-ml

# 2. Revert code
cd /home/nanobio/app
git revert HEAD
# or
git checkout <previous-tag>

# 3. Restore database backup if needed
psql -U nanobio -d nanobio_ml_prod < backup.sql

# 4. Restart
sudo supervisorctl start nanobio-ml

# 5. Verify
curl https://api.nanobio.com/api/v1/ml/health
```

---

## Scaling Recommendations

### Horizontal Scaling
- Deploy multiple API instances behind load balancer
- Use connection pooling for database
- Cache frequently accessed models in memory

### Vertical Scaling
- Increase Gunicorn workers (`-w` parameter)
- Allocate more server resources
- Use distributed training for large models

### Database Optimization
- Add indexes on frequently queried columns
- Regular VACUUM and ANALYZE
- Connection pooling with PgBouncer

---

## Security Checklist

- ✅ Use HTTPS/SSL in production
- ✅ Enable authentication for API
- ✅ Implement RBAC
- ✅ Validate all inputs with Pydantic
- ✅ Use strong database passwords
- ✅ Restrict file upload sizes
- ✅ Regular security updates
- ✅ Backup critical data
- ✅ Monitor access logs
- ✅ Use environment variables for secrets

---

## Support & Maintenance

For issues or questions:
1. Check logs: `/var/log/nanobio/ml_module.log`
2. Review API docs: `https://api.nanobio.com/docs`
3. Contact: [support email]

---

**Last Updated**: 2024
