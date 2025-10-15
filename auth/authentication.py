"""
Authentication Functions
"""
import streamlit as st
import time
from typing import Tuple
from utils.security import hash_password, verify_password, validate_password_strength
from utils.file_manager import load_users, save_users, add_audit_log
from config.settings import DEFAULT_ADMIN


def do_login(username: str, password: str) -> bool:
    """
    Authenticate user
    
    Args:
        username: Username
        password: Password
        
    Returns:
        True if authentication successful
    """
    users = load_users()
    if username in users and verify_password(password, users[username]["password_hash"]):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = users[username]["role"]
        st.session_state.login_attempts[username] = [0, time.time()]
        add_audit_log("LOGIN", username)
        return True
    
    st.session_state.login_attempts[username] = [
        st.session_state.login_attempts.get(username, [0, time.time()])[0] + 1,
        time.time()
    ]
    return False


def do_logout():
    """Logout current user"""
    username = st.session_state.username
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = ""
    add_audit_log("LOGOUT", username)


def show_login_ui() -> bool:
    """
    Display login UI in sidebar
    
    Returns:
        True if user is logged in
    """
    st.sidebar.title("🔐 Login")
    
    if st.session_state.logged_in:
        users = load_users()
        full_name = users.get(st.session_state.username, {}).get('full_name', '')
        display_name = full_name if full_name else st.session_state.username
        
        st.sidebar.success(f"✓ {display_name}")
        st.sidebar.caption(f"Role: {st.session_state.role}")
        if st.sidebar.button("🚪 Logout"):
            do_logout()
            st.experimental_rerun()
        return True
    
    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if do_login(username.strip(), password):
                st.experimental_rerun()
            else:
                st.error("❌ Username หรือ Password ไม่ถูกต้อง")
    
    st.sidebar.markdown("---")
    st.sidebar.info("📞 ติดต่อ Admin เพื่อเพิ่มบัญชีผู้ใช้")
    return False


def add_user(username: str, password: str, role: str = "Member", full_name: str = "") -> Tuple[bool, str]:
    """
    Add a new user
    
    Args:
        username: New username
        password: New password
        role: User role (Member/Admin)
        full_name: Full name of user
        
    Returns:
        Tuple of (success, message)
    """
    username = username.strip()
    if not username:
        return False, "username ว่าง"
    
    valid, msg = validate_password_strength(password)
    if not valid:
        return False, msg
    
    users = load_users()
    if username in users:
        return False, "username มีอยู่แล้ว"
    
    users[username] = {
        "password_hash": hash_password(password),
        "role": role.title(),
        "full_name": full_name.strip()
    }
    
    if save_users(users):
        add_audit_log("ADD_USER", st.session_state.username, f"Added user: {username} ({full_name})")
        return True, "เพิ่มผู้ใช้เรียบร้อย"
    return False, "เกิดข้อผิดพลาด"


def remove_user(username: str) -> Tuple[bool, str]:
    """
    Remove a user
    
    Args:
        username: Username to remove
        
    Returns:
        Tuple of (success, message)
    """
    if username == DEFAULT_ADMIN[0]:
        return False, "ไม่อนุญาตให้ลบบัญชี admin เริ่มต้น"
    
    users = load_users()
    if username not in users:
        return False, "ไม่พบ username"
    
    del users[username]
    if save_users(users):
        add_audit_log("REMOVE_USER", st.session_state.username, f"Removed user: {username}")
        return True, "ลบผู้ใช้เรียบร้อย"
    return False, "เกิดข้อผิดพลาด"
