# Environment Configuration Guide

**Created:** 2026-01-05
**Purpose:** Document environment variables for HealthRAG deployment

## Overview

HealthRAG uses environment variables to configure different deployment scenarios (local development, Docker, homelab production). This guide explains all environment variables and their usage.

## Configuration File Location

**Local & Docker:**
```
/Users/jasonewillis/Developer/jwRepos/JLWAI/HealthRAG/data/.env
```

**Homelab (CT 100):**
```
/opt/healthrag/data/.env
```

**Important:** The `.env` file is git-ignored for security. Never commit API keys or secrets to git.

---

## Environment Variables

### OLLAMA Configuration

**Variable:** `OLLAMA_BASE_URL`

**Purpose:** URL for Ollama LLM backend service

**Values:**

| Environment | Value | Notes |
|-------------|-------|-------|
| **Local Dev (Docker)** | `http://localhost:11434` | Default, Ollama bundled in container |
| **Local Dev (MLX)** | `http://localhost:11434` | Default, Ollama installed locally |
| **Homelab Production** | `http://192.168.0.211:11434` | Shared Ollama on CT 101 |

**Setting in docker-compose.homelab.yml:**
```yaml
services:
  healthrag:
    environment:
      - OLLAMA_BASE_URL=http://192.168.0.211:11434
```

**Setting in config/settings.py:**
```python
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
```

**Note:** For homelab, this is set in `docker-compose.homelab.yml`, not in `.env` file.

---

### USDA FoodData Central API

**Variable:** `USDA_FDC_API_KEY`

**Purpose:** API key for USDA FoodData Central nutrition database (400K foods)

**Required:** Yes (for food logging features)

**Get API Key:** https://fdc.nal.usda.gov/api-key-signup

**Account:** jasonewillis@gmail.com

**Example `.env` entry:**
```bash
# USDA FoodData Central API Key
# Get your free key at: https://fdc.nal.usda.gov/api-key-signup
# Account: jasonewillis@gmail.com
USDA_FDC_API_KEY=m1aOhdzpps15KKDWjpb9RE5tLKkKZUzUIivmZyvs
```

**Usage in code:**
```python
# src/food_api_fdc.py
import os
FDC_API_KEY = os.getenv("USDA_FDC_API_KEY")
```

---

### EDAMAM Food Database (Optional)

**Variables:** `EDAMAM_APP_ID`, `EDAMAM_APP_KEY`

**Purpose:** Premium food database API (paid/freemium alternative to USDA FDC)

**Required:** No (only if exceeding USDA free tier limits)

**Get Credentials:** https://developer.edamam.com/

**Example `.env` entry:**
```bash
# OPTIONAL: EDAMAM FOOD DATABASE (Premium Alternative)
# Only needed if you exceed USDA free tier limits
# Get API credentials at: https://developer.edamam.com/
# EDAMAM_APP_ID=your_app_id_here
# EDAMAM_APP_KEY=your_app_key_here
```

**Status:** Currently commented out, not used

---

## Complete `.env` File Template

**Location:** `data/.env`

