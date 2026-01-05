# HealthRAG Homelab Deployment Guide

**Created:** 2026-01-04
**Target Infrastructure:** jwBeast Proxmox Homelab

## Overview

This guide deploys HealthRAG to your Proxmox homelab using a **microservices architecture**:
- **CT 100 (Docker Host)**: 192.168.0.210 - Runs lightweight HealthRAG container
- **CT 101 (Ollama)**: 192.168.0.211 - Provides shared LLM inference (Agents-as-a-Service)

## Architecture: Shared Ollama (Microservices)

```
┌─────────────────────────────────────────────────────────────┐
│ jwBeast Proxmox Host (192.168.0.201)                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ CT 101: Ollama Service (192.168.0.211)                 │ │
│  │ - Ollama Server (port 11434)                           │ │
│  │ - Models: qwen2.5-coder:14b (9GB), llama3.1:8b (5GB)   │ │
│  │ - 8 CPU, 48GB RAM                                      │ │
│  │ - Handles: GitHub agents, HealthRAG, future services   │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↑ HTTP API (port 11434)            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ CT 100: Docker Host (192.168.0.210)                    │ │
│  │ ┌──────────────────────────────────────────────────┐   │ │
│  │ │ HealthRAG Container                              │   │ │
│  │ │ - Streamlit UI (port 8501)                       │   │ │
│  │ │ - RAG System (ChromaDB, HuggingFace embeddings)  │   │ │
│  │ │ - Lightweight (~2GB RAM)                         │   │ │
│  │ └──────────────────────────────────────────────────┘   │ │
│  │ ┌──────────────────────────────────────────────────┐   │ │
│  │ │ Future Services (GitHub Agents, etc.)            │   │ │
│  │ └──────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

User → http://192.168.0.210:8501 → HealthRAG UI
                 ↓
    http://192.168.0.211:11434 → Ollama API → LLM Inference
```

### Why Shared Ollama?

**✅ Resource Efficient:**
- Models loaded once (14GB total vs. 14GB × N containers)
- CT 101 optimized for LLM inference (48GB RAM, 8 CPU)
- HealthRAG container stays lightweight (~2GB)

**✅ Scalable:**
- Add new services without duplicating models
- GitHub agents, meal planners, workout analyzers all share backend

**✅ Maintainable:**
- Update models once (Ollama pull), all services benefit
- Consistent model versions across services

**⚠️ Trade-offs:**
- Single point of failure (mitigated with systemd auto-restart)
- Potential concurrency bottleneck (Ollama queues requests)
- Network dependency (CT 100 → CT 101, but local LAN = sub-ms latency)

## Prerequisites

### 1. Verify Proxmox Access

```bash
ssh root@192.168.0.201
# Password: jwPr0xM0x (from homelab configs/.env)
```

### 2. Verify Ollama is Running (CT 101)

```bash
# SSH to Ollama container
ssh root@192.168.0.211

# Check Ollama status
ps aux | grep ollama
# OR if running as systemd service:
# systemctl status ollama

# List installed models
ollama list
# Expected: qwen2.5-coder:14b, llama3.1:8b

# Test API
curl http://localhost:11434/api/tags
# Should return JSON with model list
```

**If Ollama is not running:**
```bash
# Install Ollama (if not installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve &

# Pull models
ollama pull llama3.1:8b        # 4.9GB - Fast, good quality
ollama pull qwen2.5-coder:14b  # 9GB - Better for technical queries
```

### 3. Verify Docker Host (CT 100)

```bash
# SSH to Docker host
ssh root@192.168.0.210
# Password: jwD0ck3r! (from homelab configs/.env)

# Verify Docker
docker --version       # Expected: v29.1.3
docker compose version # Expected: v5.0.1

# Test connectivity to Ollama
curl http://192.168.0.211:11434/api/tags
# Should return model list (confirms network connectivity)
```

## Deployment Steps

### Step 1: Transfer HealthRAG to Docker Host

**Option A: Clone from GitHub (Recommended if repo is public)**

```bash
# SSH to CT 100
ssh root@192.168.0.210

# Create project directory
mkdir -p /opt/healthrag
cd /opt/healthrag

# Clone repository
git clone https://github.com/YOUR_USERNAME/HealthRAG.git .
```

**Option B: SCP from Dev Machine (For private repo or local changes)**

```bash
# Run from your Mac
cd /Users/jasonewillis/Developer/jwRepos/JLWAI/HealthRAG

# Transfer entire project
scp -r . root@192.168.0.210:/opt/healthrag/

# Alternatively, use rsync (faster, excludes .git)
rsync -avz --exclude='.git' --exclude='venv*' --exclude='data/vectorstore' \
  . root@192.168.0.210:/opt/healthrag/
```

