import streamlit as st
from datetime import datetime

# Import authentication functions
try:
    from auth.authentication import create_user, delete_user, get_all_users, load_json, validate_password_strength
    from pathlib import Path
    DATA_DIR = Path("data")
except ImportError:
    st.error("Cannot import authentication module")

def show():
    """Display admin panel (admin only)"""
    st.title("👨‍💼 Admin Panel")
    st.markdown("---")
    
    if st.session_state.role != "admin":
        st.error("❌ Access denied. Admin privileges required.")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📋 Audit Log", "🗄️ System Info"])
    
    with tab1:
        show_user_management()
    
    with tab2:
        show_audit_log()
    
    with tab3:
        show_system_info()

def show_user_management():
    """User management interface"""
    st.header("User Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Create New User")
        
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
            
            create_btn = st.form_submit_button("Create User", use_container_width=True)
            
            if create_btn:
                if not new_username or not new_password:
                    st.error("❌ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    is_valid, msg = validate_password_strength(new_password)
                    if not is_valid:
                        st.error(f"❌ {msg}")
                    else:
                        success, message = create_user(
                            new_username, 
                            new_password, 
                            new_role,
                            st.session_state.username
                        )
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
    
    with col2:
        st.subheader("Delete User")
        
        users = get_all_users()
        user_list = [u for u in users.keys() if u != "admin"]
        
        if user_list:
            with st.form("delete_user_form"):
                user_to_delete = st.selectbox("Select User", user_list)
                delete_btn = st.form_submit_button("Delete User", use_container_width=True, type="primary")
                
                if delete_btn:
                    success, message = delete_user(user_to_delete, st.session_state.username)
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        else:
            st.info("No users to delete")
    
    st.markdown("---")
    
    # Display all users
    st.subheader("All Users")
    users = get_all_users()
    
    if users:
        import pandas as pd
        user_df = pd.DataFrame([
            {
                "Username": username,
                "Role": info["role"],
                "Created": info["created_at"]
            }
            for username, info in users.items()
        ])
        st.dataframe(user_df, use_container_width=True, hide_index=True)
    else:
        st.info("No users found")

def show_audit_log():
    """Display audit log"""
    st.header("Audit Log")
    
    audit_file = DATA_DIR / "audit_log.json"
    
    if audit_file.exists():
        audit_logs = load_json(audit_file, [])
        
        if audit_logs:
            # Show recent logs
            st.subheader(f"Recent Activities (Last {min(50, len(audit_logs))} entries)")
            
            import pandas as pd
            recent_logs = audit_logs[-50:][::-1]  # Last 50, reversed
            
            log_df = pd.DataFrame(recent_logs)
            st.dataframe(log_df, use_container_width=True, hide_index=True)
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_events = len(audit_logs)
                st.metric("Total Events", f"{total_events:,}")
            
            with col2:
                login_events = len([l for l in audit_logs if l['event_type'] == 'login'])
                st.metric("Total Logins", f"{login_events:,}")
            
            with col3:
                failed_logins = len([l for l in audit_logs if l['event_type'] == 'failed_login'])
                st.metric("Failed Logins", f"{failed_logins:,}")
        else:
            st.info("No audit logs found")
    else:
        st.info("Audit log file not found")

def show_system_info():
    """Display system information"""
    st.header("System Information")
    
    import sys
    from pathlib import Path
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Application Info")
        st.markdown(f"""
        **Version:** 1.0.0  
        **Python:** {sys.version.split()[0]}  
        **Streamlit:** {st.__version__}  
        **Environment:** Production
        """)
