"""
Analytics Dashboard Page - UPH Chart Only
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from models.cycle_time import CycleTime
from utils.file_manager import load_records


def show():
    """Display UPH analytics"""
    st.title("📊 UPH Analytics")
    st.info("**Formula:** UPH = 3600 / (Pre + Machine + Post) × Output")
    
    records = load_records()
    if not records:
        st.info("ยังไม่มีข้อมูล")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([r.to_dict() for r in records])
    df['date'] = pd.to_datetime(df['date'])
    
    # Date Range Filter
    st.markdown("### 📅 Select Date Range")
    col1, col2 = st.columns(2)
    
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    with col1:
        start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
    
    # Filter by date range
    df_filtered = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
    
    if df_filtered.empty:
        st.warning("⚠️ ไม่มีข้อมูลในช่วงวันที่ที่เลือก")
        return
    
    st.markdown("---")
    
    # Select Model
    models = sorted(df_filtered['model'].unique())
    selected_model = st.selectbox("📦 Select Model:", models)
    
    # Filter by model
    model_data = df_filtered[df_filtered['model'] == selected_model]
    
    if model_data.empty:
        st.warning("ไม่มีข้อมูล")
        return
    
    # Parse cycle times from average column
    stations = []
    for _, row in model_data.iterrows():
        avg_str = row.get('average', '')
        if avg_str:
            ct = CycleTime.parse(avg_str)
            if ct:
                stations.append({
                    'station': row['station'],
                    'pre': ct.pre,
                    'machine': ct.machine,
                    'post': ct.post,
                    'saved_output': row.get('output', '1')
                })
    
    if not stations:
        st.warning("ไม่มีข้อมูล Cycle Time")
        return
    
    st_df = pd.DataFrame(stations)
    
    # Average by station
    avg_df = st_df.groupby('station').agg({
        'pre': 'mean',
        'machine': 'mean',
        'post': 'mean'
    }).reset_index()
    
    # UPH Target Input
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        uph_target = st.number_input(
            "🎯 UPH Target",
            min_value=0,
            value=100,
            step=10,
            help="เป้าหมาย UPH (จะแสดงเส้นสีแดงในกราฟ)"
        )
    with col2:
        st.write("")
        st.write("")
        if uph_target > 0:
            st.success(f"Target UPH set to: **{uph_target}** units/hour")
    
    # Get default outputs
    st.markdown("---")
    st.markdown("### 🔢 Output per Station")
    
    outputs = {}
    num_cols = min(4, len(avg_df))
    cols = st.columns(num_cols)
    
    for i, row in avg_df.iterrows():
        station = row['station']
        
        # Get saved output
        saved = st_df[st_df['station'] == station]['saved_output'].iloc[0]
        try:
            default_output = int(float(str(saved).strip())) if saved and str(saved).strip() else 1
        except:
            default_output = 1
        
        col_idx = i % num_cols
        with cols[col_idx]:
            outputs[station] = st.number_input(
                station,
                min_value=1,
                value=default_output,
                step=1,
                key=f"output_{station}"
            )
    
    # Calculate UPH
    avg_df['output'] = avg_df['station'].map(outputs)
    avg_df['total_seconds'] = avg_df['pre'] + avg_df['machine'] + avg_df['post']
    
    # UPH = 3600 / (pre + machine + post) * output
    avg_df['UPH'] = avg_df.apply(
        lambda x: (3600.0 / x['total_seconds'] * x['output']) if x['total_seconds'] > 0 else 0,
        axis=1
    )
    
    # Show results
    st.markdown("---")
    st.markdown("### 📋 Results")
    
    result_df = avg_df[['station', 'pre', 'machine', 'post', 'output', 'UPH']].copy()
    result_df.columns = ['Station', 'Pre(s)', 'Machine(s)', 'Post(s)', 'Output', 'UPH']
    
    st.dataframe(result_df.style.format({
        'Pre(s)': '{:.1f}',
        'Machine(s)': '{:.1f}',
        'Post(s)': '{:.1f}',
        'UPH': '{:.1f}'
    }))
    
    # THE MAIN UPH CHART WITH TARGET LINE (using native Streamlit)
    st.markdown("---")
    st.markdown("### 📊 UPH Chart")
    
    # Sort by station name for consistent display
    chart_data = result_df.sort_values('Station').set_index('Station')
    
    # Create combined dataframe with UPH and Target line
    chart_combined = pd.DataFrame({
        'UPH': chart_data['UPH']
    })
    
    if uph_target > 0:
        chart_combined['Target'] = uph_target
    
    # Display chart
    st.bar_chart(chart_combined)
    
    # Add visual indicator for target line
    if uph_target > 0:
        st.markdown(f"🔴 **Red line indicates target: {uph_target} UPH**")
    
    # Stats with Target Comparison
    st.markdown("---")
    st.markdown("### 📈 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    avg_uph = result_df['UPH'].mean()
    max_uph = result_df['UPH'].max()
    min_uph = result_df['UPH'].min()
    
    with col1:
        st.metric("Avg UPH", f"{avg_uph:.1f}")
    with col2:
        st.metric("Max UPH", f"{max_uph:.1f}")
    with col3:
        st.metric("Min UPH", f"{min_uph:.1f}")
    with col4:
        if uph_target > 0:
            diff = avg_uph - uph_target
            st.metric("vs Target", f"{diff:+.1f}", delta=f"{diff:+.1f}")
        else:
            st.metric("Target", "Not Set")
    
    # Stations above/below target
    if uph_target > 0:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        above_target = result_df[result_df['UPH'] >= uph_target]
        below_target = result_df[result_df['UPH'] < uph_target]
        
        with col1:
            st.markdown("#### ✅ Above Target")
            if not above_target.empty:
                for _, row in above_target.iterrows():
                    st.success(f"**{row['Station']}**: {row['UPH']:.1f} UPH")
            else:
                st.info("No stations above target")
        
        with col2:
            st.markdown("#### ⚠️ Below Target")
            if not below_target.empty:
                for _, row in below_target.iterrows():
                    st.warning(f"**{row['Station']}**: {row['UPH']:.1f} UPH")
            else:
                st.info("All stations above target!")
    
    # Download
    st.markdown("---")
    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv,
        f"UPH_{selected_model}_{start_date}_to_{end_date}.csv",
        "text/csv"
    )
    
    records = load_records()
    if not records:
        st.info("ยังไม่มีข้อมูล")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([r.to_dict() for r in records])
    df['date'] = pd.to_datetime(df['date'])
    
    # Date Range Filter
    st.markdown("### 📅 Select Date Range")
    col1, col2 = st.columns(2)
    
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    with col1:
        start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
    
    # Filter by date range
    df_filtered = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
    
    if df_filtered.empty:
        st.warning("⚠️ ไม่มีข้อมูลในช่วงวันที่ที่เลือก")
        return
    
    st.markdown("---")
    
    # Select Model
    models = sorted(df_filtered['model'].unique())
    selected_model = st.selectbox("📦 Select Model:", models)
    
    # Filter by model
    model_data = df_filtered[df_filtered['model'] == selected_model]
    
    if model_data.empty:
        st.warning("ไม่มีข้อมูล")
        return
    
    # Parse cycle times from average column
    stations = []
    for _, row in model_data.iterrows():
        avg_str = row.get('average', '')
        if avg_str:
            ct = CycleTime.parse(avg_str)
            if ct:
                stations.append({
                    'station': row['station'],
                    'pre': ct.pre,
                    'machine': ct.machine,
                    'post': ct.post,
                    'saved_output': row.get('output', '1')
                })
    
    if not stations:
        st.warning("ไม่มีข้อมูล Cycle Time")
        return
    
    st_df = pd.DataFrame(stations)
    
    # Average by station
    avg_df = st_df.groupby('station').agg({
        'pre': 'mean',
        'machine': 'mean',
        'post': 'mean'
    }).reset_index()
    
    # UPH Target Input
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        uph_target = st.number_input(
            "🎯 UPH Target",
            min_value=0,
            value=100,
            step=10,
            help="เป้าหมาย UPH (จะแสดงเส้นสีแดงในกราฟ)"
        )
    with col2:
        st.write("")
        st.write("")
        if uph_target > 0:
            st.success(f"Target UPH set to: **{uph_target}** units/hour")
    
    # Get default outputs
    st.markdown("---")
    st.markdown("### 🔢 Output per Station")
    
    outputs = {}
    num_cols = min(4, len(avg_df))
    cols = st.columns(num_cols)
    
    for i, row in avg_df.iterrows():
        station = row['station']
        
        # Get saved output
        saved = st_df[st_df['station'] == station]['saved_output'].iloc[0]
        try:
            default_output = int(float(str(saved).strip())) if saved and str(saved).strip() else 1
        except:
            default_output = 1
        
        col_idx = i % num_cols
        with cols[col_idx]:
            outputs[station] = st.number_input(
                station,
                min_value=1,
                value=default_output,
                step=1,
                key=f"output_{station}"
            )
    
    # Calculate UPH
    avg_df['output'] = avg_df['station'].map(outputs)
    avg_df['total_seconds'] = avg_df['pre'] + avg_df['machine'] + avg_df['post']
    
    # UPH = 3600 / (pre + machine + post) * output
    avg_df['UPH'] = avg_df.apply(
        lambda x: (3600.0 / x['total_seconds'] * x['output']) if x['total_seconds'] > 0 else 0,
        axis=1
    )
    
    # Show results
    st.markdown("---")
    st.markdown("### 📋 Results")
    
    result_df = avg_df[['station', 'pre', 'machine', 'post', 'output', 'UPH']].copy()
    result_df.columns = ['Station', 'Pre(s)', 'Machine(s)', 'Post(s)', 'Output', 'UPH']
    
    st.dataframe(result_df.style.format({
        'Pre(s)': '{:.1f}',
        'Machine(s)': '{:.1f}',
        'Post(s)': '{:.1f}',
        'UPH': '{:.1f}'
    }))
    
    # THE MAIN UPH CHART WITH TARGET LINE
    st.markdown("---")
    st.markdown("### 📊 UPH Chart with Target Line")
    
    # Sort by station name for consistent display
    chart_data = result_df.sort_values('Station')
    
    # Create Plotly chart
    fig = go.Figure()
    
    # Add UPH bars
    fig.add_trace(go.Bar(
        x=chart_data['Station'],
        y=chart_data['UPH'],
        name='UPH',
        marker_color='#6366f1',
        text=chart_data['UPH'].round(1),
        textposition='outside',
        textfont=dict(size=12)
    ))
    
    # Add target line (red)
    if uph_target > 0:
        fig.add_trace(go.Scatter(
            x=chart_data['Station'],
            y=[uph_target] * len(chart_data),
            mode='lines',
            name=f'Target ({uph_target})',
            line=dict(color='red', width=3, dash='dash'),
            showlegend=True
        ))
    
    # Update layout
    fig.update_layout(
        title=f"UPH by Station - {selected_model}",
        xaxis_title="Station",
        yaxis_title="UPH (Units Per Hour)",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Stats with Target Comparison
    st.markdown("---")
    st.markdown("### 📈 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    avg_uph = result_df['UPH'].mean()
    max_uph = result_df['UPH'].max()
    min_uph = result_df['UPH'].min()
    
    with col1:
        st.metric("Avg UPH", f"{avg_uph:.1f}")
    with col2:
        st.metric("Max UPH", f"{max_uph:.1f}")
    with col3:
        st.metric("Min UPH", f"{min_uph:.1f}")
    with col4:
        if uph_target > 0:
            diff = avg_uph - uph_target
            st.metric("vs Target", f"{diff:+.1f}", delta=f"{diff:+.1f}")
        else:
            st.metric("Target", "Not Set")
    
    # Stations above/below target
    if uph_target > 0:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        above_target = result_df[result_df['UPH'] >= uph_target]
        below_target = result_df[result_df['UPH'] < uph_target]
        
        with col1:
            st.markdown("#### ✅ Above Target")
            if not above_target.empty:
                for _, row in above_target.iterrows():
                    st.success(f"**{row['Station']}**: {row['UPH']:.1f} UPH")
            else:
                st.info("No stations above target")
        
        with col2:
            st.markdown("#### ⚠️ Below Target")
            if not below_target.empty:
                for _, row in below_target.iterrows():
                    st.warning(f"**{row['Station']}**: {row['UPH']:.1f} UPH")
            else:
                st.info("All stations above target!")
    
    # Download
    st.markdown("---")
    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv,
        f"UPH_{selected_model}_{start_date}_to_{end_date}.csv",
        "text/csv"
    )
    
    # Filter by model
    model_data = df[df['model'] == selected_model]
    
    if model_data.empty:
        st.warning("ไม่มีข้อมูล")
        return
    
    # Parse cycle times from average column
    stations = []
    for _, row in model_data.iterrows():
        avg_str = row.get('average', '')
        if avg_str:
            ct = CycleTime.parse(avg_str)
            if ct:
                stations.append({
                    'station': row['station'],
                    'pre': ct.pre,
                    'machine': ct.machine,
                    'post': ct.post,
                    'saved_output': row.get('output', '1')
                })
    
    if not stations:
        st.warning("ไม่มีข้อมูล Cycle Time")
        return
    
    st_df = pd.DataFrame(stations)
    
    # Average by station
    avg_df = st_df.groupby('station').agg({
        'pre': 'mean',
        'machine': 'mean',
        'post': 'mean'
    }).reset_index()
    
    # Get default outputs
    st.markdown("---")
    st.markdown("### 🔢 Output per Station")
    
    outputs = {}
    num_cols = min(4, len(avg_df))
    cols = st.columns(num_cols)
    
    for i, row in avg_df.iterrows():
        station = row['station']
        
        # Get saved output
        saved = st_df[st_df['station'] == station]['saved_output'].iloc[0]
        try:
            default_output = int(float(str(saved).strip())) if saved and str(saved).strip() else 1
        except:
            default_output = 1
        
        col_idx = i % num_cols
        with cols[col_idx]:
            outputs[station] = st.number_input(
                station,
                min_value=1,
                value=default_output,
                step=1,
                key=f"output_{station}"
            )
    
    # Calculate UPH
    avg_df['output'] = avg_df['station'].map(outputs)
    avg_df['total_seconds'] = avg_df['pre'] + avg_df['machine'] + avg_df['post']
    
    # UPH = 3600 / (pre + machine + post) * output
    avg_df['UPH'] = avg_df.apply(
        lambda x: (3600.0 / x['total_seconds'] * x['output']) if x['total_seconds'] > 0 else 0,
        axis=1
    )
    
    # Show results
    st.markdown("---")
    st.markdown("### 📋 Results")
    
    result_df = avg_df[['station', 'pre', 'machine', 'post', 'output', 'UPH']].copy()
    result_df.columns = ['Station', 'Pre(s)', 'Machine(s)', 'Post(s)', 'Output', 'UPH']
    
    st.dataframe(result_df.style.format({
        'Pre(s)': '{:.1f}',
        'Machine(s)': '{:.1f}',
        'Post(s)': '{:.1f}',
        'UPH': '{:.1f}'
    }))
    
    # THE MAIN UPH CHART
    st.markdown("---")
    st.markdown("### 📊 UPH Chart")
    
    chart_df = result_df.set_index('Station')['UPH'].sort_values(ascending=False)
    st.bar_chart(chart_df)
    
    # Stats
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg UPH", f"{result_df['UPH'].mean():.1f}")
    with col2:
        st.metric("Max UPH", f"{result_df['UPH'].max():.1f}")
    with col3:
        st.metric("Min UPH", f"{result_df['UPH'].min():.1f}")
    
    # Download
    st.markdown("---")
    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv,
        f"UPH_{selected_model}.csv",
        "text/csv"
    )