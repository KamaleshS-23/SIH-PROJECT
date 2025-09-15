# app.py (Streamlit UI with all requested features)
import streamlit as st
import requests
import json
from PIL import Image
import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Plant Disease Detector",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2e8b57;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3cb371;
        border-bottom: 2px solid #3cb371;
        padding-bottom: 10px;
    }
    .result-box {
        background-color: #f0fff0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #3cb371;
    }
    .critical {
        border-left: 5px solid #ff4b4b;
    }
    .warning {
        border-left: 5px solid #ffa500;
    }
    .sensor-data {
        background-color: #e8f4f8;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .device-status {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 5px;
        font-weight: bold;
    }
    .online {
        background-color: #d4edda;
        color: #155724;
    }
    .offline {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1 class="main-header">🌿 Plant Disease Detection System</h1>', unsafe_allow_html=True)
st.write("""
This AI-powered application helps farmers detect plant diseases early and recommends precise pesticide amounts 
to minimize chemical usage while maximizing crop health.
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose a page", 
                               ["Home", "Disease Detection", "Spray Control", "Sensor Dashboard", "History & Analytics"])

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = []
if 'device_status' not in st.session_state:
    st.session_state.device_status = {
        "esp32": "online",
        "esp32-cam": "online",
        "pump": "offline",
        "sensors": "online"
    }

# Simulate sensor data (replace with actual API calls to your IoT devices)
def get_sensor_data():
    """Simulate sensor data - replace with actual API calls to your ESP32"""
    return {
        "temperature": np.random.uniform(20, 35),
        "humidity": np.random.uniform(40, 80),
        "soil_moisture": np.random.uniform(20, 80),
        "ph_level": np.random.uniform(5.5, 7.5),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Home page
if app_mode == "Home":
    st.markdown('<h2 class="sub-header">Welcome to the Plant Disease Detection System</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://images.unsplash.com/photo-1591370264374-9a5aef8df17a?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80", 
                 caption="Early detection saves crops")
        st.info("""
        **How it works:**
        1. Upload an image of a plant leaf
        2. Our AI analyzes the image for diseases
        3. Get precise pesticide recommendations
        4. Control spraying remotely
        """)
    
    with col2:
        st.image("https://images.unsplash.com/photo-1625246335525-4d3c9c6d3095?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80", 
                 caption="Precision agriculture reduces chemical usage")
        st.success("""
        **Benefits:**
        - Reduce pesticide usage by up to 60%
        - Early disease detection
        - Lower farming costs
        - Environmentally friendly
        """)
    
    # Display device status
    st.markdown("### System Status")
    status_cols = st.columns(4)
    devices = list(st.session_state.device_status.keys())
    
    for i, device in enumerate(devices):
        status = st.session_state.device_status[device]
        with status_cols[i]:
            st.markdown(f'<div class="device-status {status}">{device.upper()}: {status.upper()}</div>', 
                       unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Recent Detections")
    if st.session_state.history:
        for i, detection in enumerate(st.session_state.history[-3:]):
            st.write(f"**Detection {i+1}:** {detection['disease']} ({detection['confidence']:.2%} confidence)")
    else:
        st.write("No detection history yet. Upload an image to get started!")

# Disease Detection page
elif app_mode == "Disease Detection":
    st.markdown('<h2 class="sub-header">Detect Plant Diseases</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload a plant leaf image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Process the image
        if st.button("Analyze Image"):
            with st.spinner("Analyzing image for diseases..."):
                try:
                    # Prepare the image for sending to the API
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format='JPEG')
                    img_bytes.seek(0)
                    
                    # Send request to Flask backend
                    files = {'image': ('image.jpg', img_bytes, 'image/jpeg')}
                    response = requests.post('http://localhost:5000/predict', files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Add timestamp to result
                        result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Store in history
                        st.session_state.history.append(result)
                        
                        # Display results
                        st.markdown("### Analysis Results")
                        
                        # Determine severity class for styling
                        severity_class = ""
                        if result['infection_percentage'] > 50:
                            severity_class = "critical"
                        elif result['infection_percentage'] > 10:
                            severity_class = "warning"
                            
                        st.markdown(f'<div class="result-box {severity_class}">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Disease Detected", result['disease'])
                            st.metric("Confidence Level", f"{result['confidence']:.2%}")
                            
                        with col2:
                            st.metric("Infection Percentage", f"{result['infection_percentage']:.2f}%")
                            st.metric("Recommended Pesticide", f"{result['pesticide_amount_ml']:.2f} ml")
                            
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Visualize infection areas
                        if 'segmentation_map' in result:
                            st.subheader("Infection Visualization")
                            fig, ax = plt.subplots(1, 2, figsize=(10, 5))
                            
                            # Original image
                            ax[0].imshow(image)
                            ax[0].set_title('Original Image')
                            ax[0].axis('off')
                            
                            # Segmentation map (simulated)
                            # In a real app, you would use the actual segmentation data from your model
                            sim_segmentation = np.random.rand(224, 224) > 0.7
                            ax[1].imshow(sim_segmentation, cmap='hot')
                            ax[1].set_title('Infection Areas')
                            ax[1].axis('off')
                            
                            st.pyplot(fig)
                        
                        # Show action buttons
                        if result['disease'] != 'Healthy' and result['pesticide_amount_ml'] > 0:
                            if st.button("💧 Initiate Spraying", type="primary"):
                                spray_data = {'amount': result['pesticide_amount_ml']}
                                spray_response = requests.post('http://localhost:5000/spray', json=spray_data)
                                
                                if spray_response.status_code == 200:
                                    st.success(f"Spraying {result['pesticide_amount_ml']} ml of pesticide")
                                    st.session_state.device_status["pump"] = "online"
                                else:
                                    st.error("Failed to initiate spraying. Please check your IoT connection.")
                    
                    else:
                        st.error("Error analyzing image. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Spray Control page
elif app_mode == "Spray Control":
    st.markdown('<h2 class="sub-header">Manual Spray Control</h2>', unsafe_allow_html=True)
    
    st.warning("Use this feature with caution. Manual spraying should only be done when necessary.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Quick Spray Presets")
        preset_amount = st.selectbox("Select preset amount", [10, 25, 50, 100, 200], index=2)
        
        if st.button(f"Spray {preset_amount} ml", key="preset_spray"):
            spray_data = {'amount': preset_amount}
            try:
                spray_response = requests.post('http://localhost:5000/spray', json=spray_data)
                
                if spray_response.status_code == 200:
                    st.success(f"Spraying {preset_amount} ml of pesticide")
                    st.session_state.device_status["pump"] = "online"
                    
                    # Add to history
                    st.session_state.history.append({
                        "disease": "Manual Spray",
                        "confidence": 1.0,
                        "infection_percentage": 0,
                        "pesticide_amount_ml": preset_amount,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                else:
                    st.error("Failed to initiate spraying. Please check your IoT connection.")
            except:
                st.error("Could not connect to the spray controller. Please check your connection.")
    
    with col2:
        st.subheader("Custom Spray Amount")
        custom_amount = st.slider("Custom amount (ml)", 0, 500, 50, 10)
        
        if st.button(f"Spray {custom_amount} ml", key="custom_spray"):
            spray_data = {'amount': custom_amount}
            try:
                spray_response = requests.post('http://localhost:5000/spray', json=spray_data)
                
                if spray_response.status_code == 200:
                    st.success(f"Spraying {custom_amount} ml of pesticide")
                    st.session_state.device_status["pump"] = "online"
                    
                    # Add to history
                    st.session_state.history.append({
                        "disease": "Manual Spray",
                        "confidence": 1.0,
                        "infection_percentage": 0,
                        "pesticide_amount_ml": custom_amount,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                else:
                    st.error("Failed to initiate spraying. Please check your IoT connection.")
            except:
                st.error("Could not connect to the spray controller. Please check your connection.")
    
    # Spray schedule section
    st.markdown("---")
    st.subheader("Schedule Spraying")
    
    schedule_col1, schedule_col2 = st.columns(2)
    
    with schedule_col1:
        schedule_time = st.time_input("Schedule time", value=datetime.now().time())
        
    with schedule_col2:
        schedule_amount = st.number_input("Scheduled amount (ml)", min_value=0, max_value=500, value=50)
        schedule_days = st.multiselect("Repeat on", 
                                      ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                      default=["Monday", "Wednesday", "Friday"])
    
    if st.button("Schedule Spraying"):
        st.success(f"Scheduled {schedule_amount} ml spraying at {schedule_time} on {', '.join(schedule_days)}")

# Sensor Dashboard page
elif app_mode == "Sensor Dashboard":
    st.markdown('<h2 class="sub-header">Real-time Sensor Dashboard</h2>', unsafe_allow_html=True)
    
    # Button to refresh sensor data
    if st.button("Refresh Sensor Data"):
        new_data = get_sensor_data()
        st.session_state.sensor_data.append(new_data)
        # Keep only the last 100 readings
        if len(st.session_state.sensor_data) > 100:
            st.session_state.sensor_data = st.session_state.sensor_data[-100:]
    
    if st.session_state.sensor_data:
        # Display current sensor readings
        current_data = st.session_state.sensor_data[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="sensor-data">
                <h3>Temperature</h3>
                <h2>{:.1f}°C</h2>
            </div>
            """.format(current_data['temperature']), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="sensor-data">
                <h3>Humidity</h3>
                <h2>{:.1f}%</h2>
            </div>
            """.format(current_data['humidity']), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="sensor-data">
                <h3>Soil Moisture</h3>
                <h2>{:.1f}%</h2>
            </div>
            """.format(current_data['soil_moisture']), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="sensor-data">
                <h3>pH Level</h3>
                <h2>{:.1f}</h2>
            </div>
            """.format(current_data['ph_level']), unsafe_allow_html=True)
        
        # Display sensor data history as charts
        st.subheader("Sensor Data History")
        
        df = pd.DataFrame(st.session_state.sensor_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create charts
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Temperature chart
        axes[0, 0].plot(df['timestamp'], df['temperature'], 'r-')
        axes[0, 0].set_title('Temperature (°C)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Humidity chart
        axes[0, 1].plot(df['timestamp'], df['humidity'], 'b-')
        axes[0, 1].set_title('Humidity (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Soil moisture chart
        axes[1, 0].plot(df['timestamp'], df['soil_moisture'], 'g-')
        axes[1, 0].set_title('Soil Moisture (%)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # pH level chart
        axes[1, 1].plot(df['timestamp'], df['ph_level'], 'purple')
        axes[1, 1].set_title('pH Level')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Display raw data
        if st.checkbox("Show Raw Sensor Data"):
            st.dataframe(df)
    else:
        st.info("No sensor data available. Click 'Refresh Sensor Data' to get current readings.")

# History & Analytics page
elif app_mode == "History & Analytics":
    st.markdown('<h2 class="sub-header">Detection History & Analytics</h2>', unsafe_allow_html=True)
    
    if st.session_state.history:
        # Show recent detections in a table
        st.subheader("Recent Detections")
        
        # Convert to DataFrame for easier manipulation
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df)
        
        # Simple analytics
        st.subheader("Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Disease distribution
            if 'disease' in history_df.columns:
                disease_counts = history_df['disease'].value_counts()
                
                fig, ax = plt.subplots()
                ax.pie(disease_counts.values, labels=disease_counts.index, autopct='%1.1f%%')
                ax.set_title("Disease Distribution")
                st.pyplot(fig)
        
        with col2:
            # Pesticide usage over time
            if 'pesticide_amount_ml' in history_df.columns and 'timestamp' in history_df.columns:
                # Convert timestamp to datetime
                history_df['datetime'] = pd.to_datetime(history_df['timestamp'])
                history_df = history_df.sort_values('datetime')
                
                fig, ax = plt.subplots()
                ax.plot(history_df['datetime'], history_df['pesticide_amount_ml'], marker='o')
                ax.set_xlabel("Date & Time")
                ax.set_ylabel("Pesticide Amount (ml)")
                ax.set_title("Pesticide Usage Trend")
                plt.xticks(rotation=45)
                st.pyplot(fig)
        
        # Export data
        st.markdown("---")
        st.subheader("Export Data")
        
        export_format = st.selectbox("Select export format", ["CSV", "JSON"])
        
        if export_format == "CSV":
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="plant_disease_history.csv",
                mime="text/csv"
            )
        else:
            json_str = history_df.to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="plant_disease_history.json",
                mime="application/json"
            )
        
        # Clear history button
        if st.button("Clear History"):
            st.session_state.history = []
            st.experimental_rerun()
            
    else:
        st.info("No detection history available. Perform some detections first.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Plant Disease Detection System • Powered by AI & IoT • Sustainable Farming Solutions</p>
</div>
""", unsafe_allow_html=True)
