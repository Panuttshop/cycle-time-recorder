import streamlit as st
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
SESSION_TIMEOUT_MINUTES = 30

# ============================================================================
# Security Functions (self-contained)
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt"""
    salt = secrets.token_hex(16)
    password_salt = f"{password}{salt}"
    hashed = hashlib.sha256(password_salt.encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password (supports old and new formats)"""
    try:
        # New format: salt:hash
        if ':' in hashed_password:
            salt, original_hash = hashed_password.split(':', 1)
            password_salt = f"{password}{salt}"
            new_hash = hashlib.sha256(password_salt.encode()).hexdigest()
            return new_hash == original_hash
        else:
            # Old format: direct hash (no salt) - for backwards compatibility
            direct_hash = hashlib.sha256(password.encode()).hexdigest()
            return direct_hash == hashed_password
    except (ValueError, AttributeError, TypeError):
        return False

def validate_password_strength(password: str) -> tuple:
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    has_letter = any(char.isalpha() for char in password)
    if not has_letter:
        return False, "Password must contain at least one letter"
    return True, "Password is valid"

# ============================================================================
# File Management Functions (self-contained)
# ============================================================================

def load_json(file_path: Path, default=None):
    """Load JSON data from file"""
    try:
        if not file_path.exists():
            return default if default is not None else {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default if default is not None else {}
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return default if default is not None else {}

def save_json(file_path: Path, data, indent: int = 2):
    """Save data to JSON file"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup if file exists
        if file_path.exists():
            backup_path = file_path.with_suffix('.json.bak')
            import shutil
            shutil.copy2(file_path, backup_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        raise

# ============================================================================
# Session Management
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None

def check_session_timeout():
    """Check if session has timed out (30 minutes of inactivity)"""
    if st.session_state.logged_in and st.session_state.last_activity:
        last_activity = datetime.fromisoformat(st.session_state.last_activity)
        if datetime.now() - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            logout()
            st.warning(f"⏱️ Your session has expired after {SESSION_TIMEOUT_MINUTES} minutes of inactivity. Please login again.")
            return True
    return False

def update_activity():
    """Update last activity timestamp"""
    if st.session_state.logged_in:
        st.session_state.last_activity = datetime.now().isoformat()

# ============================================================================
# User Management
# ============================================================================

def load_users():
    """Load users from JSON file"""
    try:
        if not USERS_FILE.exists():
            # Create default admin user if no users exist
            default_users = {
                "admin": {
                    "password": hash_password("admin123"),
                    "role": "admin",
                    "created_at": datetime.now().isoformat()
                }
            }
            save_json(USERS_FILE, default_users)
            return default_users
        
        users = load_json(USERS_FILE, {})
        
        # Validate users data structure
        if not isinstance(users, dict):
            raise ValueError("Invalid users data structure")
        
        # Ensure admin user exists with correct structure
        if "admin" not in users or not isinstance(users.get("admin"), dict):
            users["admin"] = {
                "password": hash_password("admin123"),
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
            save_json(USERS_FILE, users)
        
        return users
        
    except Exception as e:
        print(f"Error loading users: {e}")
        # Return default admin user on any error
        default_users = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
        }
        save_json(USERS_FILE, default_users)
        return default_users

def save_users(users):
    """Save users to JSON file"""
    save_json(USERS_FILE, users)

def authenticate(username, password):
    """Authenticate user credentials"""
    try:
        users = load_users()
        
        if username not in users:
            return False, None
        
        user_data = users[username]
        
        # Check if password field exists
        if 'password' not in user_data:
            # User data is corrupted, recreate default admin if this is admin
            if username == "admin":
                users[username]['password'] = hash_password("admin123")
                save_users(users)
                user_data = users[username]
            else:
                return False, None
        
        if verify_password(password, user_data['password']):
            # Automatically upgrade old password format to new format
            if ':' not in user_data['password']:
                users[username]['password'] = hash_password(password)
                save_users(users)
            
            return True, user_data.get('role', 'user')
        
        return False, None
    except Exception as e:
        print(f"Authentication error: {e}")
        return False, None

# ============================================================================
# Login/Logout Functions
# ============================================================================

def login(username, role):
    """Set user as logged in"""
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.login_time = datetime.now().isoformat()
    st.session_state.last_activity = datetime.now().isoformat()
    log_audit_event("login", username, "User logged in successfully")

def logout():
    """Clear session and log out user"""
    username = st.session_state.get('username', 'Unknown')
    
    if st.session_state.logged_in:
        log_audit_event("logout", username, "User logged out")
    
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.last_activity = None
    st.session_state.login_time = None

def log_audit_event(event_type, username, description):
    """Log audit events"""
    audit_file = DATA_DIR / "audit_log.json"
    
    audit_logs = []
    if audit_file.exists():
        audit_logs = load_json(audit_file, [])
    
    audit_logs.append({
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "username": username,
        "description": description
    })
    
    # Keep only last 1000 entries
    if len(audit_logs) > 1000:
        audit_logs = audit_logs[-1000:]
    
    save_json(audit_file, audit_logs)

# ============================================================================
# UI Functions
# ============================================================================

def show_login_ui():
    """Display login form and handle authentication"""
    init_session_state()
    
    # Check for session timeout
    if check_session_timeout():
        return False
    
    # If already logged in, update activity and return True
    if st.session_state.logged_in:
        update_activity()
        return True
    
    # Show login form
    st.title("🔐 Cycle Time Recorder - Login")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please sign in to continue")
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", key="login_username")
            password = st.text_input("🔑 Password", type="password", key="login_password")
            
            col_login, col_info = st.columns([1, 1])
            
            with col_login:
                submit_button = st.form_submit_button("Login", use_container_width=True)
            
            with col_info:
                st.markdown("**Default Admin:**")
                st.caption("User: `admin`")
                st.caption("Pass: `admin123`")
        
        if submit_button:
            if not username or not password:
                st.error("❌ Please enter both username and password")
            else:
                success, role = authenticate(username, password)
                
                if success:
                    login(username, role)
                    st.success(f"✅ Welcome back, {username}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
                    log_audit_event("failed_login", username, "Failed login attempt")
    
    return False

def show_user_info():
    """Display logged in user information in sidebar"""
    if st.session_state.logged_in:
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 User:** {st.session_state.username}")
            st.markdown(f"**🎭 Role:** {st.session_state.role.upper()}")
            
            # Show session info
            if st.session_state.login_time:
                login_time = datetime.fromisoformat(st.session_state.login_time)
                st.caption(f"Logged in: {login_time.strftime('%H:%M:%S')}")
            
            if st.session_state.last_activity:
                last_activity = datetime.fromisoformat(st.session_state.last_activity)
                time_remaining = SESSION_TIMEOUT_MINUTES - (datetime.now() - last_activity).seconds // 60
                if time_remaining > 0:
                    st.caption(f"⏱️ Session timeout: {time_remaining} min")
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()

# ============================================================================
# Additional User Management Functions
# ============================================================================

def change_password(username, old_password, new_password):
    """Change user password"""
    users = load_users()
    
    if username not in users:
        return False, "User not found"
    
    # Verify old password
    if not verify_password(old_password, users[username]['password']):
        return False, "Incorrect current password"
    
    # Update password
    users[username]['password'] = hash_password(new_password)
    users[username]['password_changed_at'] = datetime.now().isoformat()
    
    save_users(users)
    log_audit_event("password_change", username, "Password changed successfully")
    
    return True, "Password changed successfully"

def create_user(username, password, role="user", created_by="admin"):
    """Create a new user (admin only)"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        "password": hash_password(password),
        "role": role,
        "created_at": datetime.now().isoformat(),
        "created_by": created_by
    }
    
    save_users(users)
    log_audit_event("user_created", created_by, f"Created new user: {username} with role: {role}")
    
    return True, "User created successfully"

def delete_user(username, deleted_by="admin"):
    """Delete a user (admin only)"""
    if username == "admin":
        return False, "Cannot delete admin user"
    
    users = load_users()
    
    if username not in users:
        return False, "User not found"
    
    del users[username]
    save_users(users)
    log_audit_event("user_deleted", deleted_by, f"Deleted user: {username}")
    
    return True, "User deleted successfully"

def get_all_users():
    """Get list of all users (admin only)"""
    users = load_users()
    return {
        username: {
            "role": data["role"],
            "created_at": data.get("created_at", "Unknown")
        }
        for username, data in users.items()
    }

def require_auth(role_required=None):
    """Decorator to require authentication for a page"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            init_session_state()
            
            if check_session_timeout():
                return False
            
            if not st.session_state.logged_in:
                st.warning("⚠️ Please login to access this page")
                return False
            
            update_activity()
            
            if role_required and st.session_state.role != role_required:
                st.error(f"❌ Access denied. This page requires {role_required} role.")
                return False
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
