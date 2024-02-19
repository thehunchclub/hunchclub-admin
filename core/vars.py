import os
import streamlit as st
# Load dotenv
from dotenv import load_dotenv
load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"), 
    override=True
)

SERVER_ADDRESS = st.secrets["API_SERVER_ADDRESS"].strip("/")
DEBUG = str(st.secrets["DEBUG"]).lower() == "true"
BASEPATH = os.getcwd() #os.path.dirname(os.path.abspath(__file__))
API_TOKEN = st.secrets["API_TOKEN"]
