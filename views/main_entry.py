import streamlit as st
import json
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path("data")
RECORDS_FILE = DATA_DIR / "cycle_time_records.json"

def load_records():
    """Load cycle time records from JSON"""
    if not RECORDS_FILE.exists():
        return []
    try:
        with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_records(records):
    """Save cycle time records to JSON"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

def show():
    """Display data entry page"""
    st.title("📝 Cycle Time Data Entry")
    st.markdown("---")
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Enter New Cycle Time Record")
        
        # Main entry form
        with st.form("cycle_time_entry", clear_on_submit=True):
            # Row 1: Basic Information
            col_a, col_b = st.columns(2)
            
            with col_a:
                part_number = st.text_input(
                    "Part Number *",
                    placeholder="e.g., PN-12345",
                    help="Enter the part number being produced"
                )
                
                operator_name = st.text_input(
                    "Operator Name *",
                    placeholder="e.g., John Doe",
                    help="Name of the operator"
                )
                
                machine_id = st.text_input(
                    "Machine ID *",
                    placeholder="e.g., M-001",
                    help="Machine identification number"
                )
            
            with col_b:
                work_date = st.date_input(
                    "Date *",
                    value=date.today(),
                    help="Production date"
                )
                
                shift = st.selectbox(
                    "Shift *",
                    ["Morning", "Afternoon", "Night"],
                    help="Work shift"
                )
                
                station = st.text_input(
                    "Station/Line",
                    placeholder="e.g., Line A",
                    help="Production station or line (optional)"
                )
            
            st.markdown("---")
            
            # Row 2: Cycle Time Data
            col_c, col_d, col_e = st.columns(3)
            
            with col_c:
                cycle_time = st.number_input(
                    "Cycle Time (seconds) *",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    format="%.2f",
                    help="Time to complete one cycle"
                )
            
            with col_d:
                quantity = st.number_input(
                    "Quantity Produced *",
                    min_value=1,
                    value=1,
                    step=1,
                    help="Number of units produced"
                )
            
            with col_e:
                quality_status = st.selectbox(
                    "Quality Status *",
                    ["Good", "Rework", "Scrap"],
                    help="Quality outcome"
                )
            
            # Row 3: Additional Information
            st.markdown("**Additional Information**")
            
            col_f, col_g = st.columns(2)
            
            with col_f:
                downtime = st.number_input(
                    "Downtime (minutes)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    help="Machine downtime during this period"
                )
            
            with col_g:
                defect_count = st.number_input(
                    "Defect Count",
                    min_value=0,
                    value=0,
                    step=1,
                    help="Number of defective units"
                )
            
            notes = st.text_area(
                "Notes",
                placeholder="Any additional notes or observations...",
                help="Optional notes about this record"
            )
            
            # Submit button
            st.markdown("---")
            submitted = st.form_submit_button(
                "💾 Save Record",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                # Validate required fields
                if not part_number or not operator_name or not machine_id:
                    st.error("❌ Please fill in all required fields marked with *")
                elif cycle_time <= 0:
                    st.error("❌ Cycle time must be greater than 0")
                else:
                    # Create new record
                    new_record = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                        "timestamp": datetime.now().isoformat(),
                        "date": work_date.isoformat(),
                        "part_number": part_number,
                        "operator_name": operator_name,
                        "machine_id": machine_id,
                        "shift": shift,
                        "station": station,
                        "cycle_time": cycle_time,
                        "quantity": quantity,
                        "quality_status": quality_status,
                        "downtime": downtime,
                        "defect_count": defect_count,
                        "notes": notes,
                        "entered_by": st.session_state.username,
                        "entry_timestamp": datetime.now().isoformat()
                    }
                    
                    # Load existing records and append
                    records = load_records()
                    records.append(new_record)
                    save_records(records)
                    
                    st.success("✅ Record saved successfully!")
                    st.balloons()
                    
                    # Show summary
                    with st.expander("📋 Record Summary", expanded=True):
                        st.json(new_record)
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        # Load records for stats
        records = load_records()
        
        if records:
            # Today's records
            today = date.today().isoformat()
            today_records = [r for r in records if r.get('date') == today]
            
            st.metric(
                "Today's Entries",
                len(today_records),
                delta=f"+{len(today_records)} today"
            )
            
            # Total records
            st.metric(
                "Total Records",
                len(records)
            )
            
            # Average cycle time today
            if today_records:
                avg_cycle = sum(r.get('cycle_time', 0) for r in today_records) / len(today_records)
                st.metric(
                    "Avg Cycle Time (Today)",
                    f"{avg_cycle:.2f}s"
                )
            
            # Recent entries
            st.markdown("---")
            st.markdown("**Recent Entries:**")
            
            recent = records[-5:][::-1]  # Last 5, reversed
            for r in recent:
                with st.container():
                    st.caption(f"🕐 {r.get('timestamp', '')[:19]}")
                    st.text(f"Part: {r.get('part_number', 'N/A')}")
                    st.text(f"Time: {r.get('cycle_time', 0)}s")
                    st.markdown("---")
        else:
            st.info("No records yet. Start entering data!")
        
        # Help section
        st.markdown("---")
        st.markdown("**💡 Tips:**")
        st.caption("• All fields marked with * are required")
        st.caption("• Cycle time should be in seconds")
        st.caption("• Use notes for special observations")
        st.caption("• Data is saved immediately")
