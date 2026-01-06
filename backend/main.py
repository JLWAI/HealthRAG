"""
HealthRAG Backend API - FastAPI Entry Point

Full API with all endpoints:
- Health check
- Authentication (Supabase or DEV_MODE bypass)
- User profile management
- Workout tracking
- Weight tracking
- Nutrition tracking (food search via USDA FDC + Open Food Facts)
- Data sync

Note: When Supabase is not configured, API runs in DEV_MODE with a test user.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Track loaded endpoints
loaded_endpoints = []
failed_endpoints = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI app.
    Handles startup and shutdown events.
    """
    # Startup
    dev_mode = os.getenv("SUPABASE_URL", "").startswith("https://placeholder") or not os.getenv("SUPABASE_URL")
    mode = "DEV_MODE (auth bypassed)" if dev_mode else "PRODUCTION"

    print(f"🚀 HealthRAG API starting up ({mode})...")
    print(f"📍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    db_url = os.getenv('DATABASE_URL', 'Not configured')
    print(f"🔗 Database: {db_url[:50]}..." if len(db_url) > 50 else f"🔗 Database: {db_url}")
    print(f"✅ Loaded: {', '.join(loaded_endpoints) if loaded_endpoints else 'None'}")
    if failed_endpoints:
        print(f"❌ Failed: {', '.join(failed_endpoints)}")

    yield

    # Shutdown
    print("⏹️  HealthRAG API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="HealthRAG API",
    description="Backend API for HealthRAG - Health & Fitness Tracking",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://100.113.0.73:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: API status and version
    """
    dev_mode = os.getenv("SUPABASE_URL", "").startswith("https://placeholder") or not os.getenv("SUPABASE_URL")
    return {
        "status": "healthy",
        "service": "HealthRAG API",
        "version": "0.2.0",
        "mode": "dev" if dev_mode else "production",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "loaded_endpoints": loaded_endpoints,
        "failed_endpoints": failed_endpoints
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - redirects to API documentation.

    Returns:
        dict: Welcome message with links
    """
    dev_mode = os.getenv("SUPABASE_URL", "").startswith("https://placeholder") or not os.getenv("SUPABASE_URL")
    return {
        "message": "Welcome to HealthRAG API",
        "mode": "dev (auth bypassed - use any Bearer token)" if dev_mode else "production",
        "docs": "/docs",
        "health": "/health"
    }


# Import and include all routers
# Auth endpoints
try:
    from api import auth
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    loaded_endpoints.append("auth")
except Exception as e:
    failed_endpoints.append(f"auth: {e}")

# Profile endpoints
try:
    from api import profile
    app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
    loaded_endpoints.append("profile")
except Exception as e:
    failed_endpoints.append(f"profile: {e}")

# Workout endpoints
try:
    from api import workouts
    app.include_router(workouts.router, prefix="/api/workouts", tags=["Workouts"])
    loaded_endpoints.append("workouts")
except Exception as e:
    failed_endpoints.append(f"workouts: {e}")

# Weight endpoints
try:
    from api import weight
    app.include_router(weight.router, prefix="/api/weight", tags=["Weight"])
    loaded_endpoints.append("weight")
except Exception as e:
    failed_endpoints.append(f"weight: {e}")

# Nutrition endpoints
try:
    from api import nutrition
    app.include_router(nutrition.router, prefix="/api/nutrition", tags=["Nutrition"])
    loaded_endpoints.append("nutrition")
except Exception as e:
    failed_endpoints.append(f"nutrition: {e}")

# Sync endpoints
try:
    from api import sync
    app.include_router(sync.router, prefix="/api/sync", tags=["Sync"])
    loaded_endpoints.append("sync")
except Exception as e:
    failed_endpoints.append(f"sync: {e}")


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True  # Auto-reload on code changes (development only)
    )