### Step 2: Prepare Data Directory

```bash
# SSH to CT 100
ssh root@192.168.0.210
cd /opt/healthrag

# Create data directories
mkdir -p data/pdfs data/vectorstore

# Set permissions
chmod -R 755 data/

# If PDFs are not in repo, transfer them
# From Mac:
# scp /Users/jasonewillis/Developer/jwRepos/JLWAI/HealthRAG/data/pdfs/*.pdf \
#   root@192.168.0.210:/opt/healthrag/data/pdfs/
```

### Step 3: Configure Environment (Optional)

```bash
# On CT 100
cd /opt/healthrag

# Create .env file for USDA FDC API key (optional)
cat > data/.env << 'EOF'
# USDA FoodData Central API Key (optional, for food database)
# Get free key: https://fdc.nal.usda.gov/api-key-signup.html
FDC_API_KEY=your_api_key_here
EOF

chmod 600 data/.env
```

**Note:** Ollama URL is already set in `docker-compose.homelab.yml`:
```yaml
environment:
  - OLLAMA_BASE_URL=http://192.168.0.211:11434
```

### Step 4: Build and Deploy

```bash
# On CT 100
cd /opt/healthrag

# Build the container (lightweight, ~1GB image)
docker compose -f docker-compose.homelab.yml build

# Start the service
docker compose -f docker-compose.homelab.yml up -d

# Check logs
docker compose -f docker-compose.homelab.yml logs -f healthrag
```

**Expected Output:**
```
healthrag  | Streamlit starting on port 8501...
healthrag  | Backend: ollama (http://192.168.0.211:11434)
healthrag  | VectorStore loaded from data/vectorstore/
```

### Step 5: Process PDFs (First-Time Setup)

```bash
# On CT 100
cd /opt/healthrag

# Execute inside the container to build vectorstore
docker compose -f docker-compose.homelab.yml exec healthrag python3 process_pdfs.py

# This will:
# - Load all PDFs from data/pdfs/ (28 files: RP, Nippard, BFFM)
# - Create embeddings using sentence-transformers/all-MiniLM-L6-v2
# - Store in data/vectorstore/ (ChromaDB)
# - Takes ~5-10 minutes depending on PDF count
```

**Note:** If vectorstore already exists (transferred from dev machine), this step is optional.

### Step 6: Access the Application

**From any device on your network:**
```
http://192.168.0.210:8501
```

**From Proxmox host:**
```bash
ssh root@192.168.0.201
curl http://192.168.0.210:8501/_stcore/health
```

## Verification

### 1. Check Container Status

```bash
# On CT 100
docker ps
# Should show: healthrag container, port 8501, status Up

docker compose -f docker-compose.homelab.yml ps
# Should show: healthrag, state running

docker compose -f docker-compose.homelab.yml logs --tail 50 healthrag
# Check for errors
```

### 2. Test Ollama Connectivity

```bash
# From inside HealthRAG container
docker compose -f docker-compose.homelab.yml exec healthrag \
  curl http://192.168.0.211:11434/api/tags

# Should return JSON with models: llama3.1:8b, qwen2.5-coder:14b
```

### 3. Test HealthRAG

1. **Open UI**: http://192.168.0.210:8501
2. **Select Backend**: Choose "Ollama" (should be default)
3. **Create Profile**: Fill out user profile (sidebar)
4. **Ask Question**: "What is the best way to build muscle?"
5. **Verify Response**:
   - Should cite sources (Renaissance Periodization, Jeff Nippard)
   - Should be personalized to your profile
   - Check logs for Ollama API calls

### 4. Monitor Resources

```bash
# On CT 100 - Check HealthRAG container
docker stats healthrag
# Should show ~2GB RAM, low CPU when idle

# On CT 101 - Check Ollama during inference
ssh root@192.168.0.211
htop
# During query: CPU spikes, RAM holds models (~14GB)
```

## Maintenance

### View Logs

```bash
# Real-time logs
docker compose -f docker-compose.homelab.yml logs -f healthrag

# Last 100 lines
docker compose -f docker-compose.homelab.yml logs --tail 100 healthrag

# Filter for errors
docker compose -f docker-compose.homelab.yml logs healthrag | grep -i error
```

### Restart Container

```bash
# Restart HealthRAG
docker compose -f docker-compose.homelab.yml restart healthrag

# Full restart (rebuilds if needed)
docker compose -f docker-compose.homelab.yml down
docker compose -f docker-compose.homelab.yml up -d
```

