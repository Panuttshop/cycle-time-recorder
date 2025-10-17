"""
Authentication module for Cycle Time Recorder
Handles user login, logout, and session management
"""
import streamlit as st
import json
from pathlib import Path
from utils.security import hash_password, verify_password
from utils.validation import validate_username, validate_password
from config.settings import DATA_DIR, USERS_FILE

def init_session_state():
    """Initialize session state variables for authentication"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

def load_users():
    """Load users from JSON file"""
    users_path = Path(DATA_DIR) / USERS_FILE
    if users_path.exists():
        with open(users_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    users_path = Path(DATA_DIR) / USERS_FILE
    users_path.parent.mkdir(parents=True, exist_ok=True)
    with open(users_path, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def authenticate_user(username, password):
    """Authenticate user credentials"""
    users = load_users()
    if username in users:
        user_data = users[username]
        if verify_password(password, user_data['password']):
            return True, user_data.get('role', 'user')
    return False, None

def login(username, password):
    """Handle user login"""
    is_valid, role = authenticate_user(username, password)
    if is_valid:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_role = role
        return True
    return False

def logout():
    """Handle user logout"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.rerun()  # FIXED: Changed from st.experimental_rerun()

def show_login_ui():
    """Display login UI and handle authentication"""
    init_session_state()
    
    # If already logged in, return True
    if st.session_state.logged_in:
        return True
    
    # Create login form
    st.title("🔐 Cycle Time Recorder - Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### Please login to continue")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    # Validate credentials
                    if login(username, password):
                        st.success(f"Welcome back, {username}!")
                        st.rerun()  # FIXED: Changed from st.experimental_rerun()
                    else:
                        st.error("Invalid username or password")
        
        # Add registration link or info
        st.markdown("---")
        st.info("Contact your administrator for account access.")
    
    return False

def create_user(username, password, role='user'):
    """Create a new user account"""
    users = load_users()
    
    # Validate username
    if not validate_username(username):
        return False, "Invalid username format"
    
    # Check if user already exists
    if username in users:
        return False, "Username already exists"
    
    # Validate password
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message
    
    # Create user
    users[username] = {
        'password': hash_password(password),
        'role': role,
        'created_at': str(Path(DATA_DIR).stat().st_mtime if Path(DATA_DIR).exists() else None)
    }
    
    save_users(users)
    return True, "User created successfully"

def change_password(username, old_password, new_password):
    """Change user password"""
    users = load_users()
    
    if username not in users:
        return False, "User not found"
    
    # Verify old password
    if not verify_password(old_password, users[username]['password']):
        return False, "Current password is incorrect"
    
    # Validate new password
    is_valid, message = validate_password(new_password)
    if not is_valid:
        return False, message
    
    # Update password
    users[username]['password'] = hash_password(new_password)
    save_users(users)
    
    return True, "Password changed successfully"

def delete_user(username):
    """Delete a user account"""
    users = load_users()
    
    if username not in users:
        return False, "User not found"
    
    # Prevent deleting the last admin
    admin_count = sum(1 for user in users.values() if user.get('role') == 'admin')
    if users[username].get('role') == 'admin' and admin_count <= 1:
        return False, "Cannot delete the last admin user"
    
    del users[username]
    save_users(users)
    
    return True, "User deleted successfully"

def is_admin():
    """Check if current user is admin"""
    return st.session_state.get('user_role') == 'admin'

def require_auth(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('logged_in', False):
            st.warning("Please login to access this page")
            show_login_ui()
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin role for a function"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('logged_in', False):
            st.warning("Please login to access this page")
            show_login_ui()
            st.stop()
        if not is_admin():
            st.error("This page requires administrator privileges")
            st.stop()
        return func(*args, **kwargs)
    return wrapper
