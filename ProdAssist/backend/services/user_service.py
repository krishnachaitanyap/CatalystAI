"""
User service for managing user operations
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.database.models import User
from models.schemas.schemas import UserCreate, UserUpdate
from utils.security import get_password_hash, verify_password
from utils.logging import LoggerMixin


class UserService(LoggerMixin):
    """Service for user management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        try:
            # Hash password
            hashed_password = get_password_hash(user_data["password"])
            
            # Create user
            db_user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hashed_password,
                is_active=user_data.get("is_active", True),
                is_admin=user_data.get("is_admin", False)
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            self.logger.info(f"✅ Created user: {db_user.username}")
            return db_user
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Error creating user: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        try:
            db_user = self.get_user_by_id(user_id)
            if not db_user:
                return None
            
            # Update fields
            update_data = user_data.dict(exclude_unset=True)
            
            # Hash password if provided
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            for field, value in update_data.items():
                setattr(db_user, field, value)
            
            self.db.commit()
            self.db.refresh(db_user)
            
            self.logger.info(f"✅ Updated user: {db_user.username}")
            return db_user
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Error updating user: {str(e)}")
            raise
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by deactivating)"""
        try:
            db_user = self.get_user_by_id(user_id)
            if not db_user:
                return False
            
            db_user.is_active = False
            self.db.commit()
            
            self.logger.info(f"✅ Deactivated user: {db_user.username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Error deleting user: {str(e)}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    def verify_user_password(self, user: User, password: str) -> bool:
        """Verify user password"""
        return verify_password(password, user.hashed_password)
