import os
import requests
import pandas as pd
import streamlit as st

# URL of the Flask backend
# Inside the Docker network, the frontend reaches the backend by its container name;
# it can be overridden with the BACKEND_URL environment variable
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

# Product types grouped as perishables (all others are non perishables), same as in training
PERISHABLES = ["Dairy", "Meat", "Fruits and Vegetables", "Breakfast", "Breads", "Seafood"]
PRODUCT_TYPES = [
    "Baking Goods", "Breads", "Breakfast", "Canned", "Dairy", "Frozen Foods", "Fruits and Vegetables", "Hard Drinks",
    "Health and Hygiene", "Household", "Meat", "Others", "Seafood", "Snack Foods", "Soft Drinks", "Starchy Foods",
]

# Set the title and description of the app
st.title("SuperKart Sales Prediction App")
st.write("This app predicts the total sales revenue of a product in a SuperKart store.")

# Section for online (single) prediction
st.subheader("Online Prediction")

# Collect the product details from the user
st.markdown("**Product details**")
product_id_char = st.selectbox(
    "Product Code (first two letters of the Product Id)",
    ["FD", "DR", "NC"],
    help="FD = Food, DR = Drinks, NC = Non-Consumables",
)
product_type = st.selectbox("Product Type", PRODUCT_TYPES, index=PRODUCT_TYPES.index("Frozen Foods"))
product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
product_allocated_area = st.number_input(
    "Product Allocated Area (ratio of display area)", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f"
)
product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=0.01)

# Collect the store details from the user
st.markdown("**Store details**")
store_size = st.selectbox("Store Size", ["Small", "Medium", "High"], index=1)
store_location_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
store_type = st.selectbox(
    "Store Type", ["Departmental Store", "Food Mart", "Supermarket Type1", "Supermarket Type2"], index=3
)
store_establishment_year = st.number_input("Store Establishment Year", min_value=1950, max_value=2025, value=2009, step=1)

# Convert the user input into the features expected by the model
input_data = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar_content,
    "Product_Allocated_Area": product_allocated_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_location_city_type,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": 2025 - int(store_establishment_year),
    "Product_Type_Category": "Perishables" if product_type in PERISHABLES else "Non Perishables",
}

# Send the input to the backend and display the prediction when the button is clicked
if st.button("Predict"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=input_data, timeout=30)
        if response.status_code == 200:
            prediction = response.json()["Predicted Sales"]
            st.success(f"Predicted Product Store Sales Total: {prediction:,.2f}")
        else:
            st.error(f"Error making prediction (status {response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the backend at {BACKEND_URL}: {e}")

# Section for batch prediction
st.subheader("Batch Prediction")
st.write(
    "Upload a CSV file with the columns: " + ", ".join(f"`{col}`" for col in input_data.keys())
)

# Allow the user to upload a CSV file for batch prediction
uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

# Send the file to the backend and display the predictions when the button is clicked
if uploaded_file is not None:
    if st.button("Predict Batch"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                timeout=60,
            )
            if response.status_code == 200:
                predictions = response.json()

                # Show the uploaded data along with the predicted sales
                batch_data = pd.read_csv(uploaded_file)
                batch_data["Predicted_Sales"] = [predictions[str(idx)] for idx in batch_data.index]
                st.success("Batch predictions completed!")
                st.dataframe(batch_data)
            else:
                st.error(f"Error making batch prediction (status {response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the backend at {BACKEND_URL}: {e}")
