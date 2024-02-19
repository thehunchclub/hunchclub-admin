import os
import streamlit as st

SERVER_ADDRESS = st.secrets["API_SERVER_ADDRESS"].strip("/")
DEBUG = str(st.secrets["DEBUG"]).lower() == "true"
BASEPATH = os.getcwd() #os.path.dirname(os.path.abspath(__file__))
API_TOKEN = st.secrets["API_TOKEN"]
