"""
Admin Panel Page
"""
import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from auth.authentication import add_user, remove_user
from utils.file_manager import load_users, load_records, add_audit_log
from config.settings import DEFAULT_ADMIN, AUDIT_FILE


def show():
    """Display admin panel"""
    st.title("🔒 Admin Panel")
    
    # User Management Section
    st.markdown("## 👥 User Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ➕ เพิ่มผู้ใช้")
        with st.form("add_user_form"):
            new_user = st.text_input("Username")
            new_full_name = st.text_input("Full Name")
            new_pass = st.text_input("Password", type="password")
            new_pass_conf = st.text_input("Confirm Password", type="password")
            new_role = st.selectbox("Role", ["Member", "Admin"])
            
            if st.form_submit_button("➕ Add User"):
                if not new_user or not new_pass:
                    st.error("❌ กรอก username และ password")
                elif new_pass != new_pass_conf:
                    st.error("❌ Password ไม่ตรงกัน")
                else:
                    ok, msg = add_user(new_user, new_pass, new_role, new_full_name)
                    if ok:
                        st.success(msg)
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error(msg)
    
    with col2:
        st.markdown("#### 🗑️ ลบผู้ใช้")
        users = load_users()
        user_list = [u for u in users.keys() if u != DEFAULT_ADMIN[0]]
        
        if user_list:
            to_remove = st.selectbox("เลือกผู้ใช้:", user_list)
            if st.button("🗑️ Remove User"):
                if st.session_state.username == to_remove:
                    st.error("❌ ไม่สามารถลบบัญชีตัวเอง")
                else:
                    ok, msg = remove_user(to_remove)
                    if ok:
                        st.success(msg)
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error(msg)
        else:
            st.info("ไม่มีผู้ใช้ที่สามารถลบได้")
    
    st.markdown("---")
    st.markdown("#### 👥 Current Users")
    
    users = load_users()
    user_data = []
    for username in users:
        user_data.append({
            "Username": username,
            "Full Name": users[username].get("full_name", ""),
            "Role": users[username]["role"]
        })
    
    st.dataframe(pd.DataFrame(user_data))
    
    # Change User Role Section
    st.markdown("---")
    st.markdown("#### 🔄 Change User Role")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get list of users excluding current admin if they want to prevent self-demotion
        user_list_for_role = [u for u in users.keys()]
        selected_user = st.selectbox("Select User:", user_list_for_role, key="role_change_user")
    
    with col2:
        if selected_user:
            current_role = users[selected_user]["role"]
            st.info(f"Current Role: **{current_role}**")
            
            new_role = st.selectbox(
                "New Role:",
                ["Member", "Admin"],
                index=0 if current_role == "Member" else 1,
                key="new_role_select"
            )
            
            if st.button("🔄 Change Role"):
                if selected_user == DEFAULT_ADMIN[0] and new_role == "Member":
                    st.error("❌ ไม่สามารถเปลี่ยน role ของ admin เริ่มต้นเป็น Member ได้")
                elif selected_user == st.session_state.username and new_role == "Member":
                    st.warning("⚠️ คุณกำลังจะเปลี่ยน role ของตัวเองเป็น Member - คุณจะสูญเสียสิทธิ์ Admin!")
                    if st.button("⚠️ ยืนยันการเปลี่ยน Role ของตัวเอง"):
                        users[selected_user]["role"] = new_role
                        if save_users(users):
                            add_audit_log("CHANGE_ROLE", st.session_state.username, 
                                        f"Changed {selected_user} role to {new_role}")
                            st.success(f"✅ เปลี่ยน role ของ {selected_user} เป็น {new_role} เรียบร้อย")
                            st.session_state.role = new_role  # Update current session
                            time.sleep(2)
                            st.experimental_rerun()
                        else:
                            st.error("❌ เกิดข้อผิดพลาดในการบันทึก")
                else:
                    users[selected_user]["role"] = new_role
                    if save_users(users):
                        add_audit_log("CHANGE_ROLE", st.session_state.username, 
                                    f"Changed {selected_user} role from {current_role} to {new_role}")
                        st.success(f"✅ เปลี่ยน role ของ {selected_user} เป็น {new_role} เรียบร้อย")
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error("❌ เกิดข้อผิดพลาดในการบันทึก")
    
    st.markdown("---")
    
    # Audit Trail Section
    st.markdown("## 📋 Audit Trail")
    try:
        with open(AUDIT_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        if logs:
            df_logs = pd.DataFrame(logs).tail(50)
            st.dataframe(df_logs)
        else:
            st.info("ไม่มี log")
    except Exception as e:
        st.error(f"Error loading audit log: {e}")
    
    st.markdown("---")
    
    # Backup Section
    st.markdown("## 💾 Data Backup")
    if st.button("💾 Create Backup Now"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"cycle_records_backup_{timestamp}.json"
        
        try:
            records = load_records()
            data = [r.to_dict() for r in records]
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            st.success(f"✅ Backup created: {backup_file}")
            add_audit_log("BACKUP", st.session_state.username)
        except Exception as e:
            st.error(f"❌ Backup failed: {e}")