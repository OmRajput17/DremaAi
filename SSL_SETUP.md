# SSL Certificate Setup Guide

This guide explains how to set up and manage SSL certificates for the Drema AI API using Nginx and Let's Encrypt.

## Prerequisites

Before setting up SSL, ensure you have:

1. **Domain Name**: `api.simplifyingskills.live` configured with DNS
2. **DNS Configuration**: An A record pointing to your EC2 instance's public IP
3. **EC2 Security Groups**: Ports 80 and 443 open for inbound traffic
4. **Docker & Docker Compose**: Installed on your EC2 instance

### Verify DNS Configuration

```bash
# Check if domain resolves to your EC2 IP
nslookup api.simplifyingskills.live

# Or use dig
dig api.simplifyingskills.live +short
```

The output should show your EC2 instance's public IP address.

### Verify Security Groups

Ensure your EC2 security group allows:
- **Port 80 (HTTP)**: Required for Let's Encrypt validation
- **Port 443 (HTTPS)**: Required for HTTPS traffic

## Initial SSL Setup

### Step 1: Update Email Address

Edit the `init-letsencrypt.sh` script and update the email address:

```bash
nano init-letsencrypt.sh
```

Change this line:
```bash
EMAIL="your-email@example.com"  # UPDATE THIS
```

To your actual email address (required by Let's Encrypt):
```bash
EMAIL="youremail@example.com"
```

### Step 2: Make Scripts Executable

```bash
chmod +x init-letsencrypt.sh
chmod +x renew-certificates.sh
```

### Step 3: Run Initial Setup

```bash
./init-letsencrypt.sh
```

This script will:
1. ✓ Check domain accessibility
2. ✓ Create necessary directories
3. ✓ Generate DH parameters for security
4. ✓ Start Nginx temporarily
5. ✓ Request SSL certificate from Let's Encrypt
6. ✓ Configure production Nginx with SSL
7. ✓ Start all services

**Note**: The script may take 5-10 minutes to complete, especially when generating DH parameters.

### Step 4: Verify SSL is Working

```bash
# Test HTTPS endpoint
curl https://api.simplifyingskills.live/api/boards

# Check certificate details
openssl s_client -connect api.simplifyingskills.live:443 -servername api.simplifyingskills.live < /dev/null

# Test HTTP to HTTPS redirect
curl -I http://api.simplifyingskills.live/api/boards
```

Expected results:
- HTTPS endpoint returns API response
- Certificate shows "Issuer: Let's Encrypt"
- HTTP requests redirect to HTTPS (301/302)

## Certificate Management

### Automatic Renewal

Certificates are automatically renewed by the Certbot container, which:
- Runs renewal checks twice daily
- Renews certificates when they have 30 days or less remaining
- Automatically reloads Nginx after successful renewal

**No manual intervention is required for renewals.**

### Manual Renewal

To manually renew certificates:

```bash
./renew-certificates.sh
```

Or use Docker directly:

```bash
docker compose run --rm certbot renew
docker compose exec nginx nginx -s reload
```

### Dry-Run Renewal Test

Test renewal without actually renewing:

```bash
docker compose run --rm certbot renew --dry-run
```

This is useful to verify that renewal will work when needed.

### Check Certificate Expiry

```bash
# View certificate expiry date
echo | openssl s_client -servername api.simplifyingskills.live -connect api.simplifyingskills.live:443 2>/dev/null | openssl x509 -noout -dates
```

## Troubleshooting

### Certificate Request Failed

**Problem**: `init-letsencrypt.sh` fails to obtain certificate

**Solutions**:
1. Verify DNS is configured correctly:
   ```bash
   nslookup api.simplifyingskills.live
   ```

2. Check that ports 80 and 443 are accessible:
   ```bash
   # From your local machine
   telnet api.simplifyingskills.live 80
   telnet api.simplifyingskills.live 443
   ```

3. Check Nginx logs:
   ```bash
   docker compose logs nginx
   ```

4. Check Certbot logs:
   ```bash
   docker compose logs certbot
   ```

5. Try with staging certificates first:
   ```bash
   # Edit init-letsencrypt.sh and set STAGING=1
   # Then run the script
   ./init-letsencrypt.sh
   ```

### HTTPS Not Working

**Problem**: Can't access API via HTTPS

**Solutions**:
1. Check if Nginx is running:
   ```bash
   docker compose ps nginx
   ```

2. Check Nginx configuration:
   ```bash
   docker compose exec nginx nginx -t
   ```

3. View Nginx error logs:
   ```bash
   docker compose logs nginx --tail 100
   ```

4. Verify certificate files exist:
   ```bash
   ls -la certbot/conf/live/api.simplifyingskills.live/
   ```

### HTTP to HTTPS Redirect Not Working

**Problem**: HTTP requests don't redirect to HTTPS

**Solutions**:
1. Check Nginx configuration in `nginx/app.conf`
2. Verify port 80 is accessible
3. Check Nginx logs for errors

### Certificate Renewal Failing

**Problem**: Automatic renewal fails

**Solutions**:
1. Test renewal manually:
   ```bash
   docker compose run --rm certbot renew --dry-run
   ```

2. Check if domain is still pointing to the correct IP
3. Verify ports 80 and 443 are still open
4. Review Certbot logs:
   ```bash
   docker compose logs certbot
   ```

## SSL Security Testing

### Test SSL Configuration

Use SSL Labs to test your SSL setup:

```
https://www.ssllabs.com/ssltest/analyze.html?d=api.simplifyingskills.live
```

You should aim for an **A or A+ rating**.

### Test Security Headers

Use SecurityHeaders.com:

```
https://securityheaders.com/?q=https://api.simplifyingskills.live
```

The Nginx configuration includes:
- Strict-Transport-Security (HSTS)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection

## Configuration Files

### File Structure

```
drema-ai/
├── nginx/
│   ├── nginx.conf          # Main Nginx config
│   └── app.conf            # Site config with SSL
├── certbot/
│   ├── conf/               # SSL certificates (auto-generated)
│   └── www/                # ACME challenge files
├── dhparam/
│   └── dhparam.pem         # DH parameters for security
├── docker-compose.yml      # Updated with Nginx and Certbot
├── init-letsencrypt.sh     # Initial setup script
└── renew-certificates.sh   # Manual renewal script
```

### Key Configuration Files

**nginx/app.conf**: Main Nginx configuration with SSL settings
- Handles HTTP to HTTPS redirect
- Proxies requests to Flask app
- Configures SSL certificates and security headers

**docker-compose.yml**: Docker services
- `drema-ai`: Flask application
- `nginx`: Reverse proxy with SSL
- `certbot`: Certificate management

## Additional Information

### Certificate Validity

- Let's Encrypt certificates are valid for **90 days**
- Auto-renewal triggers at **60 days** (30 days remaining)
- Certbot checks twice daily for renewals

### Rate Limits

Let's Encrypt has rate limits:
- 50 certificates per domain per week
- 5 duplicate certificates per week

Use `STAGING=1` in `init-letsencrypt.sh` for testing to avoid hitting limits.

### Logs Location

- **Nginx logs**: In Docker volume `nginx-logs`
- **Certbot logs**: In Docker volume `certbot-logs`
- **Flask app logs**: `./logs/` directory

View logs:
```bash
docker compose logs nginx
docker compose logs certbot
docker compose logs drema-ai
```

## Support

For issues related to:
- **Let's Encrypt**: https://community.letsencrypt.org/
- **Nginx**: https://nginx.org/en/docs/
- **Docker**: https://docs.docker.com/

---

**Last Updated**: December 2025
