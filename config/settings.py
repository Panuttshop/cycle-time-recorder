"""
Settings and Maintenance Page
"""
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from utils.security import verify_password, validate_password_strength, hash_password
from utils.file_manager import load_users, save_users, load_records, save_records, add_audit_log
from config.settings import DATA_FILE, USERS_FILE, AUDIT_FILE


def show():
    """Display settings page"""
    st.title("⚙️ Settings & Maintenance")
    
    if st.session_state.role != "Admin":
        st.error("❌ Admin access required")
        return
    
    # Change Password Section
    st.markdown("## 🔑 Change Your Password")
    with st.form("change_pwd_form"):
        old_pwd = st.text_input("Current Password", type="password")
        new_pwd = st.text_input("New Password", type="password")
        confirm_pwd = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("🔐 Change Password"):
            users = load_users()
            current_user_data = users[st.session_state.username]
            
            if not verify_password(old_pwd, current_user_data['password_hash']):
                st.error("❌ Current password is incorrect")
            elif new_pwd != confirm_pwd:
                st.error("❌ New passwords don't match")
            else:
                valid, msg = validate_password_strength(new_pwd)
                if not valid:
                    st.error(msg)
                else:
                    users[st.session_state.username]['password_hash'] = hash_password(new_pwd)
                    if save_users(users):
                        add_audit_log("CHANGE_PASSWORD", st.session_state.username)
                        st.success("✅ Password changed successfully")
                    else:
                        st.error("❌ Failed to save new password")
    
    st.markdown("---")
    
    # Data Maintenance Section
    st.markdown("## 📊 Data Maintenance")
    
    records = load_records()
    st.metric("Total Records", len(records))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🧹 Clean Old Records")
        days_old = st.slider("Delete records older than (days)", 0, 365, 90)
        
        if st.button("🗑️ Delete Old Records"):
            cutoff_date = (datetime.now() - timedelta(days=days_old)).date()
            original_count = len(records)
            
            records = [r for r in records if pd.to_datetime(r.date).date() > cutoff_date]
            deleted = original_count - len(records)
            
            if save_records(records):
                add_audit_log("DELETE_OLD_RECORDS", st.session_state.username, f"Deleted {deleted} records")
                st.success(f"✅ Deleted {deleted} records")
            else:
                st.error("❌ Failed to delete records")
    
    with col2:
        st.markdown("#### 📋 Export All Data")
        if st.button("📤 Export All Records"):
            data = [r.to_dict() for r in records]
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            st.download_button(
                "📥 Download JSON",
                json_str,
                f"all_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )
    
    st.markdown("---")
    
    # System Information Section
    st.markdown("## 🔍 System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Statistics**")
        records = load_records()
        users = load_users()
        
        st.write(f"- Total Records: **{len(records)}**")
        st.write(f"- Total Users: **{len(users)}**")
        st.write(f"- Admin Users: **{sum(1 for u in users.values() if u['role'] == 'Admin')}**")
        
        if records:
            dates = [pd.to_datetime(r.date).date() for r in records]
            st.write(f"- Date Range: **{min(dates)} to {max(dates)}**")
    
    with col2:
        st.markdown("**File Information**")
        
        try:
            data_size = os.path.getsize(DATA_FILE) / 1024
            users_size = os.path.getsize(USERS_FILE) / 1024
            audit_size = os.path.getsize(AUDIT_FILE) / 1024 if os.path.exists(AUDIT_FILE) else 0
            
            st.write(f"- Data File: **{data_size:.1f} KB**")
            st.write(f"- Users File: **{users_size:.1f} KB**")
            st.write(f"- Audit Log: **{audit_size:.1f} KB**")
            st.write(f"- Total: **{(data_size + users_size + audit_size):.1f} KB**")
        except Exception as e:
            st.error(f"Error getting file info: {e}")
