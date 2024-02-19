import streamlit as st
# from core.utils import init

# Force remove default page navigation
st.config.set_option('client.showSidebarNavigation', False)

# from corepages.dashboard import dashboard


if __name__ == "__main__":
    # import os
    # from rich import print
    # print(os.environ)
    st.switch_page("pages/dashboard.py")
    # dashboard()
    