### Update Application

```bash
# On CT 100
cd /opt/healthrag

# Pull latest code (if using git)
git pull

# Rebuild and restart
docker compose -f docker-compose.homelab.yml down
docker compose -f docker-compose.homelab.yml build --no-cache
docker compose -f docker-compose.homelab.yml up -d

# OR transfer updated files via SCP (from Mac)
# Then rebuild as above
```

### Backup Data

```bash
# On CT 100
cd /opt/healthrag

# Backup user data (profiles, workout logs, food logs, vectorstore)
tar -czf healthrag-backup-$(date +%Y%m%d).tar.gz data/

# Copy to Proxmox host for safekeeping
scp healthrag-backup-*.tar.gz root@192.168.0.201:/var/lib/vz/dump/

# OR copy to homelab backups directory
# scp healthrag-backup-*.tar.gz root@192.168.0.201:/backups/healthrag/
```

### Rebuild VectorStore

```bash
# If PDFs change or vectorstore is corrupted
docker compose -f docker-compose.homelab.yml exec healthrag rm -rf data/vectorstore/
docker compose -f docker-compose.homelab.yml exec healthrag python3 process_pdfs.py

# Restart container to reload
docker compose -f docker-compose.homelab.yml restart healthrag
```

### Cleanup Old Images

```bash
# Remove unused Docker images
docker image prune -a

# View disk usage
docker system df
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker compose -f docker-compose.homelab.yml logs healthrag

# Common issues:
# 1. Port 8501 already in use
netstat -tulpn | grep 8501
# Solution: Change port in docker-compose.homelab.yml or kill conflicting process

# 2. Data directory permissions
ls -la data/
# Solution: chmod -R 755 data/

# 3. Missing requirements
docker compose -f docker-compose.homelab.yml build --no-cache
```

### Can't Connect to Ollama

```bash
# 1. Verify Ollama is running on CT 101
ssh root@192.168.0.211
ps aux | grep ollama
curl http://localhost:11434/api/tags

# 2. Test connectivity from CT 100
ssh root@192.168.0.210
curl http://192.168.0.211:11434/api/tags

# 3. Check firewall (Proxmox should allow internal traffic)
# On Proxmox host:
iptables -L -n | grep 11434

# 4. Check Ollama logs on CT 101
journalctl -u ollama -f  # If running as systemd service
```

### Slow Performance

```bash
# 1. Check HealthRAG container resources
docker stats healthrag

# 2. Check Ollama resources on CT 101
ssh root@192.168.0.211
htop

# 3. Check model size
ollama list
# llama3.1:8b (5GB) = faster
# qwen2.5-coder:14b (9GB) = slower but better quality

# 4. Consider switching to smaller model in UI
# Settings → Model → llama3.1:8b
```

### Ollama Out of Memory

```bash
# On CT 101
free -h
# If using >40GB with both models loaded

# Solutions:
# 1. Unload unused model
ollama rm qwen2.5-coder:14b  # Keep only 8B model

# 2. Increase CT 101 RAM in Proxmox
# Web UI → CT 101 → Resources → Memory → Set to 64GB

# 3. Restart Ollama
pkill ollama
ollama serve &
```

### Database Corruption

```bash
# Reset workout/food databases (WARNING: Deletes all logs)
docker compose -f docker-compose.homelab.yml exec healthrag rm -f data/workouts.db data/food_log.db

# Restart to recreate DBs
docker compose -f docker-compose.homelab.yml restart healthrag

# Verify DBs recreated
docker compose -f docker-compose.homelab.yml exec healthrag ls -lh data/*.db
```

### VectorStore Errors

```bash
# Rebuild from scratch
docker compose -f docker-compose.homelab.yml exec healthrag rm -rf data/vectorstore/
docker compose -f docker-compose.homelab.yml exec healthrag python3 process_pdfs.py

# If PDFs are missing
# Transfer from dev machine:
# scp /path/to/pdfs/*.pdf root@192.168.0.210:/opt/healthrag/data/pdfs/
```

## Performance Tuning

### Model Selection

In the HealthRAG UI (Settings → Backend/Model):
- **llama3.1:8b** - Faster (~5-6 tok/sec), good quality, 5GB RAM
- **qwen2.5-coder:14b** - Slower (~3-4 tok/sec), better quality, 9GB RAM

**Recommendation:** Use 8B for general queries, 14B for program generation.

### Container Resources

Limit HealthRAG resources if needed (edit `docker-compose.homelab.yml`):

