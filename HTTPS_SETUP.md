# HTTPS Setup Guide for hive.yusufss.com

This guide will walk you through setting up HTTPS/SSL for your server at `http://hive.yusufss.com`.

## Prerequisites

- ✅ Server is accessible via SSH
- ✅ Domain `hive.yusufss.com` points to your server IP (164.92.199.174)
- ✅ HTTP is currently working
- ✅ Port 80 and 443 are open in firewall

## Step 1: Update Configuration Files on Server

First, copy the updated configuration files to your server:

**On your local machine:**
```bash
cd /home/yusufss/swe573-practice/the_hive/infra
scp nginx.prod.conf docker-compose.prod.yml root@164.92.199.174:~/deploy/
```

## Step 2: Install Certbot on Server

SSH into your server and install Certbot:

```bash
ssh root@164.92.199.174
apt update
apt install certbot -y
```

## Step 3: Stop Nginx Container Temporarily

We need to stop nginx so Certbot can use port 80 for verification:

```bash
cd ~/deploy
docker compose -f docker-compose.prod.yml stop nginx
```

## Step 4: Obtain SSL Certificate

Run Certbot to get your SSL certificate. **Replace `your@email.com` with your actual email:**

```bash
certbot certonly --standalone \
  -d hive.yusufss.com \
  -d www.hive.yusufss.com \
  --email your@email.com \
  --agree-tos \
  --no-eff-email
```

**Important:** 
- Use a valid email address (for certificate expiration notifications)
- Certbot will verify domain ownership by connecting to port 80
- The certificates will be saved to `/etc/letsencrypt/live/hive.yusufss.com/`

## Step 5: Verify Certificate Files

Check that the certificates were created:

```bash
ls -la /etc/letsencrypt/live/hive.yusufss.com/
```

You should see:
- `fullchain.pem` (SSL certificate)
- `privkey.pem` (Private key)

## Step 6: Restart Nginx with HTTPS Configuration

The nginx configuration file has already been updated to support HTTPS. Now restart nginx:

```bash
cd ~/deploy
docker compose -f docker-compose.prod.yml up -d nginx
```

Verify nginx is running:
```bash
docker compose -f docker-compose.prod.yml ps
```

## Step 7: Test HTTPS

Visit your site:
- **HTTPS**: https://hive.yusufss.com ✅
- **HTTP**: http://hive.yusufss.com (should redirect to HTTPS)

You should see a padlock icon in your browser indicating a secure connection.

## Step 8: Setup Auto-Renewal

SSL certificates expire every 90 days. Let's set up automatic renewal:

Create a renewal script:
```bash
nano /root/renew-ssl.sh
```

Paste this content:
```bash
#!/bin/bash
cd /root/deploy
docker compose -f docker-compose.prod.yml stop nginx
certbot renew --standalone
docker compose -f docker-compose.prod.yml start nginx
```

Make it executable:
```bash
chmod +x /root/renew-ssl.sh
```

Add to crontab (runs twice daily to check for renewal):
```bash
crontab -e
```

Add this line:
```
0 2,14 * * * /root/renew-ssl.sh >> /var/log/certbot-renew.log 2>&1
```

This will check for certificate renewal at 2 AM and 2 PM daily.

## Step 9: Update Environment Variables (if needed)

If your `.env` file still has HTTP URLs, update them to HTTPS:

```bash
cd ~/deploy
nano .env
```

Update these variables:
```env
CORS_ORIGINS=https://hive.yusufss.com,https://www.hive.yusufss.com
VITE_API_BASE_URL=https://hive.yusufss.com/api/v1
```

Then restart the frontend container:
```bash
docker compose -f docker-compose.prod.yml up -d --build frontend
```

## Troubleshooting

### Certificate generation fails
- Make sure port 80 is accessible from the internet
- Verify DNS: `dig hive.yusufss.com` should show your server IP
- Check firewall: `ufw status` should show port 80 and 443 allowed

### Nginx won't start
- Check nginx logs: `docker compose -f docker-compose.prod.yml logs nginx`
- Verify certificate paths: `ls -la /etc/letsencrypt/live/hive.yusufss.com/`
- Test nginx config: `docker compose -f docker-compose.prod.yml exec nginx nginx -t`

### HTTPS not working
- Verify port 443 is open: `ufw allow 443/tcp`
- Check nginx is listening on 443: `docker compose -f docker-compose.prod.yml exec nginx netstat -tlnp`
- Check certificate permissions: `ls -la /etc/letsencrypt/live/hive.yusufss.com/`

### Certificate renewal fails
- Check renewal logs: `cat /var/log/certbot-renew.log`
- Test renewal manually: `certbot renew --dry-run`
- Make sure the renewal script has correct paths

## Verification Checklist

- [ ] HTTPS works: https://hive.yusufss.com loads without errors
- [ ] HTTP redirects to HTTPS automatically
- [ ] Browser shows padlock icon (secure connection)
- [ ] API endpoints work: https://hive.yusufss.com/api/v1/health
- [ ] Frontend loads correctly
- [ ] Auto-renewal script is in crontab

## Security Notes

- SSL certificates are valid for 90 days and auto-renew
- Let's Encrypt has rate limits (50 certificates per domain per week)
- Keep your email address updated for expiration notifications
- The private key is stored securely in `/etc/letsencrypt/`

---

**Your site should now be accessible via HTTPS! 🎉**

For more details, see the main [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

