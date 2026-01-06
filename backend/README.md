# HealthRAG Backend API

FastAPI backend for HealthRAG mobile app and web frontend.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your Supabase credentials:
# - SUPABASE_URL (from Supabase project settings)
# - SUPABASE_KEY (anon key from Supabase project settings)
# - SUPABASE_SERVICE_KEY (service role key from Supabase project settings)
# - DATABASE_URL (PostgreSQL connection string from Supabase)
# - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
```

### 3. Initialize Database

```bash
# Run database migrations (creates tables)
python -c "from models.database import init_db; init_db()"
```

### 4. Start the Server

```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "HealthRAG API",
  "version": "0.1.0",
  "environment": "development"
}
```

### Authentication

#### Sign Up
```bash
curl -X POST http://localhost:8000/api/auth/signup \
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

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

#### Get Current User
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Profile Management

#### Create Profile
```bash
curl -X POST http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
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

Expected response (with auto-calculated TDEE and macros):
```json
{
  "id": "user-uuid",
  "email": "test@example.com",
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

#### Get Profile
```bash
curl -X GET http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update Profile
```bash
curl -X PUT http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_weight_lbs": 175,
    "goal_type": "maintain"
  }'
```

#### Delete Profile
```bash
curl -X DELETE http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Testing with Postman

### Quick Setup (Recommended)

1. **Import the collection**:
   - Open Postman
   - File → Import
   - Select `HealthRAG_API.postman_collection.json`

2. **Import the environment**:
   - File → Import
   - Select `HealthRAG_Local.postman_environment.json`
   - Select "HealthRAG Local" environment in top-right dropdown

3. **Run the tests**:
   - Collection is organized in recommended test order
   - Click "Run collection" to execute all tests
   - Or run individual requests manually

### Test Flow

The collection includes **32 requests** organized in 9 folders:

1. **Health & Status** (2 requests)
   - Health Check
   - Root Endpoint

2. **Authentication** (4 requests)
   - Signup → automatically saves `access_token`
   - Login → automatically saves `access_token`
   - Get Current User → automatically saves `user_id`
   - Logout

3. **Profile Management** (4 requests)
   - Create Profile → auto-calculates TDEE and macros
   - Get Profile
   - Update Profile
   - Delete Profile

4. **Workouts** (4 requests)
   - Create Workout Session → saves `workout_id`
   - Get Workout Sessions (by date range or recent)
   - Get Workout Session by ID
   - Delete Workout Session

5. **Nutrition** (5 requests)
   - Log Food Entry
   - Get Food Entries by Date
   - Get Daily Nutrition Totals (macro summary)
   - Search Foods (starter foods included)
   - Copy Yesterday's Meals

6. **Weight Tracking** (3 requests)
   - Log Weight Entry → auto-calculates EWMA trend
   - Get Weight Entries
   - Get Weight Trend (weekly/monthly changes)

7. **Sync Protocol** (2 requests) ⭐ NEW
   - Pull Changes (GET /api/sync/changes)
   - Push Changes (POST /api/sync/changes)

8. **External Food APIs** (3 requests) ⭐ NEW
   - Search USDA FDC (400K foods)
   - Lookup Barcode (Open Food Facts)
   - Search Open Food Facts (2.8M products)

9. **Error Handling** (3 requests)
   - Get Profile without auth (403 test)
   - Create duplicate profile (400 test)
   - Login with invalid credentials (401 test)

### Automated Tests

Each request includes automated tests that validate:
- ✅ Correct status codes
- ✅ Response structure and data types
- ✅ Auto-calculated TDEE and macros
- ✅ Token auto-save to environment
- ✅ Error handling

Run the collection and see test results in the "Test Results" tab.

### Manual Testing (Alternative)

If you prefer curl or want to use the OpenAPI spec:
1. Import OpenAPI spec from http://localhost:8000/docs
2. Use Swagger UI for interactive testing

## Development

### Project Structure

```
backend/
├── main.py                  # FastAPI app entry point
├── config.py                # Pydantic settings
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── api/
│   ├── auth.py             # Authentication endpoints
│   └── profile.py          # Profile CRUD endpoints
├── models/
│   ├── database.py         # SQLAlchemy models
│   └── schemas.py          # Pydantic request/response schemas
└── services/               # Business logic (to be created)
```

### Phase 5a Timeline

- ✅ **Week 1-2**: Setup & Auth (COMPLETE)
  - FastAPI project structure
  - Supabase Auth integration
  - Profile CRUD endpoints
  - TDEE/macro calculations

- ✅ **Week 3-4**: Core Data Endpoints (COMPLETE)
  - Workout logging endpoints
  - Food logging endpoints
  - Weight tracking endpoints

- ✅ **Week 5-6**: Sync Protocol & Food APIs (COMPLETE)
  - Sync protocol (pull/push with Last Write Wins)
  - USDA FDC integration (400K foods)
  - Open Food Facts integration (2.8M products)
  - Barcode lookup for mobile scanning
  - Docker Compose for homelab deployment

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` in `.env` is correct
- Check Supabase project is active
- Test connection: `psql $DATABASE_URL`

### Authentication Errors
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check JWT_SECRET_KEY is set
- Ensure tokens haven't expired (15 min default)

### CORS Errors
- Add your frontend URL to `CORS_ORIGINS` in `.env`
- Restart the server after env changes

## Next Steps

**Phase 5a Backend: COMPLETE** ✅

All backend endpoints are functional and ready for deployment:
- ✅ 32 API endpoints (health, auth, profile, workouts, nutrition, weight, sync, external food APIs)
- ✅ JWT authentication with Supabase
- ✅ EWMA weight trend calculation
- ✅ Sync protocol (pull/push with Last Write Wins)
- ✅ External food APIs (USDA FDC + Open Food Facts)
- ✅ Deployment-ready with Docker Compose for homelab

**Next Phase: 5b - Mobile App Development**
1. **React Native setup** - Initialize Expo project
2. **WatermelonDB** - Offline-first SQLite database
3. **Mobile UI** - Workout/Food/Weight logging screens
4. **Sync integration** - Connect to backend API
5. **Testing** - iOS + Android testing with Expo Go

**Ready to Deploy:**
- See `HOMELAB_DEPLOYMENT.md` for complete homelab deployment guide
- One-command deployment: `./deploy-to-homelab.sh`
- Includes local + remote access setup (Cloudflare Tunnel, Tailscale, or reverse proxy)
