# The Hive - Deployment Guide
**Server IP**: 164.92.199.174  
**Domain**: hive.yusufss.com  
**Date**: December 1, 2025

---

## Step 1: Configure Domain DNS

1. Go to your domain registrar (where you bought yusufss.com)
2. Add these DNS records:

```
Type: A Record
Host: hive
Value: 164.92.199.174
TTL: 3600 (or automatic)

Type: A Record  
Host: www.hive
Value: 164.92.199.174
TTL: 3600 (or automatic)
```

3. Wait 5-30 minutes for DNS propagation
4. Verify: `ping hive.yusufss.com` (should show 164.92.199.174)

---

## Step 2: Initial Server Setup

SSH into your server:
```bash
ssh root@164.92.199.174
```

Update system and install Docker:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

Setup firewall:
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

---

## Step 3: Prepare Deployment Files

On your **local machine**:

```bash
cd /home/yusufss/swe573-practice/the_hive/infra

# Run deployment script
chmod +x deploy.sh
./deploy.sh 164.92.199.174
```

This creates `.env` file with generated secrets.

**IMPORTANT**: Edit the generated `.env` to add your domain:

```bash
nano .env
```

Change:
```
CORS_ORIGINS=http://164.92.199.174,http://164.92.199.174:80
VITE_API_BASE_URL=http://164.92.199.174/api/v1
```

To:
```
CORS_ORIGINS=https://hive.yusufss.com,https://www.hive.yusufss.com,http://hive.yusufss.com
VITE_API_BASE_URL=https://hive.yusufss.com/api/v1
```

---

## Step 4: Create Production Nginx Configuration

Create `nginx.prod.conf` in the infra folder:

```bash
cd /home/yusufss/swe573-practice/the_hive/infra
nano nginx.prod.conf
```

Paste this content:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # HTTP Server (redirect to HTTPS after SSL is setup)
    server {
        listen 80;
        server_name hive.yusufss.com www.hive.yusufss.com;

        # Certbot challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Initially serve site on HTTP
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /docs {
            proxy_pass http://backend;
        }

        location /openapi.json {
            proxy_pass http://backend;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
        }
    }
}
```

---

## Step 5: Copy Files to Server

From your **local machine**:

```bash
cd /home/yusufss/swe573-practice

# Create tarball
tar -czf the-hive-deploy.tar.gz the_hive/

# Copy to server
scp the-hive-deploy.tar.gz root@164.92.199.174:~/

# Copy deployment files
cd the_hive/infra
scp docker-compose.prod.yml nginx.prod.conf .env root@164.92.199.174:~/
```

---

## Step 6: Deploy on Server

SSH back to server:
```bash
ssh root@164.92.199.174
```

Setup application:
```bash
# Extract code
cd ~
tar -xzf the-hive-deploy.tar.gz
ls -la  # Should see the_hive/ folder

# Create deployment directory
mkdir -p ~/deploy
mv docker-compose.prod.yml nginx.prod.conf .env ~/deploy/
cd ~/deploy

# Verify files
ls -la
# Should see: docker-compose.prod.yml, nginx.prod.conf, .env

# Start services
docker compose -f docker-compose.prod.yml up -d --build
```

This will take 5-10 minutes to build.

---

## Step 7: Initialize Database

```bash
cd ~/deploy

# Wait for all containers to be running
docker compose -f docker-compose.prod.yml ps

# Initialize database
docker compose -f docker-compose.prod.yml exec backend python scripts/init_db.py

# Verify
docker compose -f docker-compose.prod.yml logs backend | tail -20
```

---

## Step 8: Test Application

Visit: **http://hive.yusufss.com** (should work!)

Test endpoints:
- Frontend: http://hive.yusufss.com
- API Docs: http://hive.yusufss.com/docs
- Health: http://hive.yusufss.com/api/v1/health

---

## Step 9: Setup SSL Certificate (HTTPS)

Install Certbot:
```bash
ssh root@164.92.199.174
apt install certbot -y
```

Stop nginx temporarily:
```bash
cd ~/deploy
docker compose -f docker-compose.prod.yml stop nginx
```

Get certificate:
```bash
certbot certonly --standalone \
  -d hive.yusufss.com \
  -d www.hive.yusufss.com \
  --email your@email.com \
  --agree-tos \
  --no-eff-email
```

Update nginx configuration:
```bash
nano nginx.prod.conf
```

Replace entire content with:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # HTTP - Redirect to HTTPS
    server {
        listen 80;
        server_name hive.yusufss.com www.hive.yusufss.com;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name hive.yusufss.com www.hive.yusufss.com;

        ssl_certificate /etc/letsencrypt/live/hive.yusufss.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/hive.yusufss.com/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /docs {
            proxy_pass http://backend;
        }

        location /openapi.json {
            proxy_pass http://backend;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
        }
    }
}
```

Update docker-compose to mount SSL certificates:
```bash
nano docker-compose.prod.yml
```

Add under nginx volumes:
```yaml
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
```

Restart nginx:
```bash
docker compose -f docker-compose.prod.yml up -d nginx
```

---

## Step 10: Setup Auto-Renewal

Create renewal script:
```bash
nano /root/renew-ssl.sh
```

```bash
#!/bin/bash
certbot renew --pre-hook "cd /root/deploy && docker compose -f docker-compose.prod.yml stop nginx" \
              --post-hook "cd /root/deploy && docker compose -f docker-compose.prod.yml start nginx"
```

Make executable and add to crontab:
```bash
chmod +x /root/renew-ssl.sh

# Add to crontab (runs daily at 2am)
crontab -e
```

Add this line:
```
0 2 * * * /root/renew-ssl.sh >> /var/log/certbot-renew.log 2>&1
```

---

## Step 11: Verify Everything Works

Visit: **https://hive.yusufss.com** ✅

Should show:
- 🔒 Secure HTTPS connection
- The Hive login page
- No certificate warnings

---

## Maintenance Commands

```bash
# View logs
cd ~/deploy
docker compose -f docker-compose.prod.yml logs -f

# Restart services
docker compose -f docker-compose.prod.yml restart

# Stop everything
docker compose -f docker-compose.prod.yml down

# Update application (after git push)
cd ~/the_hive
git pull
cd ~/deploy
docker compose -f docker-compose.prod.yml up -d --build

# Backup database
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres the_hive > backup_$(date +%Y%m%d).sql

# Restore database
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres the_hive < backup.sql
```

---

## Troubleshooting

**Container won't start:**
```bash
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
```

**Database connection issues:**
```bash
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d the_hive -c "SELECT 1;"
```

**Nginx issues:**
```bash
docker compose -f docker-compose.prod.yml exec nginx nginx -t
```

**Check running containers:**
```bash
docker compose -f docker-compose.prod.yml ps
```

---

## Security Checklist

- ✅ Firewall enabled (UFW)
- ✅ SSL/HTTPS configured
- ✅ Strong database password (auto-generated)
- ✅ Strong SECRET_KEY (auto-generated)
- ✅ Docker containers isolated
- ✅ Auto SSL renewal configured

---

## Support

If you encounter issues:
1. Check logs: `docker compose -f docker-compose.prod.yml logs`
2. Verify DNS: `dig hive.yusufss.com`
3. Check containers: `docker compose -f docker-compose.prod.yml ps`

**Your application will be live at**: https://hive.yusufss.com 🚀
