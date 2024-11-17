import streamlit as st
from amplpy import AMPL
import os
from utils.dataOptimize import InputData
from utils.reports import Reports
from utils.model import ModelBuilder


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
def set_page_query_param(page_name):
    st.experimental_set_query_params(page=page_name)
set_page_query_param("supply_chain")

color1 = "#C71585"
color2 = "#FF69B4"
text = "Supply Chain Optimization"

styled_text = gradient_text(text, color1, color2)

html_code = f"""
    <div style="background-color: #FFC0CB; border: 2px solid black; padding: 10px; border-radius: 5px;">
        <h3>{styled_text}</h3>
    </div>
"""
st.markdown(html_code, unsafe_allow_html=True)

def require_rerun():        
        st.session_state["needs_rerun"] = True
        
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")


if uploaded_file is not None:
        # Ensure the temp directory exists
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

options = [
    "Category 1: Demand Balance + Inventory Carryover + Material Balance",
    "Category 2: Production Hours + Resource Capacity + Transfers + Target Stocks + Storage Capacity",
]

if uploaded_file is not None:
    st.write("You have uploaded the following file:")
    # Get the query parameters
    query_params = st.experimental_get_query_params()

    if "Category" not in query_params or not query_params["Category"]:
        st.experimental_set_query_params(Category=2)

# Get the default option based on the query parameter
    if "Category" in query_params and query_params["Category"]:
        default_option = max(0, int(query_params["Category"][0]) - 1)
    else:
        default_option = 1  # Default to Category 2 if not set

    def update_params():
        if "Category" in st.session_state:
        # Update the query parameters with the selected Category option
            st.experimental_set_query_params(Category=options.index(st.session_state["Category"]) + 1)

    class_number = (
        options.index(
        st.selectbox(
            "Production Optimization Class",
            options,
            key="Category",
            index=default_option,
            on_change=update_params,
        )
    )
    + 1
    )

    st.session_state.instance = InputData(
        temp_file_path,
        class_number,
        on_change=require_rerun,
    )

    instance = st.session_state.instance

    st.session_state.mb = ModelBuilder(
        class_number,
        on_change=require_rerun,
    )

    mb = st.session_state.mb

    ampl = AMPL()
    ampl.eval(mb.model)

    st.markdown("## Filters")

    with st.expander("Dimensions"):
        instance.filter_dimensions()

    with st.expander("Data"):
        instance.edit_data()


    demand = instance.demand[["Product", "Location", "Period", "Quantity"]].copy()
    starting_inventory = instance.starting_inventory[
        ["Product", "Location", "Quantity"]
    ].copy()
    demand["Period"] = demand["Period"].dt.strftime("%Y-%m-%d")
    periods = list(sorted(set(demand["Period"])))
    demand.set_index(["Product", "Location", "Period"], inplace=True)
    starting_inventory.set_index(["Product", "Location"], inplace=True)

    ampl.set["PRODUCTS"] = instance.selected_products
    ampl.set["LOCATIONS"] = instance.selected_locations
    ampl.set["PRODUCTS_LOCATIONS"] = instance.products_locations
    ampl.set["PERIODS"] = periods
    ampl.param["Demand"] = demand["Quantity"]
    ampl.param["InitialInventory"] = starting_inventory["Quantity"]


    if class_number >= 2:
            ampl.set["RESOURCES"] = instance.all_resources
            ampl.param["ProductionRate"] = instance.production_rate.set_index(
                ["Product", "Location", "Resource"]
            )[["Rate"]]
            ampl.param["AvailableCapacity"] = instance.available_capacity.set_index(
                ["Resource", "Location"]
            )
            ampl.set["TRANSFER_LANES"] = list(
                instance.transfer_lanes.itertuples(index=False, name=None)
            )
            ampl.param["TargetStock"] = instance.target_stocks.set_index(
                ["Product", "Location"]
            )
            ampl.param["MaxCapacity"] = instance.location_capacity.set_index(["Location"])

    with st.expander("Adjust objective penalties"):
            col1, col2 = st.columns(2)
            with col1:
                ampl.param["UnmetDemandPenalty"] = st.slider(
                    "UnmetDemandPenalty:",
                    min_value=0,
                    max_value=50,
                    value=10,
                    on_change=require_rerun,
                )

            with col2:
                ampl.param["EndingInventoryPenalty"] = st.slider(
                    "EndingInventoryPenalty:",
                    min_value=0,
                    max_value=50,
                    value=5,
                    on_change=require_rerun,
                )

            if class_number >= 2:
                with col1:
                    ampl.param["AboveTargetPenalty"] = st.slider(
                        "AboveTargetPenalty:",
                        min_value=0,
                        max_value=50,
                        value=2,
                        on_change=require_rerun,
                    )

                with col2:
                    ampl.param["BelowTargetPenalty"] = st.slider(
                        "BelowTargetPenalty:",
                        min_value=0,
                        max_value=50,
                        value=3,
                        on_change=require_rerun,
                    )

                with col1:
                    ampl.param["TransferPenalty"] = st.slider(
                        "TransferPenalty:",
                        min_value=0,
                        max_value=50,
                        value=1,
                        on_change=require_rerun,
                    )

    auto_rerun = st.checkbox(
            "Automatically rerun to update the results", value=True
        )

    if (
            auto_rerun
            or not st.session_state.get("needs_rerun", False)
            or st.button("Rerun to update the results", type="primary")
        ):
            st.session_state["needs_rerun"] = False
            # Solve the problem
            ampl.solve(solver="gurobi", mp_options="outlev=1", return_output=True)

            if ampl.solve_result == "solved":
                ampl.option["display_width"] = 1000
                model = ampl.export_model()
                model = model[: model.find("###model-end")] + "###model-end"
                
                
                # Reports
                st.markdown("## Reports")
                reports = Reports(instance, ampl)

                st.markdown("### Demand Report")
                reports.demand_report()

                st.markdown("### Material Balance Report")
                reports.material_balance_report(include_target_stock=class_number >= 2)

                if class_number >= 2:
                    st.markdown("### Resource Utilization Report")
                    reports.resource_utilization_report()

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