# HealthRAG Backend Testing Checklist

Complete guide for testing Phase 5a Week 1-2 backend implementation.

## Pre-Testing Setup

### 1. Environment Configuration (5 min)

```bash
# Create .env file
cd backend
cp .env.example .env
```

Edit `.env` with your credentials:
- [ ] **SUPABASE_URL** - Get from https://app.supabase.com → Project Settings → API
- [ ] **SUPABASE_KEY** - Anon key from API settings
- [ ] **SUPABASE_SERVICE_KEY** - Service role key from API settings
- [ ] **DATABASE_URL** - From Project Settings → Database → Connection String (URI mode)
- [ ] **JWT_SECRET_KEY** - Generate: `openssl rand -hex 32`

### 2. Install Dependencies (2 min)

```bash
pip3 install -r requirements.txt
```

Expected output: Successfully installed 19 packages.

### 3. Initialize Database (1 min)

```bash
python -c "from models.database import init_db; init_db()"
```

Expected output:
```
Creating database tables...
✅ Database tables created successfully!
```

### 4. Start Server (1 min)

```bash
python main.py
```

Expected output:
```
🚀 HealthRAG API starting up...
📍 Environment: development
🔗 Database: postgresql://...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Testing Methods

Choose your preferred testing approach:

### Option A: Postman Collection (RECOMMENDED) ⭐

**Why:** Automated tests, visual feedback, organized flow.

1. **Import files** (30 sec):
   - Open Postman
   - File → Import → `HealthRAG_API.postman_collection.json`
   - File → Import → `HealthRAG_Local.postman_environment.json`
   - Select "HealthRAG Local" environment (top-right dropdown)

2. **Run collection** (2 min):
   - Click "HealthRAG API" collection
   - Click "Run" button
   - Click "Run HealthRAG API"
   - Watch 14 requests execute with automated tests

3. **Expected results**:
   - ✅ All 14 requests should pass
   - ✅ ~30 automated tests should pass
   - ✅ `access_token` saved to environment automatically
   - ✅ TDEE and macros calculated correctly

### Option B: Swagger UI (ALTERNATIVE) 🌐

**Why:** Built-in, interactive, no setup needed.

1. **Open Swagger docs**:
   - Navigate to: http://localhost:8000/docs

2. **Test flow**:
   - Expand "Authentication" section
   - Click "POST /api/auth/signup" → Try it out
   - Fill in email/password → Execute
   - Copy `access_token` from response
   - Click 🔒 "Authorize" button (top-right)
   - Paste token → Authorize
   - Test profile endpoints (now authorized)

### Option C: curl Commands (MANUAL) 💻

**Why:** Scriptable, minimal dependencies, good for automation.

See `README.md` for detailed curl examples.

---

## Week 1-2 Acceptance Tests

### ✅ Test 1: Health Check

**Endpoint:** `GET /health`

**Postman:** Run "Health Check" request

**curl:**
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "HealthRAG API",
  "version": "0.1.0",
  "environment": "development"
}
```

**Status Code:** 200 OK

---

### ✅ Test 2: User Signup

**Endpoint:** `POST /api/auth/signup`

**Postman:** Run "Signup" request (auto-saves token)

**curl:**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@healthrag.com",
    "password": "SecurePass123!",
    "name": "Test User"
  }'
```

**Expected:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Status Code:** 201 Created

**Validations:**
- [ ] Token is a long JWT string
- [ ] Token type is "bearer"
- [ ] Expires in 900 seconds (15 minutes)

---

### ✅ Test 3: User Login

**Endpoint:** `POST /api/auth/login`

**Postman:** Run "Login" request

**curl:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@healthrag.com",
    "password": "SecurePass123!"
  }'
```

**Expected:** Same as signup (new token)

**Status Code:** 200 OK

---

### ✅ Test 4: Get Current User

**Endpoint:** `GET /api/auth/me`

**Postman:** Run "Get Current User" request

**curl:**
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "test@healthrag.com"
}
```

**Status Code:** 200 OK

**Validations:**
- [ ] user_id is a UUID
- [ ] email matches signup email

---

### ✅ Test 5: Create Profile (CRITICAL - TDEE Auto-Calculation)

**Endpoint:** `POST /api/profile`

**Postman:** Run "Create Profile" request

**curl:**
```bash
curl -X POST http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@healthrag.com",
    "name": "Test User",
    "age": 30,
    "sex": "male",
    "height_inches": 70,
    "current_weight_lbs": 180,
    "goal_type": "cut",
    "target_weight_lbs": 170,
    "training_experience": "intermediate",
    "equipment_access": "commercial_gym"
  }'
```

**Expected:**
```json
{
  "id": "user-uuid",
  "email": "test@healthrag.com",
  "name": "Test User",
  "age": 30,
  "sex": "male",
  "height_inches": 70,
  "current_weight_lbs": 180,
  "goal_type": "cut",
  "target_weight_lbs": 170,
  "training_experience": "intermediate",
  "equipment_access": "commercial_gym",
  "bmr": 1850.5,
  "tdee": 2220.6,
  "target_calories": 1720,
  "target_protein_g": 180,
  "target_carbs_g": 172,
  "target_fat_g": 57,
  "created_at": "2025-01-05T12:00:00Z",
  "updated_at": "2025-01-05T12:00:00Z"
}
```

**Status Code:** 201 Created

**CRITICAL VALIDATIONS:**
- [ ] **BMR calculated** (~1800-1900 for this profile)
- [ ] **TDEE > BMR** (activity multiplier applied)
- [ ] **Target calories = TDEE - 500** (cutting deficit)
- [ ] **Protein = ~1g/lb** (180g for 180 lbs)
- [ ] **Macros sum correctly**: `(180g × 4) + (172g × 4) + (57g × 9) ≈ 1720 cal`

**Manual Verification:**
```python
# Expected BMR (Mifflin-St Jeor for male, 30 years, 70 inches, 180 lbs):
BMR = (10 × 81.6 kg) + (6.25 × 177.8 cm) - (5 × 30) + 5 ≈ 1850 cal

