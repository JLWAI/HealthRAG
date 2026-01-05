# Future Services Architecture - Shared Ollama Backend

**Created:** 2026-01-05
**Status:** Planning Phase
**Current:** HealthRAG deployed, Ollama serving 4 models

## Overview

This document outlines the microservices architecture for future JLWAI services that share the Ollama backend on CT 101. The goal is to build a suite of AI-powered health, fitness, and automation services that leverage the same LLM infrastructure.

## Current Architecture (Deployed 2026-01-05)

```
┌─────────────────────────────────────────────────────────────┐
│ jwBeast Proxmox Host (192.168.0.201)                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ CT 101: Ollama Service (192.168.0.211:11434)           │ │
│  │ - Models: llama3.1:8b, qwen2.5-coder:14b, phi4:14b,    │ │
│  │           deepseek-coder-v2:16b, mixtral:8x7b          │ │
│  │ - 8 CPU, 48GB RAM                                      │ │
│  │ - Status: Production-ready                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↑ HTTP API (11434)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ CT 100: Docker Host (192.168.0.210)                    │ │
│  │ ┌──────────────────────────────────────────────────┐   │ │
│  │ │ HealthRAG Container (DEPLOYED)                   │   │ │
│  │ │ - Port: 8501                                     │   │ │
│  │ │ - Memory: ~103 MB                                │   │ │
│  │ │ - Status: Healthy, serving users                 │   │ │
│  │ └──────────────────────────────────────────────────┘   │ │
│  │                                                          │ │
│  │ ┌──────────────────────────────────────────────────┐   │ │
│  │ │ Future Services (Planned)                        │   │ │
│  │ │ - GitHub Agents                                  │   │ │
│  │ │ - Meal Planner                                   │   │ │
│  │ │ - Workout Analyzer                               │   │ │
│  │ │ - Progress Tracker                               │   │ │
│  │ └──────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Resource Budget

**CT 101 (Ollama):**
- Current: ~14GB RAM (models loaded)
- Available: 34GB RAM for more models or concurrent requests
- CPU: 8 cores (plenty for inference)

**CT 100 (Docker Host):**
- Current: 103 MB (HealthRAG)
- Available: 15.9 GB for additional services
- CPU: 4 cores (sufficient for lightweight apps)

**Estimated Capacity:**
- 10-15 lightweight containers (100-500 MB each)
- All sharing Ollama backend
- Total: 2-8 GB app memory + 14GB Ollama = 16-22 GB

## Proposed Services

### 1. GitHub Actions Agents (Priority: HIGH)

**Purpose:** Automated code review, testing, documentation PRs
**Current Status:** Running on jwWinMin (will migrate)

**Architecture:**
```yaml
# docker-compose.yml on CT 100
services:
  github-agent:
    build: ./github-agent
    environment:
      - OLLAMA_BASE_URL=http://192.168.0.211:11434
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    volumes:
      - ./github-agent/data:/app/data
    restart: unless-stopped
```

**Resources:**
- Memory: ~200 MB
- Model: qwen2.5-coder:14b (best for code tasks)
- Tasks: Issue processing, code reviews, documentation PRs

**Migration Plan:**
1. Adapt jwWinMin GitHub runner to use shared Ollama
2. Deploy to CT 100 as container
3. Test with small tasks
4. Scale to full automation

**Timeline:** Week 1-2 (January 2026)

---

### 2. Meal Planner Service (Priority: MEDIUM)

**Purpose:** Weekly meal planning with macro optimization
**Integration:** HealthRAG nutrition tracking + meal templates

**Features:**
- Generate weekly meal plans based on user profile
- Optimize for macros (protein, carbs, fats)
- Generate shopping lists
- Integrate with USDA FDC and Open Food Facts APIs
- Export to Google Calendar

**Architecture:**
```yaml
services:
  meal-planner:
    build: ./meal-planner
    environment:
      - OLLAMA_BASE_URL=http://192.168.0.211:11434
      - USDA_FDC_API_KEY=${USDA_FDC_API_KEY}
    ports:
      - "8502:8502"  # Streamlit UI
    volumes:
      - ./meal-planner/data:/app/data
    depends_on:
      - healthrag  # Share user profiles
```

**Resources:**
- Memory: ~150 MB
- Model: llama3.1:8b (fast meal suggestions)
- Database: Shared with HealthRAG (user profiles, food logs)

**Timeline:** Week 3-4 (January 2026)

---

### 3. Workout Analyzer (Priority: MEDIUM)

**Purpose:** Analyze workout performance and suggest adjustments
**Integration:** HealthRAG workout tracking + autoregulation

**Features:**
- Analyze strength trends (progressive overload)
- Detect plateaus and suggest deloads
- Volume/intensity recommendations (RP principles)
- Exercise form analysis (future: video upload)
- Weekly check-ins with coaching advice

**Architecture:**
```yaml
services:
  workout-analyzer:
    build: ./workout-analyzer
    environment:
      - OLLAMA_BASE_URL=http://192.168.0.211:11434
    ports:
      - "8503:8503"  # Streamlit UI
    volumes:
      - ./workout-analyzer/data:/app/data
    depends_on:
      - healthrag  # Share workout logs
