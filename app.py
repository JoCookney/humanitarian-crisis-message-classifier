# Import the libraries needed by the application
import streamlit as st
import joblib
from pathlib import Path


# Configure the browser tab
st.set_page_config(
    page_title="Humanitarian Crisis Message Classifier",
    page_icon="🌍"
)


# Locate and load the trained model
MODEL_PATH = Path(__file__).parent / "humanitarian_classifier.joblib"
model = joblib.load(MODEL_PATH)


# Display the application title
st.title("Humanitarian Crisis Message Classifier")

# Display a short description
st.write(
    "Classify disaster-related messages into humanitarian information categories."
)


# Text box where the user can enter a crisis message
message = st.text_area(
    "Enter a crisis-related message:",
    placeholder="Example: Families urgently need food, water and medical assistance."
)


# Classify the message when the user clicks the button
if st.button("Classify Message"):

    if message.strip():
        prediction = model.predict([message])[0]

        st.write("Predicted category:")
        st.success(prediction)

    else:
        st.warning("Please enter a message before classification.")