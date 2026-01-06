# HealthRAG Backend - Homelab Quick Reference

Quick commands for common homelab operations.

---

## 🚀 Deployment

### One-Command Deploy (From Dev Machine)
```bash
./deploy-to-homelab.sh
```

### Manual Deploy (SSH to Homelab)
```bash
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend
git pull origin main
docker-compose up -d --build
```

---

## 📊 Status & Monitoring

### Check Container Status
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose ps'
```

### View Live Logs
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose logs -f healthrag-api'
```

### Test Health Endpoint
```bash
# Local network
curl http://192.168.0.64:8000/health

# Remote (Cloudflare)
curl https://healthrag.yourdomain.com/health

# Remote (Tailscale)
curl http://jwwinmin:8000/health
```

---

## 🔄 Service Management

### Restart API
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose restart healthrag-api'
```

### Restart Database
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose restart healthrag-db'
```

### Restart All Services
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose restart'
```

### Stop All Services
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose down'
```

### Start All Services
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose up -d'
```

---

## 🗄️ Database Operations

### Connect to Database
```bash
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend
docker exec -it healthrag-db psql -U healthrag -d healthrag
```

### Backup Database
```bash
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend
docker exec healthrag-db pg_dump -U healthrag healthrag > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend
cat backup.sql | docker exec -i healthrag-db psql -U healthrag -d healthrag
```

### Quick Database Check
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker exec healthrag-db psql -U healthrag -d healthrag -c "SELECT COUNT(*) FROM workout_sessions;"'
```

---

## 🔧 Troubleshooting

### View Last 50 Log Lines
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose logs --tail=50 healthrag-api'
```

### Check for Errors
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose logs healthrag-api | grep -i error'
```

### Rebuild from Scratch
```bash
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend
docker-compose down -v  # ⚠️  Deletes database!
git pull origin main
docker-compose up -d --build
```

### Check Disk Space
```bash
ssh jwadmin@192.168.0.64 'df -h'
```

### Clean Up Docker
```bash
ssh jwadmin@192.168.0.64 'docker system prune -a --volumes'
```

---

## 📱 API Testing

### Test Signup
```bash
curl -X POST http://192.168.0.64:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

### Test Login
```bash
curl -X POST http://192.168.0.64:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test Protected Endpoint
```bash
TOKEN="your-access-token"
curl -H "Authorization: Bearer $TOKEN" http://192.168.0.64:8000/api/profile
```

---

## 🌐 Remote Access

### Cloudflare Tunnel

**Check Tunnel Status**:
```bash
ssh jwadmin@192.168.0.64
./cloudflared-windows-amd64.exe tunnel info healthrag
```

**Restart Tunnel**:
```bash
ssh jwadmin@192.168.0.64
net stop cloudflared
net start cloudflared
```

### Tailscale

**Check Status**:
```bash
ssh jwadmin@192.168.0.64
tailscale status
```

**Restart Tailscale**:
```bash
ssh jwadmin@192.168.0.64
tailscale down
tailscale up
```

---

## 🔐 Security

### Rotate JWT Secret
```bash
# Generate new secret
openssl rand -hex 32

# Update .env on homelab
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend
nano .env  # Update JWT_SECRET_KEY

# Restart API
docker-compose restart healthrag-api
```

### Update Environment Variables
```bash
ssh jwadmin@192.168.0.64
cd ~/HealthRAG/backend
nano .env  # Make changes
docker-compose restart healthrag-api
```

---

## 📈 Performance

### Check Container Resource Usage
```bash
ssh jwadmin@192.168.0.64 'docker stats --no-stream healthrag-api healthrag-db'
```

### Check Database Size
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker exec healthrag-db psql -U healthrag -d healthrag -c "SELECT pg_size_pretty(pg_database_size('"'"'healthrag'"'"'));"'
```

---

## 📋 Quick Access URLs

### Local Network
- **API**: http://192.168.0.64:8000
- **Swagger Docs**: http://192.168.0.64:8000/docs
- **ReDoc**: http://192.168.0.64:8000/redoc

### Remote (Cloudflare)
- **API**: https://healthrag.yourdomain.com
- **Swagger Docs**: https://healthrag.yourdomain.com/docs

### Remote (Tailscale)
- **API**: http://jwwinmin:8000
- **Swagger Docs**: http://jwwinmin:8000/docs

---

## 🚨 Emergency Commands

### Force Stop Everything
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker-compose down --remove-orphans'
```

### Emergency Database Backup
```bash
ssh jwadmin@192.168.0.64 'cd ~/HealthRAG/backend && docker exec healthrag-db pg_dumpall -U healthrag > emergency_backup_$(date +%Y%m%d_%H%M%S).sql'
```

### Check if Port 8000 is in Use
```bash
ssh jwadmin@192.168.0.64 'netstat -ano | findstr :8000'
```

### Kill Process on Port 8000 (Windows)
```bash
# Get PID from netstat command above, then:
ssh jwadmin@192.168.0.64 'taskkill /PID <PID> /F'
```

---

## 📚 Full Documentation

For complete guides, see:
- **Homelab Deployment**: `HOMELAB_DEPLOYMENT.md` (500+ lines)
- **Conversion Summary**: `HOMELAB_CONVERSION.md`
- **Backend README**: `README.md`
- **API Docs**: http://192.168.0.64:8000/docs
