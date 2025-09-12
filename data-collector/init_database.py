#!/usr/bin/env python3
"""
Database initialization script for CatalystAI Data Collector

This script initializes the SQLite database and creates a demo user.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.database import DatabaseManager, create_database
import hashlib

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_database():
    """Initialize database with demo data"""
    print("🚀 Initializing CatalystAI Database...")
    
    # Create database tables
    engine = create_database()
    print("✅ Database tables created")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Reset ChromaDB for clean start
    print("🧹 Resetting ChromaDB for clean start...")
    from connectors.api_connector import APIConnectorManager
    from utils.chunking import ChunkingConfig, ChunkingStrategy
    
    chunking_config = ChunkingConfig(
        strategy=ChunkingStrategy.ENDPOINT_BASED,
        chunk_size=512,
        chunk_overlap=50
    )
    
    api_connector_manager = APIConnectorManager(chunking_config)
    api_connector_manager.load_environment()
    
    reset_success = api_connector_manager.reset_chromadb()
    if reset_success:
        print("✅ ChromaDB reset completed")
    else:
        print("⚠️ Warning: ChromaDB reset failed")
    
    # Create demo user
    demo_user = db_manager.get_user_by_username("demo_user")
    if not demo_user:
        demo_user = db_manager.create_user(
            username="demo_user",
            email="demo@catalystai.com",
            full_name="Demo User",
            password_hash=hash_password("demo123"),
            is_admin=True
        )
        print("✅ Demo user created (username: demo_user, password: demo123)")
    else:
        print("ℹ️  Demo user already exists")
    
    # Create demo application
    demo_app = db_manager.get_application_by_id(1)
    if not demo_app:
        demo_app = db_manager.create_application(
            name="Demo Application",
            description="Demo application for testing API specifications",
            sealid="105961",
            owner_id=demo_user.id,
            app_metadata={"environment": "demo", "team": "catalystai"}
        )
        print("✅ Demo application created")
    else:
        print("ℹ️  Demo application already exists")
    
    print("\n🎉 Database initialization complete!")
    print("\n📋 Demo Credentials:")
    print("   Username: demo_user")
    print("   Password: demo123")
    print("   Token: demo-token")
    print("\n🔗 API Endpoints:")
    print("   POST /users/ - Create user")
    print("   GET /users/me - Get current user")
    print("   POST /applications/ - Create application")
    print("   GET /applications/ - List applications")
    print("   POST /upload - Upload API spec")
    print("   POST /convert - Convert API spec")

if __name__ == "__main__":
    initialize_database()
