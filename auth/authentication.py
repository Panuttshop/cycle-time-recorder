import streamlit as st
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
SESSION_TIMEOUT_MINUTES = 30

# ============================================================================
# TEMPORARY: Set usernames that can login without password check
# ============================================================================
EMERGENCY_USERS = ["admin", "29006406"]  # These can login with ANY password
USE_EMERGENCY_LOGIN = True  # Set to False after fixing passwords

# ============================================================================
# Password Functions (handles both : and $ separators)
# ============================================================================

def verify_password_both_formats(password: str, hashed_password: str) -> bool:
    """Verify password - supports both : and $ separators"""
    try:
        # Try $ separator first
        if '$' in hashed_password:
            salt, original_hash = hashed_password.split('$', 1)
            password_salt = f"{password}{salt}"
            new_hash = hashlib.sha256(password_salt.encode()).hexdigest()
            if new_hash == original_hash:
                return True
        
        # Try : separator
        if ':' in hashed_password:
            salt, original_hash = hashed_password.split(':', 1)
            password_salt = f"{password}{salt}"
            new_hash = hashlib.sha256(password_salt.encode()).hexdigest()
            if new_hash == original_hash:
                return True
        
        return False
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

# ============================================================================
# File Management
# ============================================================================

def load_json(file_path: Path, default=None):
    try:
        if not file_path.exists():
            return default if default is not None else {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default if default is not None else {}

def save_json(file_path: Path, data):
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving: {e}")

# ============================================================================
# Session Management
# ============================================================================

def init_session_state():
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
    if st.session_state.logged_in and st.session_state.last_activity:
        last_activity = datetime.fromisoformat(st.session_state.last_activity)
        if datetime.now() - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            logout()
            st.warning(f"⏱️ Session expired after {SESSION_TIMEOUT_MINUTES} minutes.")
            return True
    return False

def update_activity():
    if st.session_state.logged_in:
        st.session_state.last_activity = datetime.now().isoformat()

# ============================================================================
# User Management
# ============================================================================

def load_users():
    try:
        if not USERS_FILE.exists():
            return {}
        users = load_json(USERS_FILE, {})
        return users if isinstance(users, dict) else {}
    except:
        return {}

def authenticate(username, password):
    """Authenticate user with EMERGENCY LOGIN option"""
    try:
        users = load_users()
        
        # Check if user exists
        if username not in users:
            return False, None, None
        
        user_data = users[username]
        
        # EMERGENCY LOGIN - Allow specific users without password check
        if USE_EMERGENCY_LOGIN and username in EMERGENCY_USERS:
            role = user_data.get('role', 'Member')
            full_name = user_data.get('full_name', username)
            return True, role, full_name
        
        # Normal password verification
        password_hash = user_data.get('password_hash') or user_data.get('password')
        
        if password_hash and verify_password_both_formats(password, password_hash):
            role = user_data.get('role', 'Member')
            full_name = user_data.get('full_name', username)
            return True, role, full_name
        
        return False, None, None
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return False, None, None

def login(username, role, full_name=None):
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.full_name = full_name or username
    st.session_state.login_time = datetime.now().isoformat()
    st.session_state.last_activity = datetime.now().isoformat()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.full_name = None
    st.session_state.last_activity = None
    st.session_state.login_time = None

# ============================================================================
# UI Functions
# ============================================================================

def show_login_ui():
    init_session_state()
    
    if check_session_timeout():
        return False
    
    if st.session_state.logged_in:
        update_activity()
        return True
    
    # Login form
    st.title("🔐 Cycle Time Recorder - Login")
    
    # Show emergency login warning
    if USE_EMERGENCY_LOGIN:
        st.error("🚨 EMERGENCY LOGIN MODE ACTIVE")
        st.warning(f"Users {EMERGENCY_USERS} can login with any password")
        st.info("Set USE_EMERGENCY_LOGIN = False in authentication.py after fixing passwords")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please sign in")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username / Employee ID")
            password = st.text_input("🔑 Password", type="password")
            
            submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not username:
                st.error("❌ Please enter username")
            else:
                success, role, full_name = authenticate(username, password)
                
                if success:
                    login(username, role, full_name)
                    st.success(f"✅ Welcome, {full_name}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
                    
                    # Show debug info
                    users = load_users()
                    if username in users:
                        st.info(f"User '{username}' exists but password is incorrect")
                    else:
                        st.info(f"User '{username}' not found in system")
                        st.info(f"Available users: {', '.join(users.keys())}")
    
    return False

def show_user_info():
    if st.session_state.logged_in:
        with st.sidebar:
            st.markdown("---")
            
            if USE_EMERGENCY_LOGIN:
                st.error("🚨 EMERGENCY MODE")
            
            st.markdown(f"**👤 User:** {st.session_state.full_name or st.session_state.username}")
            st.markdown(f"**🆔 ID:** {st.session_state.username}")
            st.markdown(f"**🎭 Role:** {st.session_state.role}")
            
            if st.session_state.login_time:
                login_time = datetime.fromisoformat(st.session_state.login_time)
                st.caption(f"Logged in: {login_time.strftime('%H:%M:%S')}")
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()

# ============================================================================
# Additional Functions
# ============================================================================

def get_all_users():
    users = load_users()
    return {
        username: {
            "role": data.get("role", "Member"),
            "full_name": data.get("full_name", username),
            "created_at": data.get("created_at", "Unknown")
        }
        for username, data in users.items()
    }
