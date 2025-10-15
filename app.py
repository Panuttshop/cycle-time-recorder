"""
Cycle Time Recorder - Main Entry Point
"""
import streamlit as st
from config.settings import PAGE_CONFIG
from auth.authentication import show_login_ui
from views import main_entry, view_edit, analytics, export, admin, settings
from utils.file_manager import ensure_files

st.set_page_config(**PAGE_CONFIG)


def init_session_state():
    """Initialize session variables"""
    defaults = {
        "logged_in": False,
        "username": None,
        "role": "",
        "login_attempts": {},
        "model": "",
        "record_date": st.session_state.get("record_date", None)
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main():
    """Main application entry point"""
    init_session_state()
    ensure_files()
    
    logged_in = show_login_ui()
    
    if not logged_in:
        st.title("📊 Cycle Time Recorder")
        st.markdown("""
        ### 🔐 Login Required
        กรุณาล็อกอินจาก sidebar
        
        #### ✨ Features
        - 🔐 Secure login with audit trail
        - 📊 บันทึก Cycle Time หลาย Station
        - ✏️ แก้ไขและลบข้อมูล
        - 🔍 ค้นหากรองข้อมูล
        - 📈 Analytics & reporting
        - 👥 User management (Admin)
        - 📋 Audit trail logging
        - 💾 Data backup & export
        - ⚙️ System settings
        
        **Demo Credentials:**
        - Username: `admin`
        - Password: `admin123`
        """)
        return
    
    st.sidebar.markdown("---")
    
    menu_items = ["📊 Entry", "📋 View/Edit", "📈 Analytics", "📤 Export"]
    if st.session_state.role == "Admin":
        menu_items.extend(["🔒 Admin", "⚙️ Settings"])
    
    st.sidebar.write("**Navigation:**")
    choice = st.sidebar.radio("", menu_items)
    
    if choice == "📊 Entry":
        main_entry.show()
    elif choice == "📋 View/Edit":
        view_edit.show()
    elif choice == "📈 Analytics":
        analytics.show()
    elif choice == "📤 Export":
        export.show()
    elif choice == "🔒 Admin":
        admin.show()
    elif choice == "⚙️ Settings":
        settings.show()


if __name__ == "__main__":
    main()