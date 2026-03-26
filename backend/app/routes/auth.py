"""
Authentication API routes.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.auth import (
    UserCreate, UserResponse, Token,
    authenticate_user, create_access_token,
    get_current_user, get_user_permissions
)
from app.db.database import get_db, User, UserRole

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """Authenticate user with username/email and password."""
    from app.core.auth import verify_password

    # Try to find user by username first, then by email
    user = db.query(User).filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user."""
    from app.core.auth import verify_token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    return user


@router.post("/register")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Regular users are clients. Admin role can only be set by manual update.
    """
    from app.core.auth import get_password_hash, create_access_token

    # Normalize username (allow omitting username in request)
    username = user_data.username or user_data.email.split("@")[0]

    # Check if user already exists
    if db.query(User).filter(
        (User.email == user_data.email) | (User.username == username)
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user (always client role for registration)
    db_user = User(
        email=user_data.email,
        username=username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=UserRole.CLIENT  # Always client for registration
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token for new user
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "user": db_user}


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.get("/permissions")
async def get_user_permissions_endpoint(current_user: User = Depends(get_current_user)):
    """Get current user's permissions."""
    permissions = get_user_permissions(current_user.role)
    return {"permissions": permissions, "role": current_user.role.value}