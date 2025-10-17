import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path

# Import YOUR existing security functions
from utils.security import hash_password, verify_password

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
SESSION_TIMEOUT_MINUTES = 30

# ============================================================================
# File Management Functions
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
    if 'full_name' not in st.session_state:
        st.session_state.full_name = None
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None

def check_session_timeout():
    """Check if session has timed out"""
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
            return {}
        
        users = load_json(USERS_FILE, {})
        
        if not isinstance(users, dict):
            raise ValueError("Invalid users data structure")
        
        return users
        
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to JSON file"""
    save_json(USERS_FILE, users)

def authenticate(username, password):
    """Authenticate user credentials using YOUR security module"""
    try:
        users = load_users()
        
        if username not in users:
            return False, None, None
        
        user_data = users[username]
        
        # Use password_hash field (YOUR format)
        password_hash = user_data.get('password_hash')
        
        if not password_hash:
            return False, None, None
        
        # Use YOUR verify_password function from utils/security.py
        if verify_password(password, password_hash):
            role = user_data.get('role', 'Member')
            full_name = user_data.get('full_name', username)
            return True, role, full_name
        
        return False, None, None
        
    except Exception as e:
        print(f"Authentication error: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

# ============================================================================
# Login/Logout Functions
# ============================================================================

def login(username, role, full_name=None):
    """Set user as logged in"""
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.full_name = full_name or username
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
    st.session_state.full_name = None
    st.session_state.last_activity = None
    st.session_state.login_time = None

def log_audit_event(event_type, username, description):
    """Log audit events"""
    try:
        # Try to use your existing audit log function
        from utils.file_manager import add_audit_log
        add_audit_log(event_type, username, description)
    except ImportError:
        # Fallback to simple audit logging
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
        
        if len(audit_logs) > 1000:
            audit_logs = audit_logs[-1000:]
        
        save_json(audit_file, audit_logs)

# ============================================================================
# UI Functions
# ============================================================================

def show_login_ui():
    """Display login form and handle authentication"""
    init_session_state()
    
    if check_session_timeout():
        return False
    
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
            username = st.text_input("👤 Username / Employee ID", key="login_username")
            password = st.text_input("🔑 Password", type="password", key="login_password")
            
            submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not username or not password:
                st.error("❌ Please enter both username and password")
            else:
                with st.spinner("Authenticating..."):
                    success, role, full_name = authenticate(username, password)
                
                if success:
                    login(username, role, full_name)
                    st.success(f"✅ Welcome back, {full_name}!")
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
            st.markdown(f"**👤 User:** {st.session_state.full_name or st.session_state.username}")
            st.markdown(f"**🆔 ID:** {st.session_state.username}")
            st.markdown(f"**🎭 Role:** {st.session_state.role}")
            
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
    
    password_hash = users[username].get('password_hash')
    if not verify_password(old_password, password_hash):
        return False, "Incorrect current password"
    
    users[username]['password_hash'] = hash_password(new_password)
    users[username]['password_changed_at'] = datetime.now().isoformat()
    
    save_users(users)
    log_audit_event("password_change", username, "Password changed successfully")
    
    return True, "Password changed successfully"

def create_user(username, password, role="Member", full_name=None, created_by="admin"):
    """Create a new user"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "created_at": datetime.now().isoformat(),
        "created_by": created_by
    }
    
    if full_name:
        users[username]["full_name"] = full_name
    
    save_users(users)
    log_audit_event("user_created", created_by, f"Created new user: {username} with role: {role}")
    
    return True, "User created successfully"

def delete_user(username, deleted_by="admin"):
    """Delete a user"""
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
    """Get list of all users"""
    users = load_users()
    return {
        username: {
            "role": data.get("role", "Member"),
            "full_name": data.get("full_name", username),
            "created_at": data.get("created_at", "Unknown")
        }
        for username, data in users.items()
    }
