import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Add Utility Functions Here
def calculate_kpis(file_path):
    """Calculate KPIs and return data for charts."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        st.warning(f"No data file found at {file_path}. Showing default KPI values.")
        return {
            "compliance_rate": "No Data",
            "avg_temp": "No Data",
            "running_percentage": "No Data",
            "data": pd.DataFrame()  # Return an empty DataFrame for charts
        }

    # Load the CSV file
    data = pd.read_csv(file_path)
    if data.empty:
        st.warning("The data file is empty. Showing default KPI values.")
        return {
            "compliance_rate": "No Data",
            "avg_temp": "No Data",
            "running_percentage": "No Data",
            "data": pd.DataFrame()  # Return an empty DataFrame for charts
        }

    # Calculate KPIs
    compliance_rate = data["Is Running"].mean() * 100
    avg_temp = data[["Driving End Temp", "Driven End Temp"]].mean().mean()
    running_percentage = (data["Is Running"].sum() / len(data)) * 100

    # Return KPIs and data
    return {
        "compliance_rate": f"{compliance_rate:.2f}%",
        "avg_temp": f"{avg_temp:.2f}°C",
        "running_percentage": f"{running_percentage:.2f}%",
        "data": data
    }

def generate_recommendations(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return ["No data available for recommendations."]
    data = pd.read_csv(file_path)
    if data.empty:
        return ["No data available for recommendations."]
    recommendations = []
    if (data["Driving End Temp"] > 80).any():
        recommendations.append("Investigate high driving end temperature.")
    if (data["RMS Velocity (mm/s)"] > 5).any():
        recommendations.append("Check equipment with high vibration levels.")
    if (data["Oil Level"] == "Low").any():
        recommendations.append("Refill oil for equipment with low levels.")
    if not recommendations:
        recommendations.append("All equipment is operating within normal parameters.")
    return recommendations

def compliance_summary(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return {"safety_check": "No Data", "oil_level_compliance": "No Data"}
    data = pd.read_csv(file_path)
    if data.empty:
        return {"safety_check": "No Data", "oil_level_compliance": "No Data"}
    safety_check = (data["Abnormal Sound"] == "No").mean() * 100
    oil_level_compliance = (data["Oil Level"] != "Low").mean() * 100
    return {
        "safety_check": f"{safety_check:.2f}%",
        "oil_level_compliance": f"{oil_level_compliance:.2f}%"
    }


# Set page title
st.set_page_config(page_title="Indorama Petrochemicals Ltd", layout="wide")

# Main Page Functionality
if "page" not in st.session_state:
    st.session_state.page = "main"

if st.session_state.page == "main":
    # Set the file path for the database
    file_path = "data/condition_data.csv"

    st.title("INDORAMA PETROCHEMICALS LTD")

    # Greeting Based on Time
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning!"
    elif 12 <= current_hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"

    st.header(greeting)

    # Display KPIs
    st.subheader("Key Performance Indicators (KPIs)")
    kpis = calculate_kpis(file_path)
    col1, col2, col3 = st.columns(3)
    col1.metric("Compliance Rate", kpis["compliance_rate"])
    col2.metric("Average Temperature", kpis["avg_temp"])
    col3.metric("Running Equipment", kpis["running_percentage"])

    # Add KPI Charts
    data = kpis["data"]
    if not data.empty:  # Check if data is available
        st.write("---")
        st.subheader("KPI Charts")

        # Compliance Rate Trend
        if "Date" in data.columns and "Is Running" in data.columns:
            data["Date"] = pd.to_datetime(data["Date"])  # Ensure Date is datetime
            compliance_trend = data.groupby("Date")["Is Running"].mean() * 100
            st.write("### Compliance Rate Trend")
            st.line_chart(compliance_trend)

        # Average Temperature Trend
        if "Driving End Temp" in data.columns and "Driven End Temp" in data.columns:
            data["Avg Temp"] = data[["Driving End Temp", "Driven End Temp"]].mean(axis=1)
            avg_temp_trend = data.groupby("Date")["Avg Temp"].mean()
            st.write("### Average Temperature Trend")
            st.line_chart(avg_temp_trend)

        # Running Equipment Count
        if "Is Running" in data.columns:
            running_equipment = data.groupby("Date")["Is Running"].sum()
            st.write("### Running Equipment Count")
            st.bar_chart(running_equipment)

    else:
        st.warning("No data available for KPI charts.")

    # Display Recommendations
    st.subheader("Recommendations")
    recommendations = generate_recommendations(file_path)
    for recommendation in recommendations:
        st.write(f"- {recommendation}")

    st.write("---")

    # Display Compliance Metrics
    st.subheader("Compliance Metrics")
    compliance = compliance_summary(file_path)
    st.write(f"**Safety Check Compliance:** {compliance['safety_check']}")
    st.write(f"**Oil Level Compliance:** {compliance['oil_level_compliance']}")

    # Next Button to Navigate
    if st.button("Next"):
        st.session_state.page = "monitoring"

elif st.session_state.page == "monitoring":

    def load_data(file_path):
        """Load data from a CSV file."""
        if not os.path.exists(file_path):
            return pd.DataFrame()  # Return an empty DataFrame if file doesn't exist
        return pd.read_csv(file_path)


    def filter_data(df, equipment, start_date, end_date):
        """Filter data by equipment and date range."""
        df["Date"] = pd.to_datetime(df["Date"])  # Convert Date column to datetime
        filtered_df = df[
            (df["Equipment"] == equipment) &
            (df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date))
            ]
        return filtered_df

    # Tabs for Condition Monitoring and Report
    tab1, tab2 = st.tabs(["Condition Monitoring", "Report"])

    with tab1:
        st.header("Condition Monitoring Data Entry")

        # Equipment lists for each area
        equipment_lists = {
            "Reaction": [
                "3-P-101", "3-P-102-A", "3-P-102-B", "3-P-103-A", "3-P-103-B",
                "3-P-201", "3-P-202", "3-P-203", "3-P-204", "3-P-205", "3-P-206",
                "3-P-208", "3-P-209", "3-P-301-A", "3-P-301-B", "3-P-301-C",
                "3-K-101-A", "3-K-101-B", "3-K-301-A", "3-K-301-B", "3-P-301-A",
                "3-P-301-B", "3-P-301-C", "3-P-302-A", "3-P-302-B", "3-P-302-C",
                "3-P-303-A", "3-P-303-B", "3-P-304-A", "3-P-304-B", "3-P-305-A",
                "3-P-305-B", "3-P-306-A", "3-P-306-B", "3-M-301", "3-M-201",
                "3-M-203", "3-M-205", "3-M-207", "3-M-209", "3-P-401-A", "3-P-401-B", "3-K-102", "3-K-401", "3-K-402"
            ],
            "Distillation": [
                "3-P-901-A", "3-P-901-B", "3-P-902-A", "3-P-902-B", "3-P-903-A",
                "3-P-903-B", "3-P-903-C", "3-P-904-A", "3-P-904-B", "3-P-905-A",
                "3-P-905-B", "3-P-906-A", "3-P-906-B", "3-P-907-A", "3-P-907-B",
                "3-P-909-A", "3-P-909-B", "3-P-910-A", "3-P-910-B", "3-P-911-A",
                "3-P-911-B", "3-P-912-A", "3-P-912-B", "3-P-914-A", "3-P-914-B",
                "3-P-916-A", "3-P-916-B", "3-P-917", "3-K-901", "3-K-1001-A",
                "3-K-1001-B", "3-K-1001-C", "3-P-1001-A", "3-P-1001-B", "3-P-1001-C",
                "3-P-1001-D", "3-P-1001-E", "3-P-1001-F", "3-P-1011", "3-P-1101-A",
                "3-P-1101-B", "3-P-920-A", "3-P-920-B", "3-P-1102-A", "3-P-1102-B",
                "3-P-1121", "3-P-1122", "3-P-1201-A", "3-P-1201-B", "3-P-1202-A",
                "3-P-1202-B", "3-RUP-901", "3-RUK-901"
            ],
            "Finishing": [
                "3-P-501-A", "3-P-501-B", "3-P-502-A", "3-P-502-B", "3-P-503-A",
                "3-P-503-B", "3-P-504-A", "3-P-504-B", "3-P-601-A", "3-P-601-B",
                "3-P-601-C", "3-P-601-D", "3-P-602-A", "3-P-602-B", "3-P-602-C",
                "3-P-602-D", "3-P-603-A", "3-P-603-B", "3-P-604-A", "3-P-604-B",
                "3-P-604-C", "3-P-604-D", "3-P-605-1", "3-P-605-2", "3-P-606-1",
                "3-P-606-2", "3-P-607-1", "3-P-607-2", "3-P-608-1", "3-P-608-2",
                "3-P-609-1", "3-P-609-2", "3-P-610-1", "3-P-610-2", "3-P-611-1",
                "3-P-611-2", "3-P-612-1", "3-P-612-2", "3-K-602-A", "3-K-602-B",
                "3-K-602-C", "3-K-603-1", "3-K-603-2", "3-K-605-A", "3-K-605-B",
                "3-K-605-C", "3-K-605-D", "3-K-605-E", "3-K-605-F", "3-K-605-G",
                "3-K-606-A", "3-K-606-B", "3-K-606-C", "3-K-606-D", "3-K-606-E",
                "3-K-606-F", "3-K-606-G", "3-K-701-A", "3-K-701-B", "3-K-701-C",
                "3-K-701-D", "3-K-701-E", "3-K-701-F", "3-K-704-A", "3-K-704-B",
                "3-K-801-A", "3-K-801-B", "3-K-802-A", "3-K-802-B", "3-K-802-C",
                "3-M-501", "3-M-502", "3-M-503", "3-M-504", "3-M-505"
            ],
            "Butene": [
                "2-P-2101-A", "2-P-2101-B", "2-P-2301-A", "2-P-2301-B",
                "2-P-2302-A", "2-P-2302-B", "2-P-2306-A", "2-P-2306-B",
                "2-P-2201-A", "2-P-2201-B", "2-P-2202-A", "2-P-2202-B",
                "2-P-2203-A", "2-P-2203-B", "2-P-2304-A", "2-P-2304-B",
                "2-P-2305-A", "2-P-2305-B", "2-P-2401-A", "2-P-2401-B",
                "2-P-2601-A", "2-P-2601-B", "2-P-2701", "2-P-2501-A",
                "2-P-2501-B", "2-P-2502-A", "2-P-2502-B", "2-P-2602-A",
                "2-P-2602-B", "2-P-2303-A", "2-P-2303-B"
            ]
        }


        # Persistent fields
        date = st.date_input("Date", key="date")
        area = st.selectbox("Select Area", options=list(equipment_lists.keys()), key="area")
        equipment_options = equipment_lists.get(area, [])
        equipment = st.selectbox("Select Equipment", options=equipment_options, key="equipment")


        # Tick box for "Is the equipment running?"
        is_running = st.checkbox("Is the equipment running?", key="is_running")

        # Data Entry Fields
        if is_running:
            de_temp = st.number_input("Driving End Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                      key="de_temp")
            dr_temp = st.number_input("Driven End Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                      key="dr_temp")
            oil_level = st.selectbox("Oil Level", ["Normal", "Low", "High"], key="oil_level")
            abnormal_sound = st.selectbox("Abnormal Sound", ["No", "Yes"], key="abnormal_sound")
            leakage = st.selectbox("Leakage", ["No", "Yes"], key="leakage")
            observation = st.text_area("Observations", key="observation")

            # Vibration Monitoring
            st.subheader("Vibration Monitoring")
            vibration_rms_velocity = st.number_input("RMS Velocity (mm/s)", min_value=0.0, max_value=100.0, step=0.1,
                                                     key="vibration_rms_velocity")
            vibration_peak_acceleration = st.number_input("Peak Acceleration (g)", min_value=0.0, max_value=10.0,
                                                          step=0.1,
                                                          key="vibration_peak_acceleration")
            vibration_displacement = st.number_input("Displacement (µm)", min_value=0.0, max_value=1000.0, step=0.1,
                                                     key="vibration_displacement")

            # Gearbox Inputs
            gearbox = st.checkbox("Does the equipment have a gearbox?", key="gearbox")
            if gearbox:
                gearbox_temp = st.number_input("Gearbox Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                               key="gearbox_temp")
                gearbox_oil = st.selectbox("Gearbox Oil Level", ["Normal", "Low", "High"], key="gearbox_oil")
                gearbox_leakage = st.selectbox("Gearbox Leakage", ["No", "Yes"], key="gearbox_leakage")
                gearbox_abnormal_sound = st.selectbox("Gearbox Abnormal Sound", ["No", "Yes"], key="gearbox_abnormal_sound")
                # Vibration Monitoring for gearbox
                st.subheader("Gearbox_Vibration Monitoring")
                gearbox_vibration_rms_velocity = st.number_input("Gearbox RMS Velocity (mm/s)", min_value=0.0, max_value=100.0,
                                                         step=0.1,
                                                         key="gearbox_vibration_rms_velocity")
                gearbox_vibration_peak_acceleration = st.number_input("Gearbox Peak Acceleration (g)", min_value=0.0, max_value=10.0,
                                                              step=0.1,
                                                              key="gearbox_vibration_peak_acceleration")
                gearbox_vibration_displacement = st.number_input("Gearbox Displacement (µm)", min_value=0.0, max_value=1000.0, step=0.1,
                                                         key="gearbox_vibration_displacement")

        # Submit Button
        if st.button("Submit Data"):
            # Prepare data
            if not is_running:
                # If equipment is not running, set all numeric fields to 0 and strings to 'N/A'
                data = {
                    "Date": [date],
                    "Area": [area],
                    "Equipment": [equipment],
                    "Is Running": [False],
                    "Driving End Temp": [0.0],
                    "Driven End Temp": [0.0],
                    "Oil Level": ["N/A"],
                    "Abnormal Sound": ["N/A"],
                    "Leakage": ["N/A"],
                    "Observation": ["Not Running"],
                    "RMS Velocity (mm/s)": [0.0],
                    "Peak Acceleration (g)": [0.0],
                    "Displacement (µm)": [0.0],
                    "Gearbox Temp": [0.0],
                    "Gearbox Oil Level": ["N/A"],
                    "Gearbox Leakage": ["N/A"],
                    "Gearbox Abnormal Sound": ["N/A"],
                    "Gearbox RMS Velocity (mm/s)": [0.0],
                    "Gearbox Peak Acceleration (g)": [0.0],
                    "Gearbox Displacement (µm)": [0.0],
                }
            else:
                # If equipment is running, save entered values
                data = {
                    "Date": [date],
                    "Area": [area],
                    "Equipment": [equipment],
                    "Is Running": [True],
                    "Driving End Temp": [st.session_state.de_temp],
                    "Driven End Temp": [st.session_state.dr_temp],
                    "Oil Level": [st.session_state.oil_level],
                    "Abnormal Sound": [st.session_state.abnormal_sound],
                    "Leakage": [st.session_state.leakage],
                    "Observation": [st.session_state.observation],
                    "RMS Velocity (mm/s)": [st.session_state.vibration_rms_velocity],
                    "Peak Acceleration (g)": [st.session_state.vibration_peak_acceleration],
                    "Displacement (µm)": [st.session_state.vibration_displacement],
                    "Gearbox Temp": [st.session_state.gearbox_temp if "gearbox_temp" in st.session_state else 0.0],
                    "Gearbox Oil Level": [st.session_state.gearbox_oil if "gearbox_oil" in st.session_state else "N/A"],
                    "Gearbox Leakage": [
                        st.session_state.gearbox_leakage if "gearbox_leakage" in st.session_state else "N/A"],
                    "Gearbox Abnormal Sound": [
                        st.session_state.gearbox_leakage if "gearbox_abnormal_sound" in st.session_state else "N/A"]
                }

            # Save to CSV
            df = pd.DataFrame(data)
            file_path = "data/condition_data.csv"
            if not os.path.exists("data"):
                os.makedirs("data")
            if os.path.exists(file_path):
                df.to_csv(file_path, mode="a", header=False, index=False)
            else:
                df.to_csv(file_path, index=False)

            st.success("Data Submitted Successfully!")


    # Tab 2: Reports and Visualizations
    with (tab2):
        st.header("Reports and Visualization")
        file_path = "data/condition_data.csv"

        # Load data
        data = load_data(file_path)

        if data.empty:
            st.warning("No data available. Please enter condition monitoring data first.")
        else:
            st.write("### Full Data")
            st.dataframe(data)

            # Debugging Step: Show columns
            st.write("### Column Names")
            st.write(list(data.columns))

            # Check if 'Equipment' column exists
            if "Equipment" not in data.columns:
                st.error("The 'Equipment' column is missing. Please check the data file.")
            else:
                # Dropdown for Equipment Selection
                equipment_options = data["Equipment"].unique()
                selected_equipment = st.selectbox("Select Equipment", options=equipment_options)

                # Date Range Inputs
                start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
                end_date = st.date_input("End Date", value=datetime.now())

                if start_date > end_date:
                    st.error("Start date cannot be later than end date.")
                else:
                    # Filter Data
                    filtered_data = filter_data(data, selected_equipment, start_date, end_date)

                    if filtered_data.empty:
                        st.warning(f"No data found for {selected_equipment} between {start_date} and {end_date}.")
                    else:
                        st.write(f"### Filtered Data for {selected_equipment}")
                        st.dataframe(filtered_data)

                        # Visualizations
                        st.subheader("Data Visualizations")

                        # Allow user to choose the dataset for visualization
                        data_option = st.radio(
                            "Select data for visualization:",
                            options=["General Table (All Data)", "Filtered Table"],
                            key="data_option"
                        )

                        # Select appropriate dataset based on user choice
                        if data_option == "General Table (All Data)":
                            visualization_data = data  # Use the full dataset
                            st.write("Using data from the general table (all records).")
                        else:
                            visualization_data = filtered_data  # Use the filtered dataset
                            st.write("Using data from the filtered table.")

                        # Driving and Driven End Temperature Trend
                        if "Driving End Temp" in visualization_data.columns and "Driven End Temp" in visualization_data.columns:
                            st.write("#### Driving and Driven End Temperature Trend for Equipment")
                            temp_chart_data = visualization_data[["Date", "Driving End Temp", "Driven End Temp"]]
                            temp_chart_data = temp_chart_data.set_index("Date")
                            st.line_chart(temp_chart_data)
                        else:
                            st.warning(
                                "Temperature data (Driving End or Driven End) is missing in the selected dataset.")

                        # Equipment Vibration Trend
                        if "RMS Velocity (mm/s)" in visualization_data.columns and "Peak Acceleration (g)" in visualization_data.columns and "Displacement (µm)" in visualization_data.columns:
                            st.write("#### Vibration Trend for Equipment")
                            vibration_chart_data = visualization_data[["Date", "RMS Velocity (mm/s)", "Peak Acceleration (g)", "Displacement (µm)"]]
                            vibration_chart_data = vibration_chart_data.set_index("Date")
                            st.line_chart(vibration_chart_data)
                        else:
                            st.warning(
                                "Vibration data (RMS Velocity (mm/s) or Peak Acceleration (g) or Displacement (µm)) is missing in the selected dataset.")

                        # Driving and Driven End Temperature Trend for Gearbox
                        if "Gearbox Temp" in visualization_data.columns:
                            st.write("#### Gearbox Temperature Trend")
                            gearbox_temp_chart_data = visualization_data[["Date", "Gearbox Temp"]]
                            gearbox_temp_chart_data = gearbox_temp_chart_data.set_index("Date")
                            st.line_chart(gearbox_temp_chart_data)
                        else:
                            st.warning(
                                "Gearbox Temperature data (Gearbox Temp) is missing in the selected dataset.")

                        # Equipment Vibration Trend for Gearbox
                        if "Gearbox RMS Velocity (mm/s)" in visualization_data.columns and "Gearbox Peak Acceleration (g)" in visualization_data.columns and "Gearbox Displacement (µm)" in visualization_data.columns:
                            st.write("#### Vibration Trend for Gearbox")
                            gearbox_vibration_chart_data = visualization_data[
                                ["Date", "Gearbox RMS Velocity (mm/s)", "Gearbox Peak Acceleration (g)", "Gearbox Displacement (µm)"]]
                            gearbox_vibration_chart_data = gearbox_vibration_chart_data.set_index("Date")
                            st.line_chart(gearbox_vibration_chart_data)
                        else:
                            st.warning(
                                "Gearbox Vibration data (Gearbox RMS Velocity (mm/s) or Gearbox Peak Acceleration (g) or Gearbox Displacement (µm)) is missing in the selected dataset.")

                        # Oil Level Distribution for Equipment
                        if "Oil Level" in visualization_data.columns:
                            st.write("#### Oil Level Distribution for Equipment")
                            oil_summary = visualization_data["Oil Level"].value_counts()
                            st.bar_chart(oil_summary)
                        else:
                            st.warning("Oil Level data is missing in the selected dataset.")

                        # Oil Level Distribution for Gearbox
                        if "Gearbox Oil Level" in visualization_data.columns:
                            st.write("#### Oil Level Distribution for Gearbox")
                            gearbox_oil_summary = visualization_data["Gearbox Oil Level"].value_counts()
                            st.bar_chart(gearbox_oil_summary)
                        else:
                            st.warning("Gearbox Oil Level data is missing in the selected dataset.")

    # Add Back Button
    if st.button("Back to Home"):
        st.session_state.page = "main"