```yaml
services:
  healthrag:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Ollama Concurrency

If running multiple services, configure Ollama on CT 101:

```bash
# On CT 101, create /etc/systemd/system/ollama.service
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/ollama serve
Environment="OLLAMA_NUM_PARALLEL=4"  # Handle 4 concurrent requests
Environment="OLLAMA_MAX_LOADED_MODELS=2"  # Keep 2 models in RAM
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable ollama
systemctl restart ollama
```

## Security Considerations

### 1. Firewall / External Access

**Current:** HealthRAG accessible on LAN (192.168.0.210:8501)

**For external access:**
```bash
# On Proxmox or router, forward port
# External → 192.168.0.1:8501 → 192.168.0.210:8501

# Better: Use reverse proxy with HTTPS + authentication
```

### 2. HTTPS with Reverse Proxy

Consider adding Nginx on CT 100:

```bash
# Install Nginx
apt-get install nginx certbot python3-certbot-nginx

# Configure reverse proxy
cat > /etc/nginx/sites-available/healthrag << 'EOF'
server {
    listen 80;
    server_name healthrag.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
EOF

ln -s /etc/nginx/sites-available/healthrag /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d healthrag.yourdomain.com
```

### 3. Authentication

**HealthRAG has no built-in auth.** Options:
- **Nginx basic auth** (simple)
- **Authelia/Authentik** (advanced SSO)
- **Tailscale/WireGuard** (VPN access only)

### 4. API Keys

**USDA FDC API Key:** Store in `data/.env`, not in docker-compose.yml
```bash
# data/.env
FDC_API_KEY=your_secret_key_here
```

## Monitoring & Automation

### Health Checks

```bash
# Add to crontab on CT 100
crontab -e

# Check HealthRAG every 5 minutes
*/5 * * * * curl -f http://localhost:8501/_stcore/health || docker compose -f /opt/healthrag/docker-compose.homelab.yml restart healthrag
```

### Automated Backups

```bash
# Add to crontab on CT 100
0 2 * * * cd /opt/healthrag && tar -czf /backups/healthrag-$(date +\%Y\%m\%d).tar.gz data/ && find /backups -name "healthrag-*.tar.gz" -mtime +30 -delete
```

### Resource Monitoring

Consider integrating with Prometheus/Grafana if you set up monitoring:

```yaml
# Add to docker-compose.homelab.yml
services:
  healthrag:
    # ... existing config ...
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=8501"
```

## Cost Analysis

**Homelab (Shared Ollama):**
- CT 100: 2-4GB RAM (HealthRAG)
- CT 101: 14GB RAM (models) + inference CPU
- **Total: ~18GB RAM, efficient**

**Alternative (Self-Contained):**
- Each container: 14GB (models) + 2GB (app) = 16GB
- 3 services: 48GB RAM required
- **Won't fit on CT 100 (16GB limit!)**

**Annual Savings vs. Cloud:**
- Ollama local: FREE
- Cloud LLM (GPT-4, Claude): $0.01-0.10/1K tokens
- 100K queries/year × 1K tokens avg = $1,000-10,000/year
- **Homelab pays for itself in 1-2 years!**

## Next Steps

1. **Test with Real Workouts**: Log workouts, track progress
2. **Add More Services**: GitHub agents, meal planners (all use shared Ollama)
3. **Set Up Monitoring**: Prometheus + Grafana for resource tracking
4. **Enable HTTPS**: Add Nginx reverse proxy with SSL
5. **Automate Backups**: Cron job to backup data directory
6. **Mobile Access**: Tailscale or WireGuard for remote access

## References

- **Homelab .env**: `/Users/jasonewillis/homelab/configs/.env`
- **HealthRAG CLAUDE.md**: `/Users/jasonewillis/Developer/jwRepos/JLWAI/HealthRAG/CLAUDE.md`
- **Proxmox Web UI**: https://192.168.0.201:8006
- **Docker Host SSH**: `ssh root@192.168.0.210`
- **Ollama Host SSH**: `ssh root@192.168.0.211`

---

**Deployment Checklist:**

- [ ] Verify Ollama running on CT 101 (192.168.0.211)
- [ ] Transfer HealthRAG to CT 100 (192.168.0.210)
- [ ] Copy PDFs to data/pdfs/ directory
- [ ] Build Docker image: `docker compose -f docker-compose.homelab.yml build`
- [ ] Start container: `docker compose -f docker-compose.homelab.yml up -d`
- [ ] Process PDFs: `docker compose exec healthrag python3 process_pdfs.py`
- [ ] Access UI: http://192.168.0.210:8501
- [ ] Create user profile and test query
- [ ] Set up automated backups
- [ ] Document in homelab README
