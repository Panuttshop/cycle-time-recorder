"""
Export and Reports Page
"""
import streamlit as st
import pandas as pd
import json
from datetime import date
from utils.file_manager import load_records


def show():
    """Display export and reports page"""
    st.title("📤 Export & Reports")
    
    records = load_records()
    if not records:
        st.info("ยังไม่มีข้อมูล")
        return
    
    df = pd.DataFrame([r.to_dict() for r in records])
    
    st.markdown("## 💾 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### CSV Export")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Export as CSV",
            csv,
            f"cycle_records_{date.today()}.csv",
            "text/csv",
            key="csv_export"
        )
    
    with col2:
        st.markdown("### Excel Export")
        if st.button("📊 Export as Excel"):
            try:
                excel_file = f"cycle_records_{date.today()}.xlsx"
                df.to_excel(excel_file, index=False, engine='openpyxl')
                with open(excel_file, 'rb') as f:
                    st.download_button(
                        "📥 Download Excel",
                        f.read(),
                        excel_file,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="excel_export"
                    )
            except Exception as e:
                st.error(f"Error exporting to Excel: {e}")
    
    with col3:
        st.markdown("### JSON Export")
        json_data = json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=2)
        st.download_button(
            "🔗 Export as JSON",
            json_data,
            f"cycle_records_{date.today()}.json",
            "application/json",
            key="json_export"
        )
    
    st.markdown("---")
    st.markdown("## 📋 Generate Reports")
    
    report_type = st.selectbox("Report Type:", [
        "Daily Summary",
        "Model Performance",
        "Station Performance",
        "User Activity"
    ])
    
    if report_type == "Daily Summary":
        selected_date = st.date_input("Select Date:")
        date_str = selected_date.strftime("%Y-%m-%d")
        date_records = df[df['date'] == date_str]
        
        if date_records.empty:
            st.info(f"ไม่มีข้อมูลในวันที่ {date_str}")
        else:
            st.markdown(f"### Daily Report - {date_str}")
            st.write(f"**Total Records:** {len(date_records)}")
            st.write(f"**Models:** {date_records['model'].nunique()}")
            st.write(f"**Stations:** {date_records['station'].nunique()}")
            st.dataframe(date_records)
    
    elif report_type == "Model Performance":
        selected_model = st.selectbox("Select Model:", sorted(df['model'].unique()))
        model_records = df[df['model'] == selected_model]
        
        st.markdown(f"### Model Performance Report - {selected_model}")
        st.write(f"**Total Records:** {len(model_records)}")
        st.write(f"**Stations:** {model_records['station'].nunique()}")
        st.write(f"**Date Range:** {model_records['date'].min()} to {model_records['date'].max()}")
        
        st.subheader("Station Breakdown")
        st.dataframe(model_records.groupby('station').size().reset_index(name='Count'))
    
    elif report_type == "Station Performance":
        selected_station = st.selectbox("Select Station:", sorted(df['station'].unique()))
        station_records = df[df['station'] == selected_station]
        
        st.markdown(f"### Station Performance Report - {selected_station}")
        st.write(f"**Total Records:** {len(station_records)}")
        st.write(f"**Models:** {station_records['model'].nunique()}")
        st.dataframe(station_records)
    
    elif report_type == "User Activity":
        st.markdown("### User Activity Report")
        user_activity = df.groupby('created_by').size().reset_index(name='Records')
        st.dataframe(user_activity)
        st.bar_chart(user_activity.set_index('created_by'))