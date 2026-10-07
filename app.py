# ============================================================
# Humanitarian Crisis Message Triage Prototype
# Stage 4: Sender Interface + V1 Classification + Triage Layer
# ============================================================

import streamlit as st
import joblib
import requests
from pathlib import Path


# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Humanitarian Crisis Message System",
    page_icon="🌍"
)


# ------------------------------------------------------------
# Load trained V1 model
# ------------------------------------------------------------

MODEL_PATH = Path(__file__).parent / "humanitarian_classifier.joblib"
model = joblib.load(MODEL_PATH)


# ------------------------------------------------------------
# Supabase configuration
# ------------------------------------------------------------

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

MESSAGES_ENDPOINT = f"{SUPABASE_URL}/rest/v1/Messages"


# ------------------------------------------------------------
# Prototype triage rules
# ------------------------------------------------------------

def apply_triage_rules(message):
    """
    Apply transparent prototype heuristics to identify messages
    that may require faster human attention.

    These rules are NOT a validated emergency-response system.
    They are deliberately simple and auditable safeguards added
    on top of the V1 machine-learning classifier.
    """

    text = message.lower()

    # Signals suggesting potentially immediate danger
    high_priority_signals = [
        "trapped",
        "can't get out",
        "cannot get out",
        "rising water",
        "water is rising",
        "bleeding",
        "unconscious",
        "not breathing",
        "collapsed",
        "collapse",
        "buried",
        "drowning",
        "fire spreading",
    ]

    # Signals suggesting significant humanitarian need
    medium_priority_signals = [
        "injured",
        "medical help",
        "medicine",
        "no food",
        "need food",
        "no water",
        "need water",
        "missing",
        "disappeared",
        "evacuate",
        "evacuation",
    ]

    if any(signal in text for signal in high_priority_signals):
        priority = "High"
        review_required = True

    elif any(signal in text for signal in medium_priority_signals):
        priority = "Medium"
        review_required = True

    else:
        priority = "Standard"
        review_required = False

    return priority, review_required


# ------------------------------------------------------------
# Sender interface
# ------------------------------------------------------------

st.title("Humanitarian Crisis Message System")
st.subheader("Send a Crisis Message")

st.warning(
    "RESEARCH PROTOTYPE — TESTING ONLY. "
    "This is not an emergency service and is not monitored by "
    "emergency responders. Do not submit real emergencies or "
    "sensitive personal information. Please use fictional or "
    "simulated crisis messages for testing."
)

st.write(
    "Describe what is happening and what help may be needed. "
    "Your message will be analysed to help responders organise "
    "incoming information."
)

message = st.text_area(
    "Your message:",
    placeholder=(
        "Example: My family is trapped upstairs and "
        "the flood water is still rising."
    ),
    height=150
)


# ------------------------------------------------------------
# Submit message
# ------------------------------------------------------------

if st.button("Send Message", type="primary"):

    if message.strip():

        clean_message = message.strip()

        # Step 1: Run the trained V1 classifier
        prediction = model.predict([clean_message])[0]

        # Step 2: Apply transparent prototype triage rules
        priority, review_required = apply_triage_rules(
            clean_message
        )

        # Step 3: Construct the database record
        message_record = {
            "message": clean_message,
            "v1_category": prediction,
            "priority": priority,
            "review_required": review_required,
            "status": "New"
        }

        # Step 4: Send the record to Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                MESSAGES_ENDPOINT,
                headers=headers,
                json=message_record,
                timeout=10
            )

            response.raise_for_status()

            st.success("Test message received.")

            st.write(
                "Thank you. Your test message has been submitted "
                "to the research prototype."
            )

        except requests.RequestException:
            st.error(
                "The test message could not be submitted. "
                "Please try again."
            )

    else:
        st.warning("Please enter a test message before sending.")