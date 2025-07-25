#!/usr/bin/env python3
"""
Setup script for MongoDB task integration
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please copy env.example to .env and configure it:")
        print("   cp env.example .env")
        return False
    
    print("✅ .env file found")
    
    # Check for required MongoDB variables
    required_vars = ['MONGODB_CONNECTION_STRING', 'MONGODB_DATABASE']
    missing_vars = []
    
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f'{var}=' not in content or f'{var}=your-' in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or unconfigured variables: {', '.join(missing_vars)}")
        print("📝 Please update your .env file with actual values")
        return False
    
    print("✅ Required environment variables are configured")
    return True

def test_mongodb_connection():
    """Test MongoDB connection."""
    try:
        from mongodb.task_service import TaskService
        
        print("\n🔌 Testing MongoDB connection...")
        service = TaskService()
        
        if service.connect():
            print("✅ MongoDB connection successful!")
            service.disconnect()
            return True
        else:
            print("❌ MongoDB connection failed!")
            print("📝 Please check your MONGODB_CONNECTION_STRING in .env")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📝 Please install required dependencies: pip install pymongo python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def check_dependencies():
    """Check if required Python packages are installed."""
    required_packages = ['pymongo', 'dotenv', 'fastapi']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📝 Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required packages are installed")
    return True

def main():
    """Main setup function."""
    print("🚀 MongoDB Task Integration Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check environment file
    if not check_env_file():
        return False
    
    # Test MongoDB connection
    if not test_mongodb_connection():
        return False
    
    print("\n🎉 Setup complete! MongoDB task integration is ready.")
    print("\n📋 Next steps:")
    print("   1. Start the backend: python3 main.py")
    print("   2. Start the frontend: cd frontend && npm run dev")
    print("   3. Test the integration: python3 test_mongodb_tasks.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 