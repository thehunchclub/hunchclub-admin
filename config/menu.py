import streamlit as st

def sidebar_menu():
    
    
    st.sidebar.subheader("Menu")
    st.sidebar.page_link("pages/dashboard.py", label="Dashboard", icon="🏠")
    # st.sidebar.page_link("pages/modules.py", label="Modules", icon="🔌")
    # st.sidebar.page_link("pages/cron.py", label="Cron Jobs", icon="🕒")
    # st.sidebar.page_link("pages/api_keys.py", label="API Keys", icon="🔑")
    
    # st.sidebar.subheader("Hunch Club")
    st.sidebar.page_link("pages/hunch_club_tips.py", label="Tips", icon="🎟️")
    st.sidebar.page_link("pages/hunch_club_platforms.py", label="Publish", icon="📬")


    
    