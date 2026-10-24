# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained machine learning model (the full pipeline, including the preprocessing step)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the same order as used in training
feature_columns = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Define a route for the home page (GET request)
@superkart_api.get("/")
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the SuperKart Sales Prediction API!"


# Define an endpoint for single product-store prediction (POST request)
@superkart_api.post("/v1/predict")
def predict_sales():
    """
    This function handles POST requests to the '/v1/predict' endpoint.
    It expects a JSON payload containing the product and store details
    and returns the predicted sales as a JSON response.
    """
    # Get the JSON data from the request body
    sales_data = request.get_json()

    # Check that all the required features are present
    missing = [col for col in feature_columns if col not in sales_data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Convert the extracted data into a one-row Pandas DataFrame
    input_data = pd.DataFrame([{col: sales_data[col] for col in feature_columns}])

    # Make the prediction using the trained model
    predicted_sales = model.predict(input_data)[0]

    # Convert the predicted value to a Python float rounded to 2 decimals
    predicted_sales = round(float(predicted_sales), 2)

    # Return the prediction as a JSON response
    return jsonify({"Predicted Sales": predicted_sales})


# Define an endpoint for batch prediction (POST request)
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """
    This function handles POST requests to the '/v1/predictbatch' endpoint.
    It expects a CSV file containing the product and store details for multiple rows
    and returns the predicted sales as a dictionary in the JSON response.
    """
    # Get the uploaded CSV file from the request
    file = request.files["file"]

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Check that all the required features are present
    missing = [col for col in feature_columns if col not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Make predictions for all the rows in the DataFrame
    predicted_sales = model.predict(input_data[feature_columns])

    # Create a dictionary of predictions with the row index as the key
    output_dict = {str(idx): round(float(pred), 2) for idx, pred in zip(input_data.index, predicted_sales)}

    # Return the predictions dictionary as a JSON response
    return jsonify(output_dict)


# Run the Flask application in debug mode if this script is executed directly
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=True)
