from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import get_user_by_id, update_user
from app.schemas import UserResponse, UserUpdate
from app.dependencies import get_current_active_user
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user


@router.patch("/profile", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    updated_user = update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id_endpoint(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (for admin purposes)"""
    # Only allow users to view their own profile or admin users
    if current_user.id != user_id and current_user.role.value != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user 