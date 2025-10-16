import streamlit as st
from pathlib import Path
from auth.authentication import (
    show_login_ui, 
    show_user_info, 
    init_session_state,
    check_session_timeout
)

# Page configuration
st.set_page_config(
    page_title="Cycle Time Recorder",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def load_page(page_module, page_name):
    """Load a page module safely"""
    try:
        return page_module.show()
    except Exception as e:
        st.error(f"Error loading {page_name}: {str(e)}")
        st.exception(e)

def main():
    # Initialize session state
    init_session_state()
    
    # Check if user is logged in
    logged_in = show_login_ui()
    
    if not logged_in:
        return
    
    # Show user info in sidebar
    show_user_info()
    
    # Sidebar navigation
    st.sidebar.title("⏱️ Cycle Time Recorder")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.radio(
        "Navigation",
        [
            "📝 Data Entry",
            "👁️ View & Edit Records",
            "📊 Analytics Dashboard",
            "📤 Export & Reports",
            "⚙️ Settings",
            "👨‍💼 Admin Panel"
        ],
        key="navigation"
    )
    
    st.sidebar.markdown("---")
    
    # Load the selected page
    if page == "📝 Data Entry":
        from pages import main_entry
        load_page(main_entry, "Data Entry")
        
    elif page == "👁️ View & Edit Records":
        from pages import view_edit
        load_page(view_edit, "View & Edit Records")
        
    elif page == "📊 Analytics Dashboard":
        from pages import analytics
        load_page(analytics, "Analytics Dashboard")
        
    elif page == "📤 Export & Reports":
        from pages import export
        load_page(export, "Export & Reports")
        
    elif page == "⚙️ Settings":
        from pages import settings
        load_page(settings, "Settings")
        
    elif page == "👨‍💼 Admin Panel":
        from pages import admin
        if st.session_state.role == "admin":
            load_page(admin, "Admin Panel")
        else:
            st.error("❌ Access denied. Admin privileges required.")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2024 Cycle Time Recorder v1.0")

if __name__ == "__main__":
    main()
