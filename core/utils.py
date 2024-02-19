# from dotenv import load_dotenv
# load_dotenv()
import streamlit as st
# from rich import print
import datetime
import os
import requests
from time import sleep
from loguru import logger as log
from importlib import import_module
from dotenv import load_dotenv
import random

# Custom imports
from core.vars import SERVER_ADDRESS, DEBUG, API_TOKEN
from config.menu import sidebar_menu


def to_snake_case(snake_case_string:str):
    words = snake_case_string.split('_')
    return ' '.join(word.capitalize() for word in words)

@st.cache_resource(ttl=60)
def ping_server():
    try:
        response = requests.get(SERVER_ADDRESS + "/common/ping")
        if response.status_code != 200:
            raise Exception("Server not available at " + SERVER_ADDRESS)
        return True
    except Exception as e:
        log.error(e)
    return False

def init():
    
    load_dotenv(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"), 
        override=True
    )
    
    # Force remove default page navigation
    st.config.set_option('client.showSidebarNavigation', False)
    
    # print(dir(st)) # Streamlit methods

    try:
        st.set_page_config(
            page_title="SERVER ADMIN", 
            page_icon=":construction_worker:", 
            # initial_sidebar_state="collapsed", 
            menu_items=app_default_menu()
        )
    except:
        # print("Failed to set page config")
        pass
        
    if not ping_server():
        st.error("Server is Offline at " + SERVER_ADDRESS, icon="🚨")
        ping_server.clear()
        st.stop()
    
    if DEBUG:
        with st.expander("Debug"):
            st.subheader("Session State")
            st.write(st.session_state)

    
    # If not authenticated, show login page
    if not super_admin_authenticated(): 
        # Show login page
        st.success("Server is Online at " + SERVER_ADDRESS, icon="✅")
        show_super_admin_login()
        st.stop()

    # print(os.getcwd())
    # Show sidebar menu
    sidebar_menu()
    
    
    st.sidebar.divider()
    st.sidebar.markdown(f'### {str(datetime.datetime.utcnow().strftime("%Y-%m-%d, %H:%M"))}')
    st.sidebar.markdown("`Environment: " + str(get_env()).upper() + "`")
    
    
def footer():


    if DEBUG:
        with st.expander("Debug"):
            st.subheader("Session State")
            st.write(st.session_state)

    
@st.cache_resource(ttl=60 if not DEBUG else 5)
def get_env():
    """
    Returns dashboard metrics.
    """
    try:
        res = server_request("admin/dashboard")
        # print(res.status_code, res.text)
        if res.status_code == 200:
            data = res.json()
            return data.get('data', [])['config']['environment']
        else:
            st.error(f"Error fetching data: {res.status_code} {res.text}")
        
    except Exception as e:
        log.error(e)
        return "Unknown"
        
    return "Unknown"
        
        
def server_request(endpoint, method="GET", data=None, headers=None, params=None, api_key=None):
    
    try:
        
        endpoint = endpoint.strip("/")
        
        if not api_key: api_key = API_TOKEN
        method = method.upper()
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        if method == "GET":
            res = requests.get(f"{SERVER_ADDRESS}/{endpoint}", headers=headers)
        elif method == "POST":
            res = requests.post(f"{SERVER_ADDRESS}/{endpoint}", headers=headers, json=data)
        elif method == "PUT":
            res = requests.put(f"{SERVER_ADDRESS}/{endpoint}", headers=headers, json=data)
        elif method == "DELETE":
            res = requests.delete(f"{SERVER_ADDRESS}/{endpoint}", headers=headers, json=data)
        elif method == "PATCH":
            res = requests.patch(f"{SERVER_ADDRESS}/{endpoint}", headers=headers, json=data)
        else:
            raise Exception("Invalid method")
        return res
    
    except Exception as e:
        log.error(e)
    
    return None


def app_default_menu():
    return {
        "About":"Admin Dashboard for managing a FastAPI REST API Server."
    }

def super_admin_authenticated(access_token=None):
    
    _ac = None
    # Check if user is already authenticated
    if not access_token:
        if st.session_state.get('super_admin', None) and st.session_state.get('access_token', None):
            return True
        # Check URL and Cookie for access_token
        if 'pw' in st.query_params:
            _ac = st.query_params['pw']
    
    # Manual check
    if access_token: 
        _ac = access_token
    
    if _ac:
        
        if _ac == st.secrets["APP_PASSWORD"]:
            st.session_state['super_admin'] = True
            # st.session_state['access_token'] = _ac
            
        # try:
        #     res = requests.get(SERVER_ADDRESS + "/admin/token/verify", params={
        #         "access_token": _ac
        #     })
        #     if res.status_code != 200:
        #         raise Exception("Invalid token")
        #     st.session_state['super_admin'] = True
        #     st.session_state['access_token'] = _ac
            
        # except Exception as e:
        #     log.error(e)
    
    if st.session_state.get('super_admin', None):
        return True
    
    return False

