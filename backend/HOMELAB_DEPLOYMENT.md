# HealthRAG Backend - Homelab Deployment Guide

Deploy the HealthRAG FastAPI backend to your homelab server with local and remote access.

**Target Environment**: Windows Mini PC (jwWinMin) at 192.168.0.64

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Local Network Only)](#quick-start-local-network-only)
3. [Remote Access Setup](#remote-access-setup)
   - [Option 1: Cloudflare Tunnel (Recommended)](#option-1-cloudflare-tunnel-recommended)
   - [Option 2: Tailscale VPN (Private Access)](#option-2-tailscale-vpn-private-access)
   - [Option 3: Traditional Reverse Proxy](#option-3-traditional-reverse-proxy)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Testing](#testing)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### On Your Development Machine

- SSH access to homelab server: `ssh jwadmin@192.168.0.64`
- Git (to clone/pull repository)

### On Homelab Server (jwWinMin)

- ✅ Windows 10/11 with WSL2 installed
- ✅ Docker Desktop for Windows (or Docker in WSL2)
- ✅ Git

**Check Docker**:
```bash
ssh jwadmin@192.168.0.64
docker --version
docker-compose --version
```

If Docker is not installed, install Docker Desktop: https://www.docker.com/products/docker-desktop/

### External Services (Free Tier)

- **Supabase Account** (authentication): https://supabase.com/
- **USDA FDC API Key** (optional, food search): https://fdc.nal.usda.gov/api-key-signup

---

## Quick Start (Local Network Only)

This gets the backend running on your local network (accessible at `http://192.168.0.64:8000`).

### Step 1: SSH to Homelab Server

```bash
ssh jwadmin@192.168.0.64
```

### Step 2: Clone Repository (or Pull Latest)

```bash
# If not already cloned:
cd ~
git clone https://github.com/YOUR_USERNAME/HealthRAG.git
cd HealthRAG/backend

# If already cloned, pull latest:
cd ~/HealthRAG/backend
git pull origin main
```

### Step 3: Create Environment File

```bash
cp .env.homelab.example .env
nano .env  # or use vim, code, etc.
```

**Required Configuration**:
```bash
# Database password (make it secure!)
DB_PASSWORD=your-secure-password-here

# Supabase (get from https://app.supabase.com/project/_/settings/api)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-generated-secret-key

# Optional: USDA API Key
USDA_FDC_API_KEY=your-fdc-api-key
```

**Generate JWT Secret**:
```bash
openssl rand -hex 32
```

### Step 4: Start Services

```bash
docker-compose up -d
```

This will:
- Pull PostgreSQL and build the FastAPI backend
- Create persistent volume for database
- Start both services
- Expose API on port 8000

### Step 5: Verify Deployment

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f healthrag-api

# Test health endpoint
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "HealthRAG API",
  "version": "0.1.0",
  "environment": "production"
}
```

### Step 6: Access API

**On Local Network**:
- API: http://192.168.0.64:8000
- Swagger Docs: http://192.168.0.64:8000/docs
- ReDoc: http://192.168.0.64:8000/redoc

**From Development Machine**:
```bash
curl http://192.168.0.64:8000/health
```

---

## Remote Access Setup

Choose ONE of these options for remote access (accessing from outside your home network):

### Option 1: Cloudflare Tunnel (Recommended)

**Pros**:
- ✅ Free forever
- ✅ No port forwarding needed
- ✅ Automatic HTTPS with Cloudflare SSL
- ✅ DDoS protection included
- ✅ No dynamic DNS needed
- ✅ Works behind CGNAT

**Cons**:
- ❌ Requires a domain name (~$10/year)
- ❌ Traffic routes through Cloudflare

**Setup**:

#### 1. Get a Domain Name

Register a cheap domain (~$10/year):
- Cloudflare Registrar: https://www.cloudflare.com/products/registrar/
- Namecheap: https://www.namecheap.com/
- Porkbun: https://porkbun.com/

#### 2. Add Domain to Cloudflare

1. Sign up at https://dash.cloudflare.com/
2. Add your domain
3. Update nameservers at your registrar to Cloudflare's nameservers

#### 3. Install Cloudflare Tunnel on Homelab

```bash
ssh jwadmin@192.168.0.64

# Download cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe

# Authenticate
./cloudflared-windows-amd64.exe tunnel login

# Create tunnel
./cloudflared-windows-amd64.exe tunnel create healthrag

# Note the Tunnel ID from output
```

#### 4. Configure Tunnel

Create `tunnel-config.yml`:
```yaml
tunnel: YOUR_TUNNEL_ID_HERE
credentials-file: C:\Users\jwadmin\.cloudflared\YOUR_TUNNEL_ID.json

ingress:
  - hostname: healthrag.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

#### 5. Create DNS Record

```bash
./cloudflared-windows-amd64.exe tunnel route dns healthrag healthrag.yourdomain.com
```

#### 6. Run Tunnel

```bash
# Test first
./cloudflared-windows-amd64.exe tunnel --config tunnel-config.yml run

# If working, install as service
./cloudflared-windows-amd64.exe service install
```

#### 7. Update CORS Origins

Edit `backend/.env`:
```bash
CORS_ORIGINS=http://localhost:3000,http://192.168.0.64:3000,https://healthrag.yourdomain.com
DOMAIN=healthrag.yourdomain.com
```

Restart backend:
```bash
cd ~/HealthRAG/backend
docker-compose restart healthrag-api
```

#### 8. Access Remotely

- API: https://healthrag.yourdomain.com
- Swagger: https://healthrag.yourdomain.com/docs

**Complete Guide**: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

---

### Option 2: Tailscale VPN (Private Access)

**Pros**:
- ✅ Free for personal use (up to 100 devices)
- ✅ Zero-trust security
- ✅ No port forwarding needed
- ✅ Works on all devices (iOS, Android, Windows, Mac, Linux)
- ✅ Private access only (not exposed to internet)
- ✅ Automatic HTTPS with Tailscale TLS certificates

**Cons**:
- ❌ Requires Tailscale client on every device
- ❌ Not suitable for public APIs

**Setup**:

#### 1. Install Tailscale on Homelab Server

```bash
ssh jwadmin@192.168.0.64

# Download and install Tailscale for Windows
# Visit: https://tailscale.com/download/windows
```

#### 2. Enable MagicDNS

1. Go to https://login.tailscale.com/admin/dns
2. Enable MagicDNS
3. Note your tailnet name (e.g., `tail12345.ts.net`)

#### 3. Install Tailscale on Your Phone/Laptop

- iOS: https://apps.apple.com/us/app/tailscale/id1470499037
- Android: https://play.google.com/store/apps/details?id=com.tailscale.ipn
- Mac: https://tailscale.com/download/mac
- Windows: https://tailscale.com/download/windows

#### 4. Access API via Tailscale

Once connected to Tailscale:
- API: `http://jwwinmin:8000` (MagicDNS hostname)
- Swagger: `http://jwwinmin:8000/docs`

Or use the Tailscale IP directly:
```bash
tailscale status  # Get homelab server's Tailscale IP
curl http://100.x.x.x:8000/health
```

#### 5. (Optional) Enable HTTPS with Tailscale TLS

```bash
# On homelab server
tailscale cert jwwinmin.tail12345.ts.net
```

This generates TLS certificates. Update `docker-compose.yml` to use HTTPS.

**Complete Guide**: https://tailscale.com/kb/1017/install/

---

### Option 3: Traditional Reverse Proxy + DDNS

**Pros**:
- ✅ Full control over infrastructure
- ✅ Works with existing reverse proxy setup

**Cons**:
- ❌ Requires port forwarding (security risk)
- ❌ Requires dynamic DNS service
- ❌ More complex setup
- ❌ Doesn't work behind CGNAT

**Setup** (if you already have Nginx/Caddy):

#### 1. Port Forward Router

Forward port 443 (HTTPS) to your homelab server's IP (192.168.0.64).

#### 2. Setup Dynamic DNS

Use a DDNS service:
- DuckDNS (free): https://www.duckdns.org/
- No-IP (free): https://www.noip.com/

#### 3. Configure Reverse Proxy

**Example Nginx Config** (`/etc/nginx/sites-available/healthrag`):
```nginx
server {
    listen 80;
    server_name healthrag.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name healthrag.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/healthrag.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/healthrag.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 4. Get SSL Certificate

```bash
sudo certbot --nginx -d healthrag.yourdomain.com
```

---

## Configuration

### Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_PASSWORD` | PostgreSQL password | ✅ Yes | - |
| `SUPABASE_URL` | Supabase project URL | ✅ Yes | - |
| `SUPABASE_KEY` | Supabase anon key | ✅ Yes | - |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | ✅ Yes | - |
| `JWT_SECRET_KEY` | JWT signing secret | ✅ Yes | - |
| `JWT_ALGORITHM` | JWT algorithm | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | No | `15` |
| `CORS_ORIGINS` | Allowed origins | No | See `.env` |
| `USDA_FDC_API_KEY` | USDA Food API key | No | - |
| `DOMAIN` | Remote access domain | No | `healthrag.local` |

### Database Backup

**Backup Script** (`backup-db.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/home/jwadmin/backups/healthrag"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
docker exec healthrag-db pg_dump -U healthrag healthrag | gzip > $BACKUP_DIR/healthrag_$TIMESTAMP.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "healthrag_*.sql.gz" -mtime +7 -delete

echo "Backup completed: healthrag_$TIMESTAMP.sql.gz"
```

**Schedule with Windows Task Scheduler** (runs daily at 2 AM):
```powershell
# On homelab server
schtasks /create /tn "HealthRAG Backup" /tr "wsl bash /home/jwadmin/backup-db.sh" /sc daily /st 02:00
```

---

## Deployment

### Initial Deployment

```bash
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Update Deployment (New Code)

```bash
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Verify
docker-compose logs -f healthrag-api
```

### Database Migrations

If database schema changes:
```bash
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend

# Run migrations
docker-compose exec healthrag-api python -c "from models.database import init_db; init_db()"
```

---

## Testing

### Health Check

```bash
# Local network
curl http://192.168.0.64:8000/health

# Remote (Cloudflare Tunnel)
curl https://healthrag.yourdomain.com/health

# Remote (Tailscale)
curl http://jwwinmin:8000/health
```

### API Documentation

- **Swagger UI**: http://192.168.0.64:8000/docs
- **ReDoc**: http://192.168.0.64:8000/redoc

### Full Integration Test

1. Import Postman collection: `HealthRAG_API.postman_collection.json`
2. Import environment: `HealthRAG_Local.postman_environment.json`
3. Update `base_url` to:
   - Local: `http://192.168.0.64:8000`
   - Remote: `https://healthrag.yourdomain.com`
4. Run collection

---

## Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# API only
docker-compose logs -f healthrag-api

# Database only
docker-compose logs -f healthrag-db
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart API only
docker-compose restart healthrag-api
```

### Stop Services

```bash
docker-compose down
```

### Update Docker Images

```bash
# Pull latest PostgreSQL
docker-compose pull

# Rebuild API
docker-compose up -d --build
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it healthrag-db psql -U healthrag -d healthrag

# Example queries
SELECT COUNT(*) FROM workout_sessions;
SELECT * FROM user_profiles LIMIT 5;
```

---

## Troubleshooting

### Port 8000 Already in Use

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Cannot Connect to Database

```bash
# Check database is running
docker-compose ps healthrag-db

# Check database logs
docker-compose logs healthrag-db

# Test connection
docker exec -it healthrag-db psql -U healthrag -d healthrag
```

### API Returns 500 Errors

```bash
# Check API logs
docker-compose logs -f healthrag-api

# Common issues:
# 1. Missing environment variables
# 2. Database connection failed
# 3. Supabase credentials incorrect
```

### Cloudflare Tunnel Not Working

```bash
# Check tunnel status
./cloudflared-windows-amd64.exe tunnel info healthrag

# Check tunnel logs
# Windows: Event Viewer > Applications and Services Logs > Cloudflare

# Restart tunnel service
net stop cloudflared
net start cloudflared
```

### Tailscale Connection Issues

```bash
# Check Tailscale status
tailscale status

# Restart Tailscale
tailscale down
tailscale up
```

### CORS Errors

**Symptom**: Browser shows "CORS policy: No 'Access-Control-Allow-Origin' header"

**Fix**: Update `.env` with your frontend URL:
```bash
CORS_ORIGINS=http://localhost:3000,https://healthrag.yourdomain.com
```

Then restart:
```bash
docker-compose restart healthrag-api
```

---

## Cost Estimate

### Homelab Deployment

**Total Monthly Cost**: **$0-13/month**

| Service | Cost | Notes |
|---------|------|-------|
| Homelab Server | $0 | You already own it |
| Electricity (~20W) | ~$2/month | 24/7 operation |
| Internet | $0 | You already pay for it |
| Supabase (Free Tier) | $0 | 50K MAU, 500MB database |
| USDA FDC API | $0 | Free forever |
| **Remote Access** | | |
| Cloudflare Tunnel | $0 | Free forever |
| Domain Name | ~$10/year | Or use DuckDNS (free) |
| **OR Tailscale** | $0 | Free for personal use |

**vs. Cloud Deployment**: Render.com starter plan = $7/month + database $7/month = **$14/month = $168/year**

**Annual Savings**: **$150-160/year** by self-hosting

---

## Security Best Practices

1. **Use Strong Passwords**:
   - Database: 20+ characters, random
   - JWT Secret: Generated with `openssl rand -hex 32`

2. **Keep Supabase Keys Secret**:
   - Never commit `.env` to git
   - Use service role key only on backend (never frontend)

3. **Enable Automatic Updates**:
   ```bash
   # Update Docker images weekly
   docker-compose pull && docker-compose up -d
   ```

4. **Firewall Rules** (if using port forwarding):
   - Only open port 443 (HTTPS)
   - Block all other inbound ports

5. **Monitor Logs**:
   ```bash
   # Check for suspicious activity
   docker-compose logs --tail=100 healthrag-api | grep "401\|403\|500"
   ```

6. **Regular Backups**:
   - Schedule daily database backups
   - Store backups off-server (cloud storage, external drive)

---

## Next Steps

1. **Deploy Backend** ✅ (you're here)
2. **Test APIs** with Postman
3. **Deploy Frontend** (Streamlit or React Native mobile app)
4. **Setup Monitoring** (Uptime Kuma, Prometheus)
5. **Automate Backups** (daily cron job)

---

## Support & Documentation

- **Backend API Docs**: http://192.168.0.64:8000/docs
- **Cloudflare Tunnel Docs**: https://developers.cloudflare.com/cloudflare-one/
- **Tailscale Docs**: https://tailscale.com/kb/
- **Docker Compose Docs**: https://docs.docker.com/compose/
- **HealthRAG Issues**: https://github.com/YOUR_USERNAME/HealthRAG/issues
