import streamlit as st
from datetime import datetime

# Import from authentication module
try:
    from auth.authentication import change_password, SESSION_TIMEOUT_MINUTES, validate_password_strength
except ImportError:
    from authentication import change_password, SESSION_TIMEOUT_MINUTES, validate_password_strength

def show():
    """Display settings page"""
    st.title("⚙️ Settings")
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔐 Change Password", "👤 Profile", "ℹ️ About"])
    
    with tab1:
        show_change_password()
    
    with tab2:
        show_profile_info()
    
    with tab3:
        show_about_info()

def show_change_password():
    """Show change password form"""
    st.header("Change Password")
    st.markdown("Update your account password")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("change_password_form"):
            current_password = st.text_input(
                "Current Password",
                type="password",
                help="Enter your current password"
            )
            
            new_password = st.text_input(
                "New Password",
                type="password",
                help="Enter your new password (minimum 6 characters)"
            )
            
            confirm_password = st.text_input(
                "Confirm New Password",
                type="password",
                help="Re-enter your new password"
            )
            
            submit = st.form_submit_button("Change Password", use_container_width=True)
            
            if submit:
                # Validate inputs
                if not current_password or not new_password or not confirm_password:
                    st.error("❌ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ New passwords do not match")
                else:
                    # Validate password strength
                    is_valid, message = validate_password_strength(new_password)
                    
                    if not is_valid:
                        st.error(f"❌ {message}")
                    else:
                        # Attempt to change password
                        success, result_message = change_password(
                            st.session_state.username,
                            current_password,
                            new_password
                        )
                        
                        if success:
                            st.success(f"✅ {result_message}")
                            st.info("Please login again with your new password on next session.")
                        else:
                            st.error(f"❌ {result_message}")
    
    with col2:
        st.info("""
        **Password Requirements:**
        - Minimum 6 characters
        - At least one letter
        - Mix of letters and numbers recommended
        """)

def show_profile_info():
    """Show user profile information"""
    st.header("Profile Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Account Details")
        st.markdown(f"**Username:** `{st.session_state.username}`")
        st.markdown(f"**Role:** `{st.session_state.role.upper()}`")
        
        if st.session_state.login_time:
            login_time = datetime.fromisoformat(st.session_state.login_time)
            st.markdown(f"**Login Time:** {login_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        st.markdown("### Session Information")
        st.markdown(f"**Session Timeout:** {SESSION_TIMEOUT_MINUTES} minutes")
        
        if st.session_state.last_activity:
            last_activity = datetime.fromisoformat(st.session_state.last_activity)
            st.markdown(f"**Last Activity:** {last_activity.strftime('%H:%M:%S')}")
            
            time_elapsed = (datetime.now() - last_activity).seconds // 60
            time_remaining = SESSION_TIMEOUT_MINUTES - time_elapsed
            
            if time_remaining > 0:
                st.markdown(f"**Time Until Logout:** {time_remaining} minutes")
                
                # Progress bar for session timeout
                progress = time_elapsed / SESSION_TIMEOUT_MINUTES
                st.progress(progress)
            else:
                st.warning("Session expired - you will be logged out shortly")

def show_about_info():
    """Show about information"""
    st.header("About Cycle Time Recorder")
    
    st.markdown("""
    ### 📊 Cycle Time Recorder v1.0
    
    A comprehensive application for recording and analyzing manufacturing cycle times.
    
    **Features:**
    - ✅ Real-time data entry
    - ✅ Historical record viewing and editing
    - ✅ Advanced analytics dashboard
    - ✅ Export to multiple formats
    - ✅ User authentication and role management
    - ✅ Automatic session management (30-minute timeout)
    - ✅ Audit logging
    
    **Session Management:**
    - Sessions automatically expire after 30 minutes of inactivity
    - Your session persists across page refreshes
    - Activity is tracked on each page interaction
    
    **Security Features:**
    - Encrypted password storage
    - Session timeout protection
    - Audit trail for all user actions
    - Role-based access control
    
    ---
    
    **Technical Information:**
    - Built with Streamlit
    - Python-based backend
    - JSON data storage
    - SHA-256 password hashing
    
    ---
    
    © 2024 Cycle Time Recorder | All rights reserved
    """)
    
    # System info
    with st.expander("📋 System Information"):
        st.markdown(f"""
        **Current User:** {st.session_state.username}  
        **Role:** {st.session_state.role}  
        **Session Timeout:** {SESSION_TIMEOUT_MINUTES} minutes  
        **Login Status:** {"✅ Active" if st.session_state.logged_in else "❌ Not logged in"}
        """)
