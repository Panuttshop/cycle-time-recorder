"""
Analytics Dashboard Page
"""
import streamlit as st
import pandas as pd
from models.cycle_time import CycleTime
from utils.file_manager import load_records


def show():
    """Display analytics dashboard"""
    st.title("📈 Analytics Dashboard")
    
    records = load_records()
    if not records:
        st.info("ยังไม่มีข้อมูลสำหรับวิเคราะห์")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([r.to_dict() for r in records])
    df['date'] = pd.to_datetime(df['date'])
    
    # Key Metrics
    st.markdown("## 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Total Records", len(records))
    with col2:
        st.metric("🏭 Unique Models", df['model'].nunique())
    with col3:
        st.metric("🎯 Unique Stations", df['station'].nunique())
    with col4:
        st.metric("👥 Contributors", df['created_by'].nunique())
    
    st.markdown("---")
    
    # Time Series
    st.markdown("## 📅 Records Over Time")
    daily_counts = df.groupby('date').size()
    st.line_chart(daily_counts)
    
    st.markdown("---")
    
    # Model Performance
    st.markdown("## 🏭 Model Performance")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Records per Model")
        model_counts = df['model'].value_counts()
        st.bar_chart(model_counts)
    
    with col2:
        st.subheader("Records per Station")
        station_counts = df['station'].value_counts().head(10)
        st.bar_chart(station_counts)
    
    st.markdown("---")
    
    # Average Cycle Times
    st.markdown("## ⏱️ Average Cycle Times by Model")
    
    model_list = sorted(df['model'].unique())
    selected_model = st.selectbox("Select Model:", model_list)
    
    model_df = df[df['model'] == selected_model]
    
    if not model_df.empty:
        # Extract average values
        averages = []
        for idx, row in model_df.iterrows():
            if row['average']:
                try:
                    ct = CycleTime.parse(row['average'])
                    if ct:
                        averages.append({
                            'date': row['date'].strftime('%Y-%m-%d'),
                            'station': row['station'],
                            'pre': ct.pre,
                            'machine': ct.machine,
                            'post': ct.post,
                            'total': ct.pre + ct.machine + ct.post
                        })
                except:
                    pass
        
        if averages:
            avg_df = pd.DataFrame(averages)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Pre Time", f"{avg_df['pre'].mean():.1f}s")
            with col2:
                st.metric("Avg Machine Time", f"{avg_df['machine'].mean():.1f}s")
            with col3:
                st.metric("Avg Post Time", f"{avg_df['post'].mean():.1f}s")
            
            st.markdown("**Trend Chart**")
            st.line_chart(avg_df[['pre', 'machine', 'post']].describe().loc[['mean', '50%', 'max']])
        else:
            st.info("ไม่มีข้อมูล average ที่สมบูรณ์")
    else:
        st.info(f"ไม่มีข้อมูลสำหรับ Model: {selected_model}")