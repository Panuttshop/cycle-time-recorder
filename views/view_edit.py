"""
View and Edit Records Page
"""
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from models.cycle_time import CycleTime
from utils.validation import validate_cycle_input
from utils.file_manager import load_records, save_records, add_audit_log


def show():
    """Display view and edit records page"""
    st.title("📋 View/Edit Records")
    
    records = load_records()
    if not records:
        st.info("ยังไม่มีข้อมูล")
        return
    
    # Filters
    st.markdown("### 🔍 ตัวกรอง")
    col1, col2, col3 = st.columns(3)
    
    dates = sorted(set(r.date for r in records), reverse=True)
    models = sorted(set(r.model for r in records))
    
    with col1:
        date_filter = st.selectbox("วันที่", ["ทั้งหมด"] + dates)
    with col2:
        model_filter = st.selectbox("Model", ["ทั้งหมด"] + models)
    with col3:
        station_filter = st.text_input("ค้นหา Station")
    
    # Apply filters
    filtered = records
    if date_filter != "ทั้งหมด":
        filtered = [r for r in filtered if r.date == date_filter]
    if model_filter != "ทั้งหมด":
        filtered = [r for r in filtered if r.model == model_filter]
    if station_filter:
        filtered = [r for r in filtered if station_filter.lower() in r.station.lower()]
    
    st.write(f"**แสดง {len(filtered)} จาก {len(records)} รายการ**")
    
    # Display table
    df = pd.DataFrame([r.to_dict() for r in filtered])
    st.dataframe(df)
    
    # Download
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("⬇️ ดาวน์โหลด CSV", csv, "cycle_records.csv", "text/csv")
    
    st.markdown("---")
    
    # Edit/Delete
    st.markdown("### ✏️ แก้ไข/ลบ")
    
    if not filtered:
        st.info("ไม่มีข้อมูลให้แก้ไข")
        return
    
    options = [f"{i}: {r.date} - {r.model} - Station {r.station}" 
               for i, r in enumerate(filtered)]
    selected = st.selectbox("เลือก:", options)
    
    if selected:
        idx = int(selected.split(":")[0])
        rec = filtered[idx]
        rec_idx = records.index(rec)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 แก้ไข")
            with st.form("edit_form"):
                new_date = st.date_input("วันที่", value=pd.to_datetime(rec.date).date())
                new_model = st.text_input("Model", value=rec.model)
                new_station = st.text_input("Station", value=rec.station)
                new_r1 = st.text_input("รอบ1", value=str(rec.r1) if rec.r1 else "")
                new_r2 = st.text_input("รอบ2", value=str(rec.r2) if rec.r2 else "")
                new_r3 = st.text_input("รอบ3", value=str(rec.r3) if rec.r3 else "")
                new_output = st.text_input("Output", value=getattr(rec, 'output', ''))
                
                if st.form_submit_button("💾 บันทึก"):
                    # Validate
                    errors = []
                    for val, label in [(new_r1, "รอบ1"), (new_r2, "รอบ2"), (new_r3, "รอบ3")]:
                        v, m = validate_cycle_input(val)
                        if not v:
                            errors.append(f"{label}: {m}")
                    
                    if errors:
                        st.error("ข้อมูลไม่ถูกต้อง:\n" + "\n".join(errors))
                    else:
                        records[rec_idx].date = new_date.isoformat()
                        records[rec_idx].model = new_model
                        records[rec_idx].station = new_station
                        records[rec_idx].r1 = CycleTime.parse(new_r1)
                        records[rec_idx].r2 = CycleTime.parse(new_r2)
                        records[rec_idx].r3 = CycleTime.parse(new_r3)
                        records[rec_idx].output = new_output
                        records[rec_idx].modified_by = st.session_state.username
                        records[rec_idx].modified_at = datetime.now().isoformat()
                        
                        if save_records(records):
                            add_audit_log("EDIT_RECORD", st.session_state.username, f"Edited: {rec.model} - {rec.station}")
                            st.success("✅ แก้ไขเรียบร้อย")
                            time.sleep(1)
                            st.experimental_rerun()
        
        with col2:
            st.subheader("🗑️ ลบ")
            st.warning("⚠️ การลบไม่สามารถย้อนกลับได้")
            st.text(f"วันที่: {rec.date}\nModel: {rec.model}\nStation: {rec.station}")
            
            if st.button("🗑️ ลบรายการนี้"):
                records.pop(rec_idx)
                if save_records(records):
                    add_audit_log("DELETE_RECORD", st.session_state.username, f"Deleted: {rec.model} - {rec.station}")
                    st.success("✅ ลบเรียบร้อย")
                    time.sleep(1)
                    st.experimental_rerun()