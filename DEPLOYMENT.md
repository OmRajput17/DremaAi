# Deployment Instructions for EC2

This guide provides step-by-step instructions for deploying the SSL-enabled Drema AI application to your EC2 instance.

## Prerequisites Checklist

Before deployment, ensure:

- [ ] **DNS Configuration**: `api.simplifyingskills.live` A record points to EC2 public IP
- [ ] **EC2 Security Group**: Ports 80 and 443 are open for inbound traffic
- [ ] **Docker Installed**: Docker and Docker Compose are installed on EC2
- [ ] **Repository Cloned**: DremaAi repository is cloned to EC2
- [ ] **Environment Variables**: `.env` file exists with required API keys

## Step-by-Step Deployment

### 1. SSH into EC2 Instance

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### 2. Navigate to Project Directory

```bash
cd ~/DremaAi
```

### 3. Pull Latest Changes

```bash
git pull origin main
```

### 4. Verify Environment Variables

```bash
cat .env
```

Ensure it contains:
```env
OPENAI_API_KEY=your_key_here
LANGCHAIN_PROJECT=DremaAi
PORT=5000
FLASK_ENV=production
```

### 5. Update Email in SSL Script

```bash
nano init-letsencrypt.sh
```

Change the email address:
```bash
EMAIL="your-email@example.com"
```

Save and exit (Ctrl+X, then Y, then Enter).

### 6. Make Scripts Executable

```bash
chmod +x init-letsencrypt.sh
chmod +x renew-certificates.sh
```

### 7. Run SSL Initialization

**Important**: This step will:
- Generate DH parameters (takes 3-5 minutes)
- Request SSL certificate from Let's Encrypt
- Configure and start all services

```bash
./init-letsencrypt.sh
```

Expected output:
```
======================================
Let's Encrypt SSL Certificate Setup
======================================

✓ Domain is accessible
✓ Directories created
✓ DH parameters generated
✓ Nginx started
✓ Certificate obtained successfully!
✓ Configuration restored
✓ Services restarted
✓ Nginx is running
✓ Flask app is running

======================================
SSL Setup Complete!
======================================
```

### 8. Verify Deployment

Test the API:

```bash
# Test HTTPS endpoint
curl https://api.simplifyingskills.live/api/boards

# Test HTTP redirect
curl -I http://api.simplifyingskills.live/api/boards
```

Check running containers:

```bash
docker compose ps
```

Expected output:
```
NAME                IMAGE                              STATUS
drema-ai            omrajput17/drema-ai:latest         Up
drema-nginx         nginx:alpine                       Up
drema-certbot       certbot/certbot                    Up
```

## Troubleshooting Deployment

### Issue: "Cannot reach domain"

**Solution**:
```bash
# Verify DNS
nslookup api.simplifyingskills.live

# Check security group allows ports 80 and 443
```

### Issue: "Certificate request failed"

**Solutions**:
1. Check Nginx logs:
   ```bash
   docker compose logs nginx
   ```

2. Check Certbot logs:
   ```bash
   docker compose logs certbot
   ```

3. Test with staging certificate:
   ```bash
   # Edit init-letsencrypt.sh and set STAGING=1
   nano init-letsencrypt.sh
   # Run again
   ./init-letsencrypt.sh
   ```

### Issue: "DH parameter generation takes too long"

**Note**: This is normal! Generating 2048-bit DH parameters can take 3-10 minutes depending on your EC2 instance type. Just wait for it to complete.

### Issue: "Services not starting"

**Solutions**:
1. Check Docker status:
   ```bash
   sudo systemctl status docker
   ```

2. View all logs:
   ```bash
   docker compose logs
   ```

3. Restart Docker:
   ```bash
   sudo systemctl restart docker
   docker compose up -d
   ```

## Post-Deployment Verification

### 1. Test API Endpoints

```bash
# Health check
curl https://api.simplifyingskills.live/api/boards

# Test an actual endpoint
curl https://api.simplifyingskills.live/api/classes?board=CBSE
```

### 2. Test SSL Certificate

```bash
openssl s_client -connect api.simplifyingskills.live:443 -servername api.simplifyingskills.live < /dev/null | grep "Verify return code"
```

Should show: `Verify return code: 0 (ok)`

### 3. Check SSL Rating

Visit: https://www.ssllabs.com/ssltest/analyze.html?d=api.simplifyingskills.live

You should get an A or A+ rating.

### 4. Test Auto-Renewal

```bash
# Dry-run renewal
docker compose run --rm certbot renew --dry-run
```

Should complete without errors.

## CI/CD Integration

The GitHub Actions workflow is already configured to deploy to EC2. After initial SSL setup:

1. **Automatic Deployments**: Pushing to `main` branch automatically deploys to EC2
2. **SSL Persistence**: Certificates are stored in volumes and persist across deployments
3. **No Downtime**: Docker Compose handles rolling updates

### Verify CI/CD is Working

1. Make a small change and push to main
2. Watch GitHub Actions workflow
3. Verify deployment on EC2:
   ```bash
   docker compose logs --tail 50
   ```

## Maintenance

### Update Application

```bash
cd ~/DremaAi
git pull origin main
docker compose pull
docker compose up -d --force-recreate
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f drema-ai
docker compose logs -f nginx
docker compose logs -f certbot
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart nginx
docker compose restart drema-ai
```

### Check Certificate Expiry

```bash
docker compose run --rm certbot certificates
```

### Manual Certificate Renewal

```bash
./renew-certificates.sh
```

## Security Checklist

After deployment, verify:

- [ ] HTTPS works and shows valid certificate
- [ ] HTTP redirects to HTTPS
- [ ] No certificate warnings in browser
- [ ] API endpoints are accessible
- [ ] Automatic renewal is configured
- [ ] Firewall rules are properly configured

## Support

For issues:
1. Check [SSL_SETUP.md](SSL_SETUP.md) for SSL-specific troubleshooting
2. Check [EC2_SETUP_GUIDE.md](EC2_SETUP_GUIDE.md) for EC2-specific issues
3. Review logs: `docker compose logs`

---

**Last Updated**: December 2025
