import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from firebase_utils import store_data,retrieve_data
from llama_api import query_llama,build_prompt
import datetime
from firebase_admin import db
from visualize import (
    compute_total_usage,
    prepare_grouped_data_for_chart,
    get_year_data,
    aggregate_monthly_usage,
    aggregate_weekly_usage,
    get_week_number
)
load_dotenv()
from render import render_grouped_bar_chart,render_single_bar_chart
THRESHOLD_PER_PERSON = 350 #average water usage limit per person

if "basic_info" not in st.session_state:
    st.session_state.basic_info = {}



if "monthly_data_grouped" not in st.session_state:
    st.session_state.monthly_data_grouped = {}

if "weekly_data_grouped" not in st.session_state:
    st.session_state.weekly_data_grouped = {}


st.set_page_config(page_title="Water Conservation Advisor", layout="centered")
st.title("💧 Water Conservation Household Advisor")

menu = st.sidebar.radio("Choose Action", ["Submit Household Data", "View Stored Data"])

if menu == "Submit Household Data":
    st.subheader("🏠 Enter Household Water Details")

    name = st.text_input("Full Name")
    family_members = st.number_input("Family Members", min_value=1, step=1)

    st.markdown("### 🚰 Enter Water Usage per Resource")

    # Define available resources
    available_resources = ["Tap Water", "Borewell", "Rain Catchment", "Tanker Water"]

    # Initialize inputs
    water_usage_gallons = {}
    selected_resources=[]

    for resource in available_resources:
        col1, col2 = st.columns([2, 1])
        with col1:
            checked = st.checkbox(resource, key=f"{resource}_checkbox")
        with  col2:
            if checked:
                usage = st.number_input(f"{resource} (litres)", min_value=0, step=1, key=f"{resource}_input")
                water_usage_gallons[resource] = usage
                selected_resources.append(resource)
    

    client_id_input = st.text_input("Client ID (Leave empty if you are a new user)", value="")

    if st.button("Submit Data"):
        if name and water_usage_gallons:
            basic_info = {
                "name": name,
                "family_members": family_members

            }
            detail_data=water_usage_gallons
            st.session_state.basic_info = basic_info

            client_id = client_id_input if client_id_input else None
            client_id = store_data(basic_info,detail_data, client_id)  # store daily usage
            st.session_state.client_id = client_id
            
            st.success(f"✅ Data saved successfully!\n\nClient ID: {client_id}\n\nSave this Client ID for your future login")
           
           

            # Total usage for the day
            total_usage = sum(detail_data.values())

            # Fetch number of family members from basic_info
            members = basic_info.get("family_members", 1)

            # Calculate allowed limit
            threshold = THRESHOLD_PER_PERSON * members
            st.session_state.threshold=threshold

            if total_usage > threshold:
                st.warning(f"🚨 Alert: Your usage of {total_usage} litres exceeds the allowed limit of {threshold} litres.")

        
        else:
            st.warning("Please fill all fields and enter at least one resource.")
    st.markdown("---")
    st.subheader("📊 Visualize Usage")

    # 1. Select Year
    current_year = datetime.datetime.now().year
    year = st.selectbox("Select Year", [str(y) for y in range(current_year, current_year - 5, -1)])

    # 2. Select Month (for weekly chart)
    month = st.selectbox("Select Month (for Weekly View)", [f"{i:02d}" for i in range(1, 13)])

    # 3. Show Charts Button
    if st.button("Generate Charts"):
        # Fetch yearly usage data
        client_id = st.session_state.client_id
        year_data = get_year_data(client_id, year)

        if not year_data:
            st.warning("No usage data found for the selected year.")
        else:
            # Monthly summary
            monthly_summary = aggregate_monthly_usage(year_data)

            # Weekly summary for selected month
            monthly_data = year_data.get(month, {})
            weekly_summary = aggregate_weekly_usage(monthly_data, year, month)

            # Monthly charts
            month_labels, monthly_data_grouped = prepare_grouped_data_for_chart(monthly_summary)
            st.session_state.monthly_data_grouped=monthly_data_grouped
        
            render_grouped_bar_chart(monthly_data_grouped, month_labels, "📊 Month vs Water Usage by Resource")

            month_labels, month_totals = compute_total_usage(monthly_summary)
            render_single_bar_chart(month_totals, month_labels, "📈 Month vs Total Water Usage")

            # Weekly charts
            week_labels, weekly_data_grouped = prepare_grouped_data_for_chart(weekly_summary)
            st.session_state.weekly_data_grouped=weekly_data_grouped
        

            render_grouped_bar_chart(weekly_data_grouped, week_labels, "📊 Week vs Water Usage by Resource")

            week_labels, week_totals = compute_total_usage(weekly_summary)
            render_single_bar_chart(week_totals, week_labels, "📈 Week vs Total Water Usage")
    st.subheader("💬 Chat with Water Conservation Advisor")
    user_question = st.text_input("Ask a water-related question:")

    if st.button("Get Response"):
        if user_question:
            if st.session_state.basic_info:
                combined_info = st.session_state.basic_info | {
                    "monthly_summary": st.session_state.monthly_data_grouped,
                    "weekly_summary": st.session_state.weekly_data_grouped
            }
                final_prompt = build_prompt(user_question, combined_info)

                with st.spinner("Thinking..."):
                    reply = query_llama(final_prompt)
                    st.success(reply)
            else:
                st.warning("⚠️ Please submit household data first.")
        else:
            st.warning("⚠️ Please enter a question.")
    st.markdown("---")
    st.subheader("📝 Feedback & Survey Form")
    satisfaction = st.slider("How satisfied are you with the Water Advisor app?", 1, 10, 5)
    usefulness = st.radio("Did you find the water-saving suggestions useful?", ["Yes", "Somewhat", "No"])
    features = st.multiselect("Which features did you like?", [
    "Daily/Monthly Usage Charts",
    "LLaMa Chat Assistant",
    "Data Submission Flow"
    ])
    comments = st.text_area("Any suggestions or issues you faced?")
    survey_data={}
    if st.button("Submit Survey"):
        survey_data = {
        "satisfaction": satisfaction,
        "usefulness": usefulness,
        "features_liked": features,
        "comments": comments,
        "timestamp": str(datetime.datetime.now())
        }
        st.success("Thank you for submitting the survey")

        db.reference("/SurveyResponses").push(survey_data)

    