```

**Resources:**
- Memory: ~120 MB
- Model: qwen2.5-coder:14b (technical analysis)
- Database: Shared with HealthRAG (workouts.db)

**Timeline:** Week 5-6 (February 2026)

---

### 4. Progress Tracker & Dashboard (Priority: LOW)

**Purpose:** Unified dashboard for all health metrics
**Integration:** Aggregates data from HealthRAG, meal planner, workout analyzer

**Features:**
- Weight trend graphs (EWMA)
- Strength progression charts
- Body composition changes
- Nutrition adherence tracking
- Weekly/monthly progress reports
- Goal setting and milestones

**Architecture:**
```yaml
services:
  progress-dashboard:
    build: ./progress-dashboard
    environment:
      - OLLAMA_BASE_URL=http://192.168.0.211:11434
    ports:
      - "8504:8504"  # Plotly Dash UI
    volumes:
      - ./progress-dashboard/data:/app/data
    depends_on:
      - healthrag
      - meal-planner
      - workout-analyzer
```

**Resources:**
- Memory: ~180 MB (Plotly Dash)
- Model: llama3.1:8b (generate insights)
- Database: Read-only access to all service DBs

**Timeline:** Week 7-8 (February 2026)

---

### 5. Apple Health Sync Service (Priority: LOW)

**Purpose:** Automated sync with Apple Health XML exports
**Integration:** Updates HealthRAG with weight, workouts, nutrition

**Features:**
- Poll for new Apple Health exports (iCloud, Dropbox, etc.)
- Parse XML and update HealthRAG databases
- Bidirectional sync (export workouts to Apple Health)
- Conflict resolution (manual overrides)

**Architecture:**
```yaml
services:
  apple-health-sync:
    build: ./apple-health-sync
    environment:
      - OLLAMA_BASE_URL=http://192.168.0.211:11434  # For parsing/conflicts
      - ICLOUD_USER=${ICLOUD_USER}
      - ICLOUD_PASS=${ICLOUD_PASS}
    volumes:
      - ./apple-health-sync/data:/app/data
    depends_on:
      - healthrag
    restart: unless-stopped
```

**Resources:**
- Memory: ~100 MB
- Model: llama3.1:8b (parse conflicts)
- Frequency: Daily cron job

**Timeline:** Week 9-10 (March 2026)

---

## Service Interaction Patterns

### 1. Shared Database Access

**Problem:** Multiple services need access to user profiles, workout logs, food logs

**Solutions:**

**Option A: Shared Volume (Simplest)**
```yaml
volumes:
  healthrag-data:
    external: true

services:
  healthrag:
    volumes:
      - healthrag-data:/app/data

  meal-planner:
    volumes:
      - healthrag-data:/app/data:ro  # Read-only for safety
```

**Option B: REST API (Better, scalable)**
```yaml
services:
  healthrag:
    ports:
      - "8501:8501"  # Streamlit UI
      - "5000:5000"  # REST API for other services

  meal-planner:
    environment:
      - HEALTHRAG_API_URL=http://healthrag:5000
```

**Recommendation:** Start with Option A (shared volume), migrate to Option B when needed.

---

### 2. User Authentication

**Problem:** Multiple UIs need to share user sessions

**Solution:** Shared authentication service

```yaml
services:
  auth-service:
    image: authelia/authelia:latest
    ports:
      - "9091:9091"
    volumes:
      - ./authelia:/config
    environment:
      - AUTHELIA_JWT_SECRET=${JWT_SECRET}

  nginx-proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx:/etc/nginx/conf.d
    depends_on:
      - auth-service
      - healthrag
      - meal-planner
      - workout-analyzer