def show_super_admin_login():
    ## Show login page
    id, data, action = process_form_submission()
    if id == "login_form" and action == "login":
        # st.write(data)
        # st.write(st.session_state)
        if 'password' in data:
            if super_admin_authenticated(data['password']):
                st.success("Logged in!", icon="✅")
                sleep(1)
                st.rerun()
            else:
                st.error("Invalid", icon="🚨")
        
    with st.form(key="login_form"):
        st.write("Login")
        password = st.text_input("Password", type="password", key="password_login_form")
        st.form_submit_button("Login")
    
    
def process_form_submission():
    # Form submission should be in the format: "FormSubmitter:{module_id}-{action}"
    # Form fields should have a unique key value, and be in the format : "field_{module_id}"
    # The 'action' is the name in lowercase of the button that was clicked.
    
    id = data = action = None
    # Process form changes and save the data to the database
    _ss = st.session_state
    for k,v in _ss.items():
        if k.startswith("FormSubmitter:") and v: # Form submitted = True
            id = k.split(":")[1].split("-")[0]
            action = k.split(":")[1].split("-")[1].lower()
            # print("FORM SUBMITTED", module_id)
            form_data = {k.replace(f"_{id}",""): v for k,v in _ss.items() if id in k and "FormSubmitter" not in k}
            form_data2 = {}
            for key, value in form_data.items():
                # print("FORM FIELD", key, repr(value))
                if '[' in key: # we have a list of items
                    if key.split("[")[0] not in form_data2:
                        form_data2[key.split("[")[0]] = []
                    pass
                    
                elif "+" in key:
                    key = key.split("+")
                    _result = {}
                    current_level = _result
                    for _i, _k in enumerate(key):
                        # print(_i, _k, value, current_level)
                        if _k not in current_level:
                            current_level[_k] = {}
                        if _i == len(key)-1:
                            current_level[_k] = value
                        current_level = current_level[_k]
                    # print("FINAL RESULT", type(_result), _result)
                        # _result = _result[_k]
                    # Merge _last to form_data2
                    # form_data2 = {**form_data2, **_result}
                    merge_dicts(form_data2, _result)
                    
                    # if key[0] not in form_data2:
                    #     form_data2[key[0]] = {}
                    # form_data2[key[0]][key[1]] = value
                else:
                    form_data2[key] = value
            
            data = form_data2
    # print("FORM DATA", id, action, data, repr(data))
    return id, data, action

def merge_dicts(d1, d2):
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            merge_dicts(d1[key], d2[key])
        else:
            d1[key] = d2[key]
            
def filter_dict(data, filter_substrings, exclude=True):
    if isinstance(filter_substrings, str):
        filter_substrings = [filter_substrings]

    new_dict = {}
    for key, value in data.items():
        if any(substring in key for substring in filter_substrings):
            match = True
        else:
            match = False
            
            
        if (exclude and not match) or (not exclude and match):
            if isinstance(value, dict):
                new_dict[key] = filter_dict(value, filter_substrings, exclude)
            else:
                new_dict[key] = value
        elif not exclude and isinstance(value, dict):
            new_dict[key] = filter_dict(value, filter_substrings, exclude)
            
    return new_dict

def recursive_walk(data, callback):
    for key, value in data.items():
        if isinstance(value, dict):
            recursive_walk(value, callback)
        else:
            data[key] = callback(value)

def encode_datetimes_for_db(value):
    # Basic encoding of main problematic types
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    elif isinstance(value, datetime.time):
        return value.strftime("%H:%M")
    else:
        return value


