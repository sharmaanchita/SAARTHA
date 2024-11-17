import streamlit as st
from gradio_client import Client
import dill
import pandas as pd
import matplotlib.pyplot as plt
from itertools import chain, repeat
from pulp import *
import pickle
from utils.auxiliary_plot_library import *


def set_page_query_param(page_name):
    st.experimental_set_query_params(page=page_name)
    
set_page_query_param("resource_management")


if 'client' not in st.session_state:
    st.session_state.client = Client("anchita/proj-trail")
    
def gradient_text(text, color1, color2):
    return f"""
    <span style="
        background: linear-gradient(to right, {color1}, {color2});
        -webkit-background-clip: text;
        color: transparent;
    ">
        {text}
    </span>
    """

color1 = "#0d3270"
color2 = "#0fab7b"
text = "Best Delivery Conditions: Cost and Emission"

styled_text = gradient_text(text, color1, color2)

html_code = f"""
    <div style="background-color: lightblue; border: 2px solid black; padding: 10px; border-radius: 5px;">
        <h3>{styled_text}</h3>
    </div>
"""
st.markdown(html_code, unsafe_allow_html=True)

param_0 = st.selectbox(
    "Origin Port:",
    ["Rotterdam", "Barcelona", "Athens"]
)
param_1 = st.selectbox(
    "Third-party logistics company:",
    ["v_001","v_002","v_003","v_004"]
)

param_2 = st.selectbox(
    "Customs Procedures:",
    ["DTP","DTD","CRF"]
)
param_3 = st.selectbox(
    "Logistic Hub:",
    ["Venlo", "Hamburg", "Duseldorf","Rome","Lille","Warsaw","Bratislava","Leige","Zaragoza",1]
)
param_4 = st.text_input("Customer Location:", "Marseille")
param_5 = st.text_input("Product ID:", "167893")
param_6 = st.number_input("Units:", min_value=0, value=0)
param_7 = st.number_input("Weight:", min_value=0, value=0)
param_8 = st.number_input("Material Handling:", min_value=0, value=0)
param_9 = st.number_input("Weight Class:", min_value=0, value=0)

if st.button("Predict"):
    result = st.session_state.client.predict(
        param_0=param_0,
        param_1=param_1,
        param_2=param_2,
        param_3=param_3,
        param_4=param_4,
        param_5=param_5,
        param_6=param_6,
        param_7=param_7,
        param_8=param_8,
        param_9=param_9,
        api_name="/predict"
    )
 
    prediction_label = result['label']
    prediction_confidence = result['confidences'][0]['confidence']  
    probability_confidence = result['confidences'][1]['confidence']  

    formatted_result = f"Prediction: {prediction_confidence:.1f}, Probability: {probability_confidence:.2f}"

    st.success(formatted_result)
    
st.divider()            
    
color1 = "#0d3270"
color2 = "#0fab7b"
text = "Warehouse Layout Optimization"

styled_text = gradient_text(text, color1, color2)

html_code = f"""
    <div style="background-color: lightblue; border: 2px solid black; padding: 10px; border-radius: 5px;">
        <h3>{styled_text}</h3>
    </div>
"""
st.markdown(html_code, unsafe_allow_html=True)

with open("models/pareto.pkl", "rb") as file:
    model = dill.load(file)
    
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
        try:
            with open("temp_uploaded_file.xlsx", "wb") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
        
            if st.button("Perform Pareto Analysis"):
                model.input_file = "temp_uploaded_file.xlsx"
                
                fig = model.pareto_analysis() 
                
                st.pyplot(fig)

        except Exception as e:
            st.error(f"An error occurred: {e}")
 
st.divider()

color1 = "#0d3270"
color2 = "#0fab7b"
text = "Production Planning"

styled_text = gradient_text(text, color1, color2)

html_code = f"""
    <div style="background-color: lightblue; border: 2px solid black; padding: 10px; border-radius: 5px;">
        <h3>{styled_text}</h3>
    </div>
"""
st.markdown(html_code, unsafe_allow_html=True)

with open("models/prod_plan.pkl", "rb") as file:
    model = dill.load(file)
    
uploaded_file = st.file_uploader("Upload your csv file", type=["csv"])

if uploaded_file:
        try:
            with open("temp_uploaded_file.xlsx", "wb") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
        
            if st.button("Plan production"):
                model.input_file = "temp_uploaded_file.xlsx"
                res = model.production_planning() 
                st.write(res)

        except Exception as e:
            st.error(f"An error occurred: {e}")

st.divider()

color1 = "#0d3270"
color2 = "#0fab7b"
text = "Weekly Worker-Demand Planning"

styled_text = gradient_text(text, color1, color2)

html_code = f"""
    <div style="background-color: lightblue; border: 2px solid black; padding: 10px; border-radius: 5px;">
        <h3>{styled_text}</h3>
    </div>
"""
st.markdown(html_code, unsafe_allow_html=True)

with open("models/workers.pkl", "rb") as file:
    model = dill.load(file)
    
workers_input = st.text_input(
    "Enter the workers list (comma-separated):",
    placeholder="e.g., 5, 6, 7, 8, 5, 4, 3"
)

if workers_input:
        try:
            worker_default = [int(x.strip()) for x in workers_input.split(",")]
            if len(worker_default) != 7:
                st.error("Please enter exactly 7 values (one for each day of the week).")
            elif st.button("Plan worker-demand "):
                model.workers = worker_default
                res = model.workers_planning()
                
                st.pyplot(res)
        except ValueError:
            st.error("Invalid input. Please enter integers separated by commas.")
            
st.divider()

color1 = "#0d3270"
color2 = "#0fab7b"
text = "Inventory Planning"

styled_text = gradient_text(text, color1, color2)

html_code = f"""
    <div style="background-color: lightblue; border: 2px solid black; padding: 10px; border-radius: 5px;">
        <h3>{styled_text}</h3>
    </div>
"""
st.markdown(html_code, unsafe_allow_html=True)

file=st.file_uploader("Upload a CSV file", type=["csv"])

if file is not None:
    df = pd.read_csv(file)
    df = df.sort_values(by=["date"])
    
    st.subheader("Select Date Interval")
    first_date = pd.to_datetime(df.iloc[0]["date"])
    last_date = pd.to_datetime(df.iloc[-1]["date"])
    start_date = st.date_input("Start date", first_date, min_value=first_date)
    end_date = st.date_input("End date", last_date, max_value=last_date)

    # Success/error
    success1 = False
    if start_date < end_date:
        success1 = True
        st.success("Start date: `%s`\n\nEnd date: `%s`" % (start_date, end_date))
    else:
        success1 = False
        st.error("Error: End date must be greater than start date.")


    # Select Product
    st.subheader("Select product number")
    num_prod = st.selectbox(
        "Select Product",
        df["product_number"].unique(),
    )

    with open("models/all_plots2.pkl", "rb") as f:
        dictionary_plots = pickle.load(f)

    with open("models/x_plot2.pkl", "rb") as g:
        x = pickle.load(g)

    if st.button("Planning graph"):
        if success1:
            df_plan = plot_planning_graphic(
                start_date, end_date, x, dictionary_plots, num_prod
            )
            download_data_plot(df_plan)
        else:
            st.error("There are errors in previous fields")
else:
    st.warning("Please upload a CSV file")
    
footer="""<style>

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed by <a style='display: inline; text-align: center;' href="https://www.linkedin.com/in/harshavardhan-bajoria/" target="_blank">Team SAARTHA</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