```bash
# =================================================================
# HealthRAG Environment Configuration
# Created: 2025-XX-XX
# Updated: 2026-01-05 - Added homelab deployment configuration
# =================================================================

# =================================================================
# OLLAMA CONFIGURATION (Backend LLM Service)
# =================================================================

# For LOCAL development (Docker/MLX):
# OLLAMA_BASE_URL=http://localhost:11434  # Default, no need to set

# For HOMELAB deployment (set in docker-compose.homelab.yml):
# OLLAMA_BASE_URL=http://192.168.0.211:11434  # CT 101 Ollama service
# Note: This is configured in docker-compose.homelab.yml, not needed here

# =================================================================
# USDA FOODDATA CENTRAL API (Food Database)
# =================================================================

# Free API key for food nutrition data (400K foods)
# Get your key at: https://fdc.nal.usda.gov/api-key-signup
# Account: jasonewillis@gmail.com
USDA_FDC_API_KEY=your_api_key_here  # Replace with your actual key

# =================================================================
# DEPLOYMENT ENVIRONMENTS
# =================================================================

# Local Development:
# - Mac: MLX backend (native Apple Silicon)
# - Docker: Ollama bundled in container
# - Access: http://localhost:8501

# Homelab Production (Proxmox):
# - CT 100 (192.168.0.210): HealthRAG container
# - CT 101 (192.168.0.211): Shared Ollama service
# - Access: http://192.168.0.210:8501
# - Deployed: 2026-01-05

# =================================================================
# OPTIONAL: EDAMAM FOOD DATABASE (Premium Alternative)
# =================================================================

# Only needed if you exceed USDA free tier limits
# Get API credentials at: https://developer.edamam.com/
# EDAMAM_APP_ID=your_app_id_here
# EDAMAM_APP_KEY=your_app_key_here
```

---

## Environment-Specific Configuration

### Local Development (Mac/MLX)

**Setup:**
```bash
# 1. Copy .env.example to data/.env
cp .env.example data/.env

# 2. Add your USDA FDC API key
nano data/.env

# 3. Start application
./run_local_mlx.sh
```

**Expected behavior:**
- Ollama: Runs locally on port 11434
- Models: Downloaded to local machine
- Data: Stored in `data/` directory

---

### Local Development (Docker)

**Setup:**
```bash
# 1. Copy .env.example to data/.env
cp .env.example data/.env

# 2. Add your USDA FDC API key
nano data/.env

# 3. Start Docker containers
./start_healthrag.sh
```

**Expected behavior:**
- Ollama: Bundled in Docker container
- Models: Downloaded inside container (persistent via volume)
- Data: Mounted from host `data/` directory

---

### Homelab Production (Proxmox)

**Setup:**
```bash
# On your Mac (dev machine):

# 1. Ensure data/.env has USDA_FDC_API_KEY
nano data/.env

# 2. Deploy to homelab (includes .env sync)
./deploy-to-homelab.sh

# .env is automatically copied to CT 100:/opt/healthrag/data/.env
```

**Expected behavior:**
- Ollama: Shared service on CT 101 (192.168.0.211:11434)
- Models: Loaded once on CT 101, shared by all services
- Data: Persistent on CT 100 `/opt/healthrag/data/`
- OLLAMA_BASE_URL: Set in `docker-compose.homelab.yml` (not .env)

**Verify .env on homelab:**
```bash
ssh root@192.168.0.210
cat /opt/healthrag/data/.env
```

---

## Security Best Practices

### 1. Never Commit .env to Git

**Verify .env is ignored:**
```bash
# Check .gitignore
grep -E "\.env|.env.local" .gitignore

# Expected output:
# .env
# .env.local
```

### 2. Rotate API Keys Quarterly

**Schedule:**
- Review: Every 3 months (Jan, Apr, Jul, Oct)
- Rotate USDA_FDC_API_KEY if suspicious activity

**Process:**
1. Get new API key from https://fdc.nal.usda.gov/api-key-signup
2. Update `data/.env` locally
3. Re-deploy to homelab: `./deploy-to-homelab.sh`
4. Test food logging features
5. Delete old API key from USDA dashboard

### 3. Backup .env Securely

**.env is included in automated backups:**
```bash
# On CT 100, backups include .env
/opt/healthrag/backup-healthrag.sh
# Creates: /backups/healthrag/healthrag-YYYYMMDD_HHMMSS.tar.gz
# Includes: data/user_profile.json, data/workouts.db, data/food_log.db,
#           data/vectorstore/, data/.env
```

**Manual backup:**
```bash
# On CT 100
cp /opt/healthrag/data/.env /backups/healthrag/.env.backup-$(date +%Y%m%d)
```

### 4. Restrict File Permissions