elif menu == "View Stored Data":
    st.subheader("🔍 Retrieve Household Data")

    client_id = st.text_input("Enter Client ID to Fetch")

    if st.button("Fetch Data"):
        if client_id:
            data = retrieve_data(client_id)
            if data:
                st.success("📦 Data Retrieved:")
                st.markdown(f"### 👤 Name: `{data.get('name', 'N/A')}`")
                st.markdown(f"### 👨‍👩‍👧‍👦 Family Members: `{data.get('family_members', 'N/A')}`")
                usage = data.get("daily_usage", {})
                rows = []

                for year, months in usage.items():
                    for month, days in months.items():
                        for day, resources in days.items():
                            total_usage = sum(resources.values())
                            water_saved = st.session_state.threshold - total_usage
                            for resource, amount in resources.items():
                                rows.append({
                                    "Date": f"{year}-{month}-{day}",
                                    "Resource": resource,
                                    "Litres Used": amount
                                    "Total Daily Usage": total_usage,
                                    "Water Saved": max(0, water_saved) 
                                        })

                # Convert to DataFrame
                df = pd.DataFrame(rows)

                # Display
                st.subheader(f"Water Usage Details")
                st.dataframe(df)
                
            else:
                st.error("❌ No data found for this Client ID.")
        else:
            st.warning("⚠️ Please enter a valid Client ID.")
  

    
    



        
