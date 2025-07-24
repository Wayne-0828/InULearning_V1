from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.auth import create_access_token, create_refresh_token, verify_token
from app.crud import (
    create_user, authenticate_user, create_refresh_token as crud_create_refresh_token,
    get_refresh_token, revoke_refresh_token, revoke_all_user_tokens
)
from app.schemas import UserCreate, UserLogin, Token, RefreshTokenRequest, Message
from app.models import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=Message, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        create_user(db, user)
        return {"message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value}
    )
    
    # Store refresh token in database
    refresh_expires = datetime.utcnow() + timedelta(days=7)
    crud_create_refresh_token(db, user.id, refresh_token, refresh_expires)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes in seconds
    }


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    # Verify refresh token
    token_data = verify_token(refresh_request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if refresh token exists and is not revoked
    db_refresh_token = get_refresh_token(db, refresh_request.refresh_token)
    if not db_refresh_token or db_refresh_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token"
        )
    
    # Check if refresh token is expired
    if datetime.utcnow() > db_refresh_token.expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(token_data.user_id), "email": token_data.email, "role": token_data.role},
        expires_delta=access_token_expires
    )
    
    # Create new refresh token
    new_refresh_token = create_refresh_token(
        data={"sub": str(token_data.user_id), "email": token_data.email, "role": token_data.role}
    )
    
    # Revoke old refresh token
    revoke_refresh_token(db, refresh_request.refresh_token)
    
    # Store new refresh token
    refresh_expires = datetime.utcnow() + timedelta(days=7)
    crud_create_refresh_token(db, token_data.user_id, new_refresh_token, refresh_expires)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 1800
    }


@router.post("/logout", response_model=Message)
def logout(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Logout user by revoking refresh token"""
    success = revoke_refresh_token(db, refresh_request.refresh_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all", response_model=Message)
def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user from all devices by revoking all refresh tokens"""
    revoke_all_user_tokens(db, current_user.id)
    return {"message": "Successfully logged out from all devices"} 