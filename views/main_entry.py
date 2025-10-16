import streamlit as st

def show():
    """Display data entry page"""
    st.title("📝 Data Entry")
    st.markdown("---")
    
    st.info("👷‍♂️ This page is under construction. Your existing data entry code should go here.")
    
    # Placeholder form
    with st.form("cycle_time_entry"):
        col1, col2 = st.columns(2)
        
        with col1:
            part_number = st.text_input("Part Number")
            operator = st.text_input("Operator Name")
            machine = st.text_input("Machine ID")
        
        with col2:
            cycle_time = st.number_input("Cycle Time (seconds)", min_value=0.0, step=0.1)
            quantity = st.number_input("Quantity", min_value=1, step=1)
            date = st.date_input("Date")
        
        notes = st.text_area("Notes (Optional)")
        
        submitted = st.form_submit_button("Submit Entry", use_container_width=True)
        
        if submitted:
            st.success("✅ Entry recorded successfully!")
            st.balloons()
