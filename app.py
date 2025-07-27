import streamlit as st
import json
import os
from blockchain import Blockchain
from landchain_utils import *
import folium
from streamlit_folium import st_folium

# --- App Configuration ---
st.set_page_config(
    page_title="LandChain - Tamper-Proof Land Registry",
    layout="wide",
)

# --- Load/Save Blockchain ---
def load_chain():
    if os.path.exists("data/land_records.json"):
        with open("data/land_records.json", "r") as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
    return []

def save_chain(chain):
    with open("data/land_records.json", "w") as f:
        json.dump(chain, f, indent=4)

# --- Login Function ---
def login():
    st.title("🔐 LandChain Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if validate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = get_user_role(username)
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid credentials")

# --- Register Land ---
def register_land():
    st.header("📋 Register New Land")
    location = st.text_input("Location")
    area = st.number_input("Area (sq.ft)", step=1.0)
    land_id = st.text_input("Unique Land ID")
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")

    if st.button("Register Land"):
        chain = load_chain()
        data = {
            "land_id": land_id,
            "location": location,
            "area": area,
            "latitude": lat,
            "longitude": lon,
            "owner": st.session_state.role,
            "registered_by": st.session_state.user,
            "gst_paid": False
        }
        chain.append({"data": data})
        save_chain(chain)
        st.success("✅ Land registered successfully.")

# --- View All Lands ---
def view_all_lands():
    st.header("📜 All Registered Lands")
    chain = load_chain()
    for block in chain:
        st.json(block["data"])

# --- Map View ---
def view_land_map():
    st.header("🌍 Land Locations on Map")
    chain = load_chain()
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    for block in chain:
        data = block["data"]
        if "latitude" in data and "longitude" in data:
            popup_text = f"ID: {data['land_id']}<br>Owner: {data['owner']}<br>Area: {data['area']} sq.ft"
            folium.Marker([data["latitude"], data["longitude"]], popup=popup_text).add_to(m)
    st_folium(m, width=800, height=500)

# --- Request Land Transfer ---
def request_transfer():
    st.header("🔄 Request Land Transfer")
    land_id = st.text_input("Land ID")
    if st.button("Request Transfer"):
        add_transfer_request(land_id, st.session_state.role)
        st.success("Transfer request sent.")

# --- Approve Requests ---
def approve_requests():
    st.header("✅ Approve Transfer Requests")
    requests = get_transfer_requests_for_owner(st.session_state.role)
    for req in requests:
        st.write(f"Request from {req['from']} for Land ID: {req['land_id']}")
        if st.button(f"Approve {req['land_id']}"):
            approve_transfer(req['land_id'])
            st.success("Request approved.")

# --- Pay GST ---
def pay_gst():
    st.header("💰 Pay GST Before Ownership Change")
    land_id = st.text_input("Land ID")
    if st.button("Pay GST"):
        if mark_gst_paid(land_id):
            st.success("GST paid successfully.")
        else:
            st.error("Invalid or already paid.")

# --- Routing Logic ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("🏠 Dashboard")
    choice = st.sidebar.radio("Choose Action", [
        "Register Land",
        "View All Lands",
        "View Land Map",
        "Request Land Transfer",
        "Approve Requests",
        "Pay GST",
        "Logout"
    ])

    if choice == "Register Land":
        register_land()
    elif choice == "View All Lands":
        view_all_lands()
    elif choice == "View Land Map":
        view_land_map()
    elif choice == "Request Land Transfer":
        request_transfer()
    elif choice == "Approve Requests":
        approve_requests()
    elif choice == "Pay GST":
        pay_gst()
    elif choice == "Logout":
        st.session_state.logged_in = False
        st.rerun()