def create_form_element(form, label=None, value=None, key=None, help=None, disabled=False, use_columns=False, show_label=True, options=[], field=None):
    
    # if 'time' in label: print(key, label,use_columns, show_label, type(value))
    
    _label_visibility = 'visible' if label else 'collapsed'
    if not label: label = "-"
    _type = "password" if label and any(x in label.lower() for x in ['api','token','password']) else "default"
    if field == "password": _type = "password"
    if label.lower().strip() in ["id","_id"]:
        disabled = True
        key = None
    label = to_snake_case(label)
    if not show_label: 
        _label_visibility = "collapsed"
        label = "-"
    # if options and not isinstance(value, list):
    #     value = [value]
    if disabled:
        key = random.randint(1,999999)
        
    def col_split(label, value, key=None):
        c1, c2 = form.columns(2)
        # print(label, value, help)
        with c1:
            # form.text_input(label, label, key= random.randint(1,999999), label_visibility="collapsed", type="default", disabled=True)
            form.write(label)
        with c2:
            create_form_element(form, label, value, key=key, help=help, disabled=disabled, show_label=False, options=options, field=field)
            if help: form.caption(help)
        
    if isinstance(value, bool):
        if use_columns:
            col_split(label, value, key)
        else:
            form.toggle(label, value=value, key=key, help=help, label_visibility=_label_visibility, disabled=disabled)
    elif isinstance(value, float) or isinstance(value, int):
        if use_columns:
            col_split(label, value, key)
        else:
            form.number_input(label, value=value, key=key, help=help, label_visibility=_label_visibility, disabled=disabled, min_value=0)
    elif isinstance(value, datetime.datetime) or field == "date":
        if use_columns:
            col_split(label, value, key)
        else:
            form.date_input(label, value=value, key=key, help=help, label_visibility=_label_visibility, disabled=disabled)
    elif isinstance(value, datetime.time) or field == "time":
        # Convert string to datetime.time
        if isinstance(value, str):
            hours_minutes = value.split(":")[:2]
            value = datetime.datetime.strptime(":".join(hours_minutes), "%H:%M").time()
        # Format time into HH:MM
        # value = value.strftime("%H:%M")
        if use_columns:
            col_split(label, value, key)
        else:
            form.time_input(label, value=value, key=key, help=help, label_visibility=_label_visibility, disabled=disabled, step=900 if not DEBUG else 60)
    elif isinstance(value, list) or options:
        # form.write(label)
        # print(options, value)
        if use_columns:
            col_split(label, value, key)
        else:
            if field == "multiselect":
                form.multiselect(label, options, key=key, help=help, label_visibility=_label_visibility, default=[v for v in value if v in options], disabled=disabled)
            else:
                _index = options.index(value) if options and value in options else 0
                form.selectbox(label, options, key=key, help=help, label_visibility=_label_visibility, disabled=disabled, index=_index)
        # with form.container(border=True):
        #     for i, item in enumerate(value):
        #         create_form_element(form, None, item, key=f"{key}[{i}]", help=help, disabled=disabled)
        # form.multiselect(label, value, key=key, help=help, label_visibility=_label_visibility)
    elif isinstance(value, dict):
        items = value.items() #sorted(value.items(), key=lambda x: x[0])
        # TODO go through list and remove _help and _options and add them to the form correctly.
        
        form.subheader(label, divider=True, anchor=None)
        # c1, c2 = form.columns(2)
        with form.container(border=True):
            for k,v in items: #value.items():
                _help = None
                _field = None
                _options = []
                # if k == 'CronInterval': _help = "Default Interval in minutes. May be overridden by Cron Job config."
                # if k == 'CronActive': _help = 'Enable or disable the cron job. Both this AND the cron job must be enabled for the module to run periodically.'
                if any(l in k for l in ['_help','_options','_field']) : continue
                
                if k + "_help" in value:
                    _help = value[k + "_help"]
                if k + "_options" in value:
                    _options = value[k + "_options"]
                if k + "_field" in value:
                    _field = value[k + "_field"]

                create_form_element(form, k, v, key=f"{key}+{k}", help=_help, disabled=disabled, use_columns=True, field=_field, options=_options)
                # with c1:
                #     form.text_input(k, k, help=help,key= random.randint(1,999999), label_visibility="collapsed", type="default", disabled=True)
                # with c2:
                #     create_form_element(form, None, v, key=f"{key}+{k}", help=help, disabled=disabled)
        # form.json( value, expanded=False)
    elif isinstance(value, str):

        if (len(value) > 100 or field == "textarea") and _type != "password":
            form.text_area(label, value=value, key=key, help=help, label_visibility=_label_visibility, disabled=disabled)
        else:
            if use_columns:
                col_split(label, value, key)
            else:
                form.text_input(label, value=value, key=key, help=help, label_visibility=_label_visibility, type=_type,  disabled=disabled)
                # form.code( value)
    else:
        if use_columns:
            col_split(label, value, key)
        else:
            form.text_input(label, value=value, key=key, help=help, label_visibility=_label_visibility, type=_type, disabled=disabled)
