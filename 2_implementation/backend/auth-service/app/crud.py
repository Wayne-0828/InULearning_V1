from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.models import User, RefreshToken
from app.schemas import UserCreate, UserUpdate
from app.auth import get_password_hash, verify_password
from datetime import datetime


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("User with this email or username already exists")


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user profile"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_refresh_token(db: Session, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
    """Create refresh token record"""
    db_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """Get refresh token by token string"""
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()


def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoke a refresh token"""
    db_token = get_refresh_token(db, token)
    if not db_token:
        return False
    
    db_token.is_revoked = True
    db.commit()
    return True


def revoke_all_user_tokens(db: Session, user_id: int) -> bool:
    """Revoke all refresh tokens for a user"""
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).update({"is_revoked": True})
    db.commit()
    return True 