from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import get_user_by_id, update_user, create_user, get_user_by_email, get_user_by_username
from app.schemas import UserResponse, UserUpdate, UserCreate
from app.dependencies import get_current_active_user
from app.models import User, UserRole

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


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_by_teacher(
    payload: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Teacher/Admin creates a user (primarily students).

    Constraints:
    - Only teacher or admin can create users
    - If role is not student, only admin is allowed
    - email/username must be unique
    """
    if current_user.role not in [UserRole.teacher, UserRole.admin]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # Teachers can only create students
    if current_user.role == UserRole.teacher and payload.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="教師只能建立學生帳號")

    # basic unique checks
    if get_user_by_email(db, str(payload.email)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email 已存在")
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username 已存在")

    try:
        created = create_user(db, payload)
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))