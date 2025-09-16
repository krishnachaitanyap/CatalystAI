"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

from config.settings import settings
from models.database.models import Base


# Create database engine
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(settings.database_url)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with default data"""
    create_tables()
    
    # Create default admin user if it doesn't exist
    from services.user_service import UserService
    from utils.security import get_password_hash
    
    db = SessionLocal()
    try:
        user_service = UserService(db)
        admin_user = user_service.get_user_by_username("admin")
        
        if not admin_user:
            user_service.create_user({
                "username": "admin",
                "email": "admin@prodassist.com",
                "password": "admin123",
                "is_admin": True
            })
            print("✅ Created default admin user (username: admin, password: admin123)")
        
    finally:
        db.close()