```

**Timeline:** When adding second service (Meal Planner)

---

### 3. Model Selection Strategy

**By Use Case:**

| Service | Model | Rationale |
|---------|-------|-----------|
| HealthRAG | llama3.1:8b | Fast general Q&A |
| GitHub Agents | qwen2.5-coder:14b | Best for code tasks |
| Meal Planner | llama3.1:8b | Fast meal suggestions |
| Workout Analyzer | qwen2.5-coder:14b | Technical analysis |
| Progress Tracker | llama3.1:8b | Generate insights |

**Concurrency:**
- Ollama queues requests automatically
- 48GB RAM can hold 2-3 models simultaneously
- If bottleneck: Add second Ollama instance (CT 102)

---

## Deployment Strategy

### Phase 1: HealthRAG (COMPLETE ✅)

- [x] Deploy HealthRAG to CT 100
- [x] Configure shared Ollama backend
- [x] Set up automated backups
- [x] Document architecture

### Phase 2: GitHub Agents (Week 1-2, January 2026)

- [ ] Migrate GitHub runner from jwWinMin
- [ ] Create Docker container
- [ ] Test with small tasks
- [ ] Full automation

### Phase 3: Meal Planner (Week 3-4, January 2026)

- [ ] Build meal planning service
- [ ] Integrate with HealthRAG data
- [ ] Deploy to CT 100
- [ ] Add authentication (Authelia)

### Phase 4: Workout Analyzer (Week 5-6, February 2026)

- [ ] Build workout analysis service
- [ ] Integrate with HealthRAG workout logs
- [ ] Deploy to CT 100

### Phase 5: Progress Dashboard (Week 7-8, February 2026)

- [ ] Build unified dashboard
- [ ] Aggregate data from all services
- [ ] Deploy to CT 100

### Phase 6: Apple Health Sync (Week 9-10, March 2026)

- [ ] Build sync service
- [ ] Test with Apple Health exports
- [ ] Deploy as background service

---

## Resource Monitoring

### Prometheus + Grafana (Recommended)

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"

  cadvisor:
    image: google/cadvisor:latest
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
```

**Dashboards:**
- Container resource usage (CPU, memory, network)
- Ollama API latency and request rate
- Database sizes and query performance
- User activity (queries, workouts logged, meals planned)

**Alerts:**
- Container down (restart failed)
- High memory usage (>90%)
- Ollama slow response (>10s)
- Disk space low (<10GB)

**Timeline:** Week 3-4 (with Meal Planner deployment)

---

## Cost Analysis

### Hardware (One-Time)

Already purchased, fully amortized:
- jwBeast (Ryzen 9, 128GB RAM): $2,000
- Already owned, no additional cost

### Operating Costs

**Electricity:**
- jwBeast idle: ~50W
- jwBeast full load: ~200W
- Average: ~100W × 24h × 365 days × $0.12/kWh = **$105/year**

**Internet:**
- Already have internet, no additional cost

**Total: ~$105/year**

### Cloud Alternative (Annual Costs)

**LLM API Costs:**
- GPT-4/Claude: $0.01-0.10/1K tokens
- 100K queries/year × 1K tokens avg = $1,000-10,000/year

**Hosting:**
- 5 containers × $20/month = $1,200/year
- Database storage: $120/year

**Total: $2,320-11,320/year**

**Homelab Savings: $2,215-11,215/year (21x-107x cheaper!)**

---

## Security Considerations

### 1. Network Isolation

**External Access:**
- Use reverse proxy (Nginx) with SSL
- Authelia for authentication
- Fail2ban for brute force protection

**Internal Network:**
- CT 100 and CT 101 on same subnet (192.168.0.x)
- No external exposure of Ollama port 11434

### 2. Data Privacy

**User Data:**
- All data stays local (no cloud sync)
- Encrypted backups (optional: GPG)
- Access logs for audit trail

**API Keys:**
- Stored in `.env` files (git-ignored)
- Rotated quarterly
- Never hardcoded in containers

### 3. Container Security

**Best Practices:**
- Run as non-root user
- Read-only filesystems where possible
- Resource limits (memory, CPU)
- Health checks for auto-restart

---

## Future Expansion

### Additional Services (6-12 months)

1. **Recipe Generator** - AI-powered recipe creation from ingredients
2. **Supplement Tracker** - Log and analyze supplement stack
3. **Sleep Analyzer** - Apple Health sleep data + recommendations
4. **Injury Prevention** - Detect overtraining, suggest recovery
5. **Social Features** - Share workouts with friends (local network only)

### Model Upgrades

As new models are released:
- Replace llama3.1:8b with llama3.2:8b (if better)
- Add specialized models (nutrition-specific, fitness-specific)
- Fine-tune models on personal data (privacy-first)

### Hardware Upgrades

If hitting resource limits:
- Add CT 102 (second Ollama instance for load balancing)
- Upgrade CT 101 RAM to 64GB
- Add GPU passthrough for faster inference (RTX 4090)

---

## Maintenance Schedule

**Daily:**
- Automated backups (2 AM)
- Health checks (cron every 5 minutes)

**Weekly:**
- Review container logs
- Check resource usage (Grafana)
- Verify backups (restore test)

**Monthly:**
- Update Docker images
- Update models (Ollama pull latest)
- Review security logs

**Quarterly:**
- Rotate API keys
- Review architecture (add/remove services)
- Performance optimization

---

## References

- **HealthRAG Deployment**: `docs/HOMELAB_DEPLOYMENT.md`
- **Homelab Infrastructure**: `/Users/jasonewillis/homelab/README.md`
- **Ollama API Docs**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Docker Compose Best Practices**: https://docs.docker.com/compose/best-practices/

---

**Next Action:** Deploy GitHub Agents (Week 1-2, January 2026)
