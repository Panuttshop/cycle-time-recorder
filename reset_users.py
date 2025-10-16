"""
Emergency Reset Utility for Cycle Time Recorder

This script resets the users.json file to default admin account.
Use this if you're locked out or have corrupted user data.

Usage:
    python reset_users.py
"""

import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
BACKUP_FILE = DATA_DIR / "users.json.backup"

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt"""
    salt = secrets.token_hex(16)
    password_salt = f"{password}{salt}"
    hashed = hashlib.sha256(password_salt.encode()).hexdigest()
    return f"{salt}:{hashed}"

def backup_existing_users():
    """Create backup of existing users file"""
    if USERS_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = DATA_DIR / f"users.json.backup_{timestamp}"
        
        with open(USERS_FILE, 'r') as src:
            content = src.read()
        
        with open(backup_path, 'w') as dst:
            dst.write(content)
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    return None

def reset_users():
    """Reset users to default admin account"""
    print("=" * 60)
    print("🔧 Cycle Time Recorder - User Reset Utility")
    print("=" * 60)
    print()
    
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Backup existing users
    if USERS_FILE.exists():
        print("📦 Backing up existing users.json...")
        backup_path = backup_existing_users()
        if backup_path:
            print(f"   Backup saved to: {backup_path}")
    
    # Create default admin user
    default_users = {
        "admin": {
            "password": hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.now().isoformat(),
            "reset_at": datetime.now().isoformat(),
            "reset_reason": "Emergency reset utility"
        }
    }
    
    # Save new users file
    print()
    print("🔄 Creating new users.json with default admin...")
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_users, f, indent=2, ensure_ascii=False)
    
    print("✅ Users file reset successfully!")
    print()
    print("=" * 60)
    print("📝 Default Login Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT: Change the admin password after logging in!")
    print("   Go to Settings > Change Password")
    print()
    print("🎉 You can now login to your application!")
    print()

def show_current_users():
    """Display current users in the system"""
    if not USERS_FILE.exists():
        print("❌ No users.json file found")
        return
    
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        
        print("=" * 60)
        print("👥 Current Users:")
        print("=" * 60)
        
        for username, data in users.items():
            role = data.get('role', 'unknown')
            created = data.get('created_at', 'unknown')
            print(f"   • {username} ({role}) - Created: {created}")
        
        print("=" * 60)
        print()
    except Exception as e:
        print(f"❌ Error reading users: {e}")

if __name__ == "__main__":
    print()
    print("Choose an option:")
    print("1. Reset users (create new admin account)")
    print("2. Show current users")
    print("3. Exit")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    print()
    
    if choice == "1":
        confirm = input("⚠️  This will reset all users. Continue? (yes/no): ").strip().lower()
        if confirm == "yes":
            reset_users()
        else:
            print("❌ Reset cancelled")
    elif choice == "2":
        show_current_users()
    else:
        print("👋 Goodbye!")