# HealthRAG Backend - Deployment Guide

Complete guide for deploying HealthRAG Backend API to production using Render.com.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Deploy (Render.com)](#quick-deploy-rendercom)
- [Manual Setup](#manual-setup)
- [Environment Variables](#environment-variables)
- [Database Migration](#database-migration)
- [Testing Deployment](#testing-deployment)
- [Troubleshooting](#troubleshooting)
- [Cost Estimates](#cost-estimates)

---

## Prerequisites

1. **GitHub Account** - Code must be in a GitHub repository
2. **Render.com Account** - Free tier available (https://render.com/register)
3. **Supabase Account** - For auth + PostgreSQL (https://supabase.com/dashboard)
4. **USDA FDC API Key** (Optional) - For food search (https://fdc.nal.usda.gov/api-key-signup)

---

## Quick Deploy (Render.com)

### Option 1: Blueprint Deploy (Recommended)

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "Add backend deployment files"
   git push origin main
   ```

2. **Deploy with Blueprint**:
   - Go to: https://dashboard.render.com/select-repo
   - Select your HealthRAG repository
   - Choose branch: `main`
   - Render will auto-detect `render.yaml` and provision:
     - Web Service (FastAPI backend)
     - PostgreSQL database
     - Environment variables

3. **Set environment secrets** (in Render dashboard):
   - `SUPABASE_URL` - From Supabase project settings → API → URL
   - `SUPABASE_KEY` - From Supabase project settings → API → anon key
   - `SUPABASE_SERVICE_KEY` - From Supabase project settings → API → service_role key
   - `USDA_FDC_API_KEY` (optional) - From https://fdc.nal.usda.gov/api-key-signup

4. **Wait for deployment** (~5-10 minutes)
   - Render will build Docker image
   - Run health checks
   - Deploy to production

5. **Verify deployment**:
   ```bash
   curl https://healthrag-api.onrender.com/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "HealthRAG API",
     "version": "0.1.0",
     "environment": "production"
   }
   ```

### Option 2: Manual Web Service Creation

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Create New → Web Service**:
   - Connect GitHub repository
   - Choose branch: `main`

3. **Configure Service**:
   - **Name**: `healthrag-api`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`
   - **Plan**: Free (or Starter $7/mo for production)
   - **Region**: Oregon (or closest to users)

4. **Add Environment Variables** (see Environment Variables section below)

5. **Create Web Service** → Wait for deployment

---

## Manual Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-username/HealthRAG.git
cd HealthRAG/backend
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Database
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# JWT
JWT_SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# CORS
CORS_ORIGINS=http://localhost:3000,https://healthrag.app

# Optional: USDA FDC API
USDA_FDC_API_KEY=your-usda-key-here
```

### 4. Initialize Database

```bash
python -c "from models.database import init_db; init_db()"
```

This creates tables:
- `user_profiles` - User data and TDEE/macro calculations
- `workout_sessions` - Workout metadata
- `workout_sets` - Individual sets (exercise, weight, reps, RIR)
- `food_entries` - Food logs with macros
- `weight_entries` - Daily weight with EWMA trend
- `body_measurements` - 11 body measurements

### 5. Run Locally

```bash
python main.py
```

Access:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Environment Variables

### Required (Production)

| Variable | Description | Example | Source |
|----------|-------------|---------|--------|
| `SUPABASE_URL` | Supabase project URL | `https://abc123.supabase.co` | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Supabase anon key | `eyJhbGc...` | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | `eyJhbGc...` | Supabase Dashboard → Settings → API |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` | Supabase Dashboard → Settings → Database |
| `JWT_SECRET_KEY` | Secret for JWT signing | `a1b2c3d4...` | Generate: `openssl rand -hex 32` |

### Optional

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `ENVIRONMENT` | Environment name | `development` | Set to `production` in Render |
| `API_HOST` | Host to bind | `0.0.0.0` | Use `0.0.0.0` in Docker |
| `API_PORT` | Port to bind | `8000` | Render assigns port automatically |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | DO NOT CHANGE |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `15` | Security best practice: ≤15 min |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` | Comma-separated list |
| `USDA_FDC_API_KEY` | USDA FoodData Central key | None | Get free key: https://fdc.nal.usda.gov/api-key-signup |

---

## Database Migration

Render provides free PostgreSQL (with limitations), but Supabase is recommended for production:

### Supabase Setup (Recommended)

1. **Create Supabase Project**: https://supabase.com/dashboard
2. **Get Connection String**:
   - Dashboard → Settings → Database → Connection string (Direct connection)
   - Format: `postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres`
3. **Copy to `DATABASE_URL` in Render**

### Render PostgreSQL (Alternative)

1. **Create Database** (via Blueprint or manual):
   - Dashboard → New → PostgreSQL
   - Plan: Free (7-day data retention, 1GB storage)
2. **Render auto-populates** `DATABASE_URL` environment variable
3. **Warning**: Free tier has limitations:
   - 7-day data retention (old data deleted)
   - 1GB storage limit
   - No read replicas

---

## Testing Deployment

### 1. Health Check

```bash
curl https://healthrag-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "HealthRAG API",
  "version": "0.1.0",
  "environment": "production"
}
```

### 2. Signup Test

```bash
curl -X POST https://healthrag-api.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "name": "Test User"
  }'
```

Expected response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 3. API Docs

Visit: https://healthrag-api.onrender.com/docs

You should see interactive Swagger UI with all 32 endpoints:
- **Health** (2)
- **Authentication** (4)
- **Profile** (4)
- **Workouts** (4)
- **Nutrition** (8 endpoints, including USDA + OFF)
- **Weight** (3)
- **Sync** (2)
- **Error Handling** (3)

---

## Troubleshooting

### Build Fails

**Error**: `ModuleNotFoundError: No module named 'xyz'`

**Fix**: Ensure dependency is in `requirements.txt`:
```bash
pip freeze | grep xyz >> requirements.txt
git add requirements.txt && git commit -m "Add missing dependency"
git push origin main
```

Render will auto-redeploy.

---

### Health Check Fails

**Error**: `Service unhealthy`

**Fix**: Check Render logs:
- Dashboard → Your Service → Logs
- Look for Python errors, database connection failures

Common causes:
- Missing environment variables (check `DATABASE_URL`, `SUPABASE_*`)
- Database connection timeout (check Supabase IP whitelist)
- Port mismatch (Render assigns port via `$PORT` env var)

---

### Database Connection Error

**Error**: `OperationalError: could not connect to server`

**Fix**:
1. Verify `DATABASE_URL` is correct
2. Check Supabase IP whitelist:
   - Dashboard → Settings → Database → Connection Pooling
   - Add Render IP range (or allow all IPs)
3. Test connection:
   ```bash
   psql $DATABASE_URL
   ```

---

### CORS Errors (Frontend)

**Error**: `Access-Control-Allow-Origin header is missing`

**Fix**: Add frontend URL to `CORS_ORIGINS`:
```bash
CORS_ORIGINS=https://healthrag.app,http://localhost:3000
```

Update in Render dashboard → Environment → Edit.

---

### 502 Bad Gateway

**Error**: Render returns 502 after deployment

**Possible Causes**:
1. **App crashed on startup** - Check logs for Python errors
2. **Port mismatch** - Ensure app binds to `0.0.0.0:8000`
3. **Health check timeout** - Increase startup time in `Dockerfile`

**Fix**:
```dockerfile
# In Dockerfile, increase health check start period:
HEALTHCHECK --start-period=30s ...
```

---

### USDA FDC API Unavailable

**Error**: `USDA FDC API unavailable: API key required`

**Fix**:
1. Get free API key: https://fdc.nal.usda.gov/api-key-signup
2. Add to Render environment:
   - Dashboard → Environment → Add → `USDA_FDC_API_KEY`

**Note**: USDA FDC is optional. Open Food Facts works without API key.

---

## Cost Estimates

### Free Tier (Development)

| Service | Plan | Cost | Limitations |
|---------|------|------|-------------|
| Render Web Service | Free | $0/mo | Spins down after inactivity, 750 hrs/mo |
| Render PostgreSQL | Free | $0/mo | 7-day data retention, 1GB storage |
| Supabase | Free | $0/mo | 500MB database, 2GB bandwidth, 50K MAU |
| USDA FDC API | Free | $0/mo | 1000 requests/hour |
| Open Food Facts | Free | $0/mo | 100 requests/min |

**Total**: $0/month (with limitations)

---

### Production Tier (Recommended)

| Service | Plan | Cost | Benefits |
|---------|------|------|----------|
| Render Web Service | Starter | $7/mo | Always-on, 0.5GB RAM |
| Supabase | Pro | $25/mo | 8GB database, 250GB bandwidth, unlimited MAU |
| USDA FDC API | Free | $0/mo | 1000 requests/hour (sufficient) |
| Open Food Facts | Free | $0/mo | 100 requests/min (sufficient) |

**Total**: $32/month (production-ready)

**Alternative** (Render-only):
- Render Starter: $7/mo
- Render PostgreSQL Standard: $7/mo
- **Total**: $14/mo (but Supabase Auth integration is easier)

---

## Next Steps

After successful deployment:

1. **Update Frontend**:
   - Point mobile app to: `https://healthrag-api.onrender.com`
   - Update CORS origins with production domain

2. **Monitor Usage**:
   - Render Dashboard → Metrics (CPU, memory, requests)
   - Supabase Dashboard → Reports (database size, API requests)

3. **Set Up CI/CD** (Optional):
   - Render auto-deploys on `git push` to `main`
   - Add pre-push tests: `git push` → pytest → deploy

4. **Custom Domain** (Optional):
   - Render Dashboard → Settings → Custom Domains
   - Add CNAME: `api.healthrag.com` → `healthrag-api.onrender.com`
   - Free SSL certificate included

5. **Backup Strategy**:
   - Supabase: Automatic daily backups (7-day retention on free tier)
   - Render PostgreSQL: No backups on free tier (use Supabase instead)

---

## Support

- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **GitHub Issues**: https://github.com/your-username/HealthRAG/issues

---

**Deployment Complete!** 🎉

Your HealthRAG Backend API is now live and ready to serve mobile clients.
