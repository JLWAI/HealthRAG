"""
Authentication API using Supabase Auth.

Handles user signup, login, token refresh, and JWT validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

from models.schemas import LoginRequest, SignupRequest, Token, TokenData
from config import settings

router = APIRouter()
security = HTTPBearer()

# Initialize Supabase client (optional - will be None if not configured)
supabase: Client = None
try:
    # Only initialize if credentials are provided and not placeholders
    if (settings.supabase_url and settings.supabase_key and
        not settings.supabase_url.startswith("https://placeholder") and
        settings.supabase_key != "placeholder-anon-key"):
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
except Exception as e:
    # Supabase initialization failed - auth endpoints will return 503
    print(f"Warning: Supabase initialization failed: {e}")
    supabase = None


def check_auth_enabled():
    """
    Check if Supabase authentication is configured.

    Raises:
        HTTPException: If Supabase is not configured
    """
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is currently disabled. Please configure Supabase credentials to enable auth endpoints."
        )


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in token
        expires_delta: Token expiration time (default: 15 minutes)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        TokenData with user_id and email

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

        return TokenData(user_id=user_id, email=email)

    except JWTError:
        raise credentials_exception


# Dev mode user for local testing (when Supabase is not configured)
DEV_USER = TokenData(
    user_id="dev-user-local-testing",
    email="dev@healthrag.local"
)

# Check if we're in dev mode (Supabase not configured)
DEV_MODE = supabase is None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Dependency to get current authenticated user from JWT token.

    In DEV_MODE (Supabase not configured), returns a test user for local development.

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        TokenData with user_id and email

    Raises:
        HTTPException: If token is invalid (production mode only)

    Usage:
        @router.get("/protected")
        def protected_route(current_user: TokenData = Depends(get_current_user)):
            return {"user_id": current_user.user_id}
    """
    if DEV_MODE:
        # In dev mode, return test user without requiring valid token
        return DEV_USER
    return decode_access_token(credentials.credentials)


@router.post("/signup", response_model=Token, tags=["Authentication"])
async def signup(request: SignupRequest):
    """
    Register a new user with Supabase Auth.

    Args:
        request: Signup request with email, password, name

    Returns:
        JWT access token

    Raises:
        HTTPException: If signup fails (email already exists, weak password, etc.)
    """
    check_auth_enabled()
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })

        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed. Email may already exist."
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": auth_response.user.id, "email": auth_response.user.email}
        )

        return Token(
            access_token=access_token,
            expires_in=settings.access_token_expire_minutes * 60
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )


@router.post("/login", response_model=Token, tags=["Authentication"])
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.

    Args:
        request: Login request with email and password

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    check_auth_enabled()
    try:
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": auth_response.user.id, "email": auth_response.user.email}
        )

        return Token(
            access_token=access_token,
            expires_in=settings.access_token_expire_minutes * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout", tags=["Authentication"])
async def logout(current_user: TokenData = Depends(get_current_user)):
    """
    Logout user (sign out from Supabase).

    Note: JWT tokens are stateless, so we can't truly invalidate them
    until expiration. The mobile app should discard the token.
    """
    check_auth_enabled()
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/me", response_model=TokenData, tags=["Authentication"])
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """
    Get current authenticated user information from token.

    Returns:
        TokenData with user_id and email
    """
    return current_user
