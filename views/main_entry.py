"""
Main Data Entry Page
"""
import streamlit as st
import time
from datetime import date, datetime
from config.settings import MAX_ROWS
from models.cycle_time import CycleTime
from models.cycle_record import CycleRecord
from utils.validation import validate_cycle_input
from utils.file_manager import load_records, save_records, add_audit_log


def show():
    """Display main data entry page"""
    st.title("📊 Cycle Time Recorder")
    
    # Initialize record_date if not exists
    if "record_date" not in st.session_state or st.session_state.record_date is None:
        st.session_state.record_date = date.today()
    
    st.markdown("## ⚙️ ข้อมูลทั่วไป")
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.model = st.text_input("Model *", value=st.session_state.get("model", ""), 
                                                help="กรุณากรอก Model ก่อนบันทึกข้อมูล")
        if not st.session_state.model:
            st.warning("⚠️ กรุณากรอก Model ก่อนเพื่อเปิดใช้งานการบันทึกข้อมูล")
    with col2:
        st.session_state.record_date = st.date_input("วันที่บันทึก", value=st.session_state.record_date)
    
    st.markdown("---")
    st.markdown("## 🧍 Station Data Entry")
    
    # Disable station input if Model is not filled
    model_filled = bool(st.session_state.model and st.session_state.model.strip())
    
    if not model_filled:
        st.info("ℹ️ กรุณากรอก Model ด้านบนเพื่อเริ่มบันทึกข้อมูล Station")
    
    num_rows = st.slider("จำนวน Station", 1, MAX_ROWS, 5, disabled=not model_filled)
    
    inputs = []
    validation_errors = []
    
    for i in range(num_rows):
        cols = st.columns([1, 2, 2, 2, 2])  # Added column for output
        
        with cols[0]:
            station = st.text_input(f"Station {i+1}", key=f"st_{i}", disabled=not model_filled)
        
        with cols[1]:
            r1 = st.text_input("รอบ1", key=f"r1_{i}", placeholder="5(12)4", disabled=not model_filled)
            valid, msg = validate_cycle_input(r1)
            if not valid:
                validation_errors.append(f"Station {i+1} รอบ1: {msg}")
        
        with cols[2]:
            r2 = st.text_input("รอบ2", key=f"r2_{i}", placeholder="5(12)4", disabled=not model_filled)
            valid, msg = validate_cycle_input(r2)
            if not valid:
                validation_errors.append(f"Station {i+1} รอบ2: {msg}")
        
        with cols[3]:
            r3 = st.text_input("รอบ3", key=f"r3_{i}", placeholder="5(12)4", disabled=not model_filled)
            valid, msg = validate_cycle_input(r3)
            if not valid:
                validation_errors.append(f"Station {i+1} รอบ3: {msg}")
        
        with cols[4]:
            output = st.text_input("Output", key=f"output_{i}", placeholder="100", disabled=not model_filled,
                                   help="จำนวนชิ้นงานที่ผลิตได้")
        
        r1_val = st.session_state.get(f"r1_{i}", "")
        r2_val = st.session_state.get(f"r2_{i}", "")
        r3_val = st.session_state.get(f"r3_{i}", "")
        output_val = st.session_state.get(f"output_{i}", "")
        inputs.append((station, r1_val, r2_val, r3_val, output_val))
    
    if validation_errors:
        st.error("**พบข้อผิดพลาด:**")
        for err in validation_errors:
            st.text(f"• {err}")
    
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    
    with col1:
        save_btn = st.button("💾 บันทึก", disabled=bool(validation_errors) or not model_filled)
    with col2:
        if not model_filled:
            st.error("❌ กรุณากรอก Model ก่อน")
        elif validation_errors:
            st.warning("⚠️ กรุณาแก้ไขข้อผิดพลาดก่อน")
    
    if save_btn:
        if not st.session_state.model:
            st.error("❌ กรุณากรอก Model")
            return
        
        with st.spinner("กำลังบันทึก..."):
            records = load_records()
            now = datetime.now().isoformat()
            count = 0
            
            for station, r1_str, r2_str, r3_str, output_str in inputs:
                if station and (r1_str or r2_str or r3_str):
                    rec = CycleRecord(
                        st.session_state.record_date.isoformat(),
                        st.session_state.model,
                        station,
                        CycleTime.parse(r1_str),
                        CycleTime.parse(r2_str),
                        CycleTime.parse(r3_str),
                        st.session_state.username,
                        now
                    )
                    # Add output to record
                    if output_str and output_str.strip():
                        rec.output = output_str.strip()
                    else:
                        rec.output = ""
                    
                    records.append(rec)
                    count += 1
            
            if count == 0:
                st.info("ℹ️ ไม่มีข้อมูลที่จะบันทึก")
            else:
                if save_records(records):
                    add_audit_log("CREATE_RECORDS", st.session_state.username, f"Added {count} records")
                    st.success(f"✅ บันทึก {count} Station เรียบร้อย")
                    time.sleep(1)
                    st.experimental_rerun()