# Expected TDEE (sedentary × 1.2):
TDEE = 1850 × 1.2 ≈ 2220 cal

# Expected target (cutting -500):
Target = 2220 - 500 = 1720 cal
```

---

### ✅ Test 6: Get Profile

**Endpoint:** `GET /api/profile`

**Postman:** Run "Get Profile" request

**curl:**
```bash
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected:** Same as create response

**Status Code:** 200 OK

---

### ✅ Test 7: Update Profile (Weight Change)

**Endpoint:** `PUT /api/profile`

**Postman:** Run "Update Profile - Weight Change" request

**curl:**
```bash
curl -X PUT http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "current_weight_lbs": 175
  }'
```

**Expected:**
```json
{
  "current_weight_lbs": 175,
  "bmr": 1820.0,
  "tdee": 2184.0,
  "target_calories": 1684,
  "target_protein_g": 175,
  ...
}
```

**Status Code:** 200 OK

**Validations:**
- [ ] Weight updated to 175 lbs
- [ ] **TDEE recalculated** (should be lower: ~2184 vs. 2220)
- [ ] **Target calories adjusted** (1684 vs. 1720)
- [ ] **Protein adjusted** (175g vs. 180g)

---

### ✅ Test 8: Update Profile (Goal Change)

**Endpoint:** `PUT /api/profile`

**Postman:** Run "Update Profile - Goal Change" request

**curl:**
```bash
curl -X PUT http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "goal_type": "bulk",
    "target_weight_lbs": 190
  }'
```

**Expected:**
```json
{
  "goal_type": "bulk",
  "target_weight_lbs": 190,
  "target_calories": 2484,
  ...
}
```

**Status Code:** 200 OK

**Validations:**
- [ ] Goal changed to "bulk"
- [ ] **Target calories = TDEE + 300** (2184 + 300 = 2484)

---

### ✅ Test 9: Error Handling - No Auth

**Endpoint:** `GET /api/profile` (no token)

**Postman:** Run "Get Profile - No Auth" request

**curl:**
```bash
curl http://localhost:8000/api/profile
```

**Expected:**
```json
{
  "detail": "Not authenticated"
}
```

**Status Code:** 403 Forbidden

---

### ✅ Test 10: Error Handling - Duplicate Profile

**Endpoint:** `POST /api/profile` (second time)

**Postman:** Run "Create Profile - Duplicate" request

**Expected:**
```json
{
  "detail": "Profile already exists. Use PUT to update."
}
```

**Status Code:** 400 Bad Request

---

### ✅ Test 11: Error Handling - Invalid Login

**Endpoint:** `POST /api/auth/login`

**Postman:** Run "Login - Invalid Credentials" request

**Expected:**
```json
{
  "detail": "Invalid email or password"
}
```

**Status Code:** 401 Unauthorized

---

## Success Criteria ✅

All tests must pass for Week 1-2 completion:

- [ ] **Health check** returns 200 OK
- [ ] **Signup** creates user and returns JWT token
- [ ] **Login** authenticates and returns JWT token
- [ ] **Get current user** returns user_id and email
- [ ] **Create profile** returns profile with **auto-calculated TDEE and macros**
- [ ] **Get profile** retrieves created profile
- [ ] **Update profile (weight)** recalculates TDEE and macros
- [ ] **Update profile (goal)** recalculates target calories
- [ ] **Error handling** correctly returns 400/401/403 for invalid requests
- [ ] **All Postman tests pass** (30+ automated validations)

---

## Troubleshooting

### Issue: "Connection refused" on startup

**Fix:**
- Check port 8000 is not already in use: `lsof -i :8000`
- Kill conflicting process: `kill -9 <PID>`
- Or change port in `.env`: `API_PORT=8001`

### Issue: "Could not validate credentials" (401)

**Fix:**
- Token may have expired (15 min default)
- Run signup/login again to get fresh token
- Copy new token to Postman environment or curl command

### Issue: "Profile already exists" (400)

**Fix:**
- Delete existing profile first: `DELETE /api/profile`
- Or use `PUT /api/profile` to update instead of create

### Issue: TDEE calculations seem wrong

**Verify:**
- Check input data (age, sex, height, weight) is correct
- Use Postman test assertions to validate calculations
- Compare with manual calculation using Mifflin-St Jeor formula

### Issue: Database connection error

**Fix:**
- Verify `DATABASE_URL` in `.env` is correct
- Check Supabase project is active
- Test connection: `psql $DATABASE_URL`

---

## Next Steps

Once all tests pass:

1. **✅ Mark Week 1-2 as complete**
2. **📸 Take screenshot of passing Postman tests** (optional)
3. **🚀 Continue to Week 3-4**: Core data endpoints (workouts, nutrition, weight)

**Week 3-4 Focus:**
- Workout logging endpoints (sets, reps, weight, RIR)
- Food logging endpoints (search, barcode, daily totals)
- Weight tracking endpoints (EWMA trend calculation)

See Phase 5a plan for detailed Week 3-4 roadmap.
