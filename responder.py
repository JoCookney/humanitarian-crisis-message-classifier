# ============================================================
# Humanitarian Crisis Message Triage Prototype
# Stage 4: Password-Protected Responder Dashboard
# ============================================================

import streamlit as st
import requests
import hmac


# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Humanitarian Responder Dashboard",
    page_icon="🚨",
    layout="wide"
)


# ------------------------------------------------------------
# Authentication
# ------------------------------------------------------------

def check_password():
    """
    Require the responder password before allowing access
    to the dashboard.

    The real password is stored in Streamlit Secrets and is
    never written directly into this source-code file.
    """

    # Remember successful authentication during this session
    if st.session_state.get("authenticated", False):
        return True

    st.title("Humanitarian Responder Dashboard")
    st.subheader("Responder Login")

    st.write(
        "This dashboard is restricted to authorised responders."
    )

    entered_password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Log in"):

        correct_password = st.secrets["responder"]["password"]

        if hmac.compare_digest(
            entered_password,
            correct_password
        ):
            st.session_state["authenticated"] = True
            st.rerun()

        else:
            st.error("Incorrect password.")

    return False


# Stop here unless authentication succeeds
if not check_password():
    st.stop()


# ------------------------------------------------------------
# Supabase configuration
# ------------------------------------------------------------

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

MESSAGES_ENDPOINT = f"{SUPABASE_URL}/rest/v1/Messages"


# ------------------------------------------------------------
# Authenticated dashboard
# ------------------------------------------------------------

st.title("Humanitarian Responder Dashboard")

st.success("Authenticated responder session")

st.warning(
    "RESEARCH PROTOTYPE — TESTING ONLY. "
    "This dashboard contains synthetic test messages and is not "
    "connected to emergency services."
)

st.write(
    "Incoming crisis messages submitted through the sender interface. "
    "Machine-learning classifications and prototype triage indicators "
    "are decision-support information only and require human oversight."
)


# ------------------------------------------------------------
# Logout
# ------------------------------------------------------------

if st.button("Log out"):
    st.session_state["authenticated"] = False
    st.rerun()


# ------------------------------------------------------------
# Retrieve messages from Supabase
# ------------------------------------------------------------

headers = {
    "apikey": SUPABASE_KEY
}

try:
    response = requests.get(
        MESSAGES_ENDPOINT,
        headers=headers,
        params={
            "select": (
                "id,created_at,message,v1_category,status,"
                "priority,review_required"
            ),
            "order": "created_at.desc"
        },
        timeout=10
    )

    response.raise_for_status()

    messages = response.json()

    # --------------------------------------------------------
    # Dashboard summary
    # --------------------------------------------------------

    if messages:

        high_count = sum(
            record["priority"] == "High"
            for record in messages
        )

        medium_count = sum(
            record["priority"] == "Medium"
            for record in messages
        )

        review_count = sum(
            record["review_required"] is True
            for record in messages
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Messages", len(messages))
        col2.metric("High Priority", high_count)
        col3.metric("Medium Priority", medium_count)
        col4.metric("Require Review", review_count)

        st.divider()

        # ----------------------------------------------------
        # Display individual messages
        # ----------------------------------------------------

        st.subheader("Incoming Messages")

        for record in messages:

            with st.container(border=True):

                if record["priority"] == "High":
                    st.error("🔴 HIGH PRIORITY")

                elif record["priority"] == "Medium":
                    st.warning("🟠 MEDIUM PRIORITY")

                else:
                    st.info("STANDARD PRIORITY")

                st.write(
                    f"**Message:** {record['message']}"
                )

                st.write(
                    f"**V1 ML Category:** "
                    f"{record['v1_category']}"
                )

                st.write(
                    f"**Human Review Required:** "
                    f"{record['review_required']}"
                )

                st.write(
                    f"**Status:** {record['status']}"
                )

                st.caption(
                    f"Message ID: {record['id']} | "
                    f"Received: {record['created_at']}"
                )

    else:
        st.info("No messages have been received yet.")

except requests.RequestException:
    st.error(
        "The responder dashboard could not retrieve messages "
        "from the database."
    )