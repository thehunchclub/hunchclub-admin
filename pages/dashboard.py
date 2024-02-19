import streamlit as st
from core.utils import init, server_request
from loguru import logger as log

from core.vars import DEBUG

@st.cache_resource(ttl=60 if not DEBUG else 5)
def get_dashboard():
    """
    Returns dashboard metrics.
    """
    try:
        res = server_request("admin/dashboard")
        # print(res.status_code, res.text)
        if res.status_code == 200:
            data = res.json()
            return data.get('data', [])
        else:
            st.error(f"Error fetching data: {res.status_code} {res.text}")
        
    except Exception as e:
        log.error(e)
        st.error(str(e))
        
    return None


def dashboard():
    
    init()
    
    st.header("Dashboard")

    st.success("Server is Online", icon="✅")
    
    data = get_dashboard()
    
    if data:
        # Expecting a dict of dicts
        for key, value in data.items():
            if key != "config": continue
            st.subheader(key, divider=True)
            # c1,c2,c3 = st.columns(3)
            for k, v in value.items():
                st.metric(k, v)
                # st.write(f"{k}: {v}")
            # st.write(value)


if __name__ == "__main__":
    
    dashboard()