**On homelab (CT 100):**
```bash
# Ensure .env is readable only by root
chmod 600 /opt/healthrag/data/.env
chown root:root /opt/healthrag/data/.env
```

---

## Troubleshooting

### Issue: "Ollama connection failed"

**Symptoms:**
- Error in UI: "Error connecting to Ollama: ..."
- Logs show connection timeout

**Solutions:**

1. **Verify OLLAMA_BASE_URL is correct:**
   ```bash
   # On CT 100
   docker compose -f docker-compose.homelab.yml exec healthrag env | grep OLLAMA
   # Expected: OLLAMA_BASE_URL=http://192.168.0.211:11434
   ```

2. **Test Ollama connectivity from container:**
   ```bash
   docker compose -f docker-compose.homelab.yml exec healthrag \
     curl http://192.168.0.211:11434/api/tags
   ```

3. **Verify Ollama is running on CT 101:**
   ```bash
   ssh root@192.168.0.211
   curl http://localhost:11434/api/tags
   ```

---

### Issue: "USDA FDC API key invalid"

**Symptoms:**
- Food search returns no results
- Error: "401 Unauthorized" or "403 Forbidden"

**Solutions:**

1. **Verify API key is set:**
   ```bash
   # On CT 100
   docker compose -f docker-compose.homelab.yml exec healthrag \
     python3 -c "import os; print(os.getenv('USDA_FDC_API_KEY', 'NOT SET'))"
   ```

2. **Check .env file exists and has key:**
   ```bash
   ssh root@192.168.0.210
   cat /opt/healthrag/data/.env | grep USDA_FDC_API_KEY
   ```

3. **Re-deploy with updated .env:**
   ```bash
   # On Mac
   nano data/.env  # Add/update USDA_FDC_API_KEY
   ./deploy-to-homelab.sh  # Re-deploy
   ```

4. **Get new API key if expired:**
   - Visit: https://fdc.nal.usda.gov/api-key-signup
   - Email: jasonewillis@gmail.com
   - Copy new key to `data/.env`

---

### Issue: ".env not synced to homelab"

**Symptoms:**
- Local `.env` has API keys but homelab doesn't

**Solution:**

```bash
# Manual sync from Mac to CT 100
scp data/.env root@192.168.0.210:/opt/healthrag/data/.env

# Restart container to load new .env
ssh root@192.168.0.210 \
  'cd /opt/healthrag && docker compose -f docker-compose.homelab.yml restart'
```

---

## Adding New Environment Variables

### Step 1: Update .env File

```bash
# data/.env
NEW_API_KEY=your_value_here
```

### Step 2: Update .env.example (for documentation)

```bash
# .env.example
# Description of what this is for
# NEW_API_KEY=your_api_key_here
```

### Step 3: Update This Documentation

Add section to this file explaining the new variable.

### Step 4: Update Code to Read Variable

```python
# src/your_module.py
import os

NEW_API_KEY = os.getenv("NEW_API_KEY")
if not NEW_API_KEY:
    raise ValueError("NEW_API_KEY not set in environment")
```

### Step 5: Update docker-compose.homelab.yml (if needed)

```yaml
services:
  healthrag:
    environment:
      - NEW_API_KEY=${NEW_API_KEY}
```

### Step 6: Re-deploy

```bash
# Local testing
./run_local_mlx.sh

# Homelab deployment
./deploy-to-homelab.sh
```

---

## References

- **USDA FDC API Docs:** https://fdc.nal.usda.gov/api-guide.html
- **Edamam API Docs:** https://developer.edamam.com/food-database-api-docs
- **Ollama API Docs:** https://github.com/ollama/ollama/blob/main/docs/api.md
- **Docker Environment Variables:** https://docs.docker.com/compose/environment-variables/

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-05 | Initial documentation, added homelab deployment info | Claude |
| 2025-XX-XX | Created .env file with USDA_FDC_API_KEY | Jason |
