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

def show_placeholder_page(page_name):
    """Show placeholder for pages that don't exist yet"""
    st.title(f"{page_name}")
    st.markdown("---")
    st.info(f"👷‍♂️ This page is under construction. Your existing {page_name} code should go here.")
    st.markdown("""
    ### How to add your page:
    
    1. Create a file in `views/` folder with your page code
    2. Add a `show()` function that contains your page logic
    3. The app will automatically load it
    
    **Example structure:**
    ```python
    import streamlit as st
    
    def show():
        st.title("Your Page Title")
        # Your code here
    ```
    """)

def main():
    # Initialize session state
    init_session_state()
    
    # Check if user is logged in
    logged_in = show_login_ui()
    
    if not logged_in:
        return
    
    # Show user info in sidebar
    show_user_info()
    
    # Debug info (TEMPORARY - Remove after fixing admin access)
    st.sidebar.markdown("---")
    st.sidebar.write("**🔍 DEBUG INFO:**")
    st.sidebar.write(f"Username: {st.session_state.get('username', 'NOT SET')}")
    st.sidebar.write(f"Role: {st.session_state.get('role', 'NOT SET')}")
    st.sidebar.write(f"Logged in: {st.session_state.get('logged_in', False)}")
    st.sidebar.markdown("---")
    
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
    
    # Load the selected page with error handling
    try:
        if page == "📝 Data Entry":
            try:
                from views import main_entry
                load_page(main_entry, "Data Entry")
            except (ImportError, ModuleNotFoundError) as e:
                st.error(f"Cannot load Data Entry: {str(e)}")
                show_placeholder_page("📝 Data Entry")
            
        elif page == "👁️ View & Edit Records":
            try:
                from views import view_edit
                load_page(view_edit, "View & Edit Records")
            except (ImportError, ModuleNotFoundError):
                show_placeholder_page("👁️ View & Edit Records")
            
        elif page == "📊 Analytics Dashboard":
            try:
                from views import analytics
                load_page(analytics, "Analytics Dashboard")
            except (ImportError, ModuleNotFoundError):
                show_placeholder_page("📊 Analytics Dashboard")
            
        elif page == "📤 Export & Reports":
            try:
                from views import export
                load_page(export, "Export & Reports")
            except (ImportError, ModuleNotFoundError):
                show_placeholder_page("📤 Export & Reports")
            
        elif page == "⚙️ Settings":
            try:
                from views import settings
                load_page(settings, "Settings")
            except (ImportError, ModuleNotFoundError):
                show_placeholder_page("⚙️ Settings")
            
        elif page == "👨‍💼 Admin Panel":
            # Check admin access with better error handling
            user_role = st.session_state.get('role', '').lower() if st.session_state.get('role') else ''
            
            st.write(f"**Checking admin access...**")
            st.write(f"Your role: '{st.session_state.get('role', 'NOT SET')}'")
            st.write(f"Normalized role: '{user_role}'")
            
            if user_role == "admin":
                try:
                    from views import admin
                    load_page(admin, "Admin Panel")
                except (ImportError, ModuleNotFoundError) as e:
                    st.error(f"Cannot load Admin Panel: {str(e)}")
                    show_placeholder_page("👨‍💼 Admin Panel")
            else:
                st.error("❌ Access denied. Admin privileges required.")
                st.info(f"**Current role:** '{st.session_state.get('role', 'NOT SET')}'")
                st.info("**To fix this:**")
                st.markdown("""
                1. Go to your `data/users.json` file
                2. Find your username
                3. Change `"role": "user"` to `"role": "admin"`
                4. Save and commit
                5. Logout and login again
                
                **OR**
                
                1. Delete `data/users.json` file
                2. Login with: **admin** / **admin123**
                """)
                
    except Exception as e:
        st.error(f"❌ Error loading page: {str(e)}")
        st.info("💡 Make sure all required page files exist in the `views/` folder")
        st.exception(e)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2024 Cycle Time Recorder v1.0")

if __name__ == "__main__":
    main()
