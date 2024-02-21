import streamlit as st
import requests
from loguru import logger as log
from time import sleep
from datetime import datetime
from core.utils import init, server_request, to_snake_case, create_form_element, process_form_submission, merge_dicts, recursive_walk, encode_datetimes_for_db, filter_dict
from core.vars import DEBUG

@st.cache_resource(ttl=60 if not DEBUG else 5)
def get_platforms():
    """
    Gets all tips.
    """
    try:
        res = server_request("hunch_club/platforms")
        # print(res.status_code, res.json())
        if res.status_code == 200:
            data = res.json()
            return data.get('data', [])
        else:
            st.error(f"Error fetching data: {res.status_code} {res.text}")
        
    except Exception as e:
        log.error(e)
        st.error(str(e))
        
    return None

@st.cache_resource(ttl=86400 if not DEBUG else 5)
def get_default_schema():
    """
    Gets all tips.
    """
    try:
        default_schema = server_request("hunch_club/platform/fields")
        # print(default_schema)
        if not default_schema.status_code == 200:
            raise Exception("Error fetching default schema")
        return default_schema.json()
    except Exception as e:
        log.error(e)
        
    return None

def to_delete(id):
    try:
        st.info("Deleting platform...")
        # st.snow()
        sleep(1)
        # results = await hunchclub_mongodb.delete_by_id(id)
        results = server_request(f"hunch_club/platform/{id}", method="DELETE")
        if not results.status_code == 200:
            raise Exception(results.text)
        log.info("Platform Deleted")
        get_platforms.clear()
        return True
    except Exception as e:
        log.error(e)
        return False
    
def to_update(id, data):
    try:
        # Catch publish_schedule and convert to cron format
        print(id, data)
        _schedule = data.get("publish_schedule", "")
        _schedule = _schedule.split(":") if ":" in _schedule else None
        _schedule = f"{_schedule[1]} {_schedule[0]} * * *" if _schedule else data.get("publish_schedule", "")
        if 'publish_schedule' in data: data['publish_schedule'] = _schedule
        # if 'next_publish' in data: # Remove this as it is defined on the server
        #     del data['next_publish']
        results = server_request(f"hunch_club/platform/{id}", method="PATCH", data=data)
        # print("UPDATE QUERY", results.text)  
        if not results.status_code == 200:
            raise Exception(results.text)
        get_platforms.clear()
        return True
    except Exception as e:
        log.error(e)
        return False

def to_create(data):
    try:
        # Catch publish_schedule and convert to cron format
        print(data)
        _schedule = data.get("publish_schedule", "")
        _schedule = _schedule.split(":") if ":" in _schedule else None
        _schedule = f"{_schedule[1]} {_schedule[0]} * * *" if _schedule else data.get("publish_schedule", "")
        data['publish_schedule'] = _schedule
        data['name'] = data['name'] + " (Copy)"
        if 'next_publish' in data: # Remove this as it is defined on the server
            del data['next_publish']
        results = server_request("hunch_club/platform", method="POST", data=data) 
        # print("UPDATE QUERY", results.text)  
        if not results.status_code == 200:
            raise Exception(results.text)
        get_platforms.clear()
        return True
    except Exception as e:
        log.error(e)
        return False



if __name__ == "__main__":

    st.set_page_config(
        page_title="Hunch Club - Publish", 
        page_icon=":mailbox_with_mail:", 
        # initial_sidebar_state="collapsed", 
        layout="wide",
    )

    init()

    st.header("📬 Hunch Club Publish Platforms")
    
    # st.write("This is the tips page")
    
    platforms = get_platforms()
    

    # st.dataframe(platforms)

    default_schema = get_default_schema()

    if not default_schema:
        st.error("No default schema found")
        get_default_schema.clear()
        st.stop()

    ids = [str(x['id']) for x in platforms]
    
    id, form_data, action = process_form_submission()
    
    if id in ids and form_data:
        # Form submitted
        
        # print("ACTION>>>>>>", action)
        
        # INFO: This is a recursive function that encodes datetimes to ISO format for MongoDB, since we are using Motor, it does not encode correctly.
        recursive_walk(form_data, encode_datetimes_for_db) 
        
        if action == 'delete':
            # Deleting ID
            if to_delete(id):
                st.success(":white_check_mark: Platform Deleted")
            else:
                st.error("Error deleting platform")
                
            sleep(2)
            st.rerun()

        if action == 'save':
            # Saving ID
            if to_update(id, form_data):
                st.success(":white_check_mark: Platform Updated")
            else:
                st.error("Error updating platform")
            sleep(2)
            st.rerun()

        if action == "duplicate":
            # Duplicating item
            if to_create(form_data):
                st.success(":white_check_mark: Platform Duplicated")
            else:
                st.error("Error duplicating platform")
            sleep(2)
            st.rerun()
            
        
        if action == 'test platform':
            # Send test
            result = server_request("hunch_club/platform/test", method="POST", data=form_data)
            if result.status_code != 200:
                st.error(f"API returned status code {result.status_code}: {result.text}", icon="🚨")
                log.error(f"API returned status code {result.status_code}: {result.text}")
                st.stop()
            else:
                st.success(":white_check_mark: Test Successful")
            
        # # Update the database
        # sleep(2)
        # st.rerun()
    
    
    if not platforms:
        st.info("No platforms found")
        get_platforms.clear()    
    
    _quick_summary = []
    # drop columns
    for platform in platforms:
        _plat = {}
        # for k in platform.keys():
        for k in default_schema.keys():
            # print(k)
            # if k not in default_schema.keys():
            #     continue
            if k not in [
                    'language', 
                    'name', 
                    'channel', 
                    'active', 
                    'max_tips', 
                    'sort_by', 
                    'sort_order', 
                    'date_format', 
                    'use_icons', 
                    'next_publish',
                    'tips_filter',
                    'publish_type',
                    'tips_days_delta',
                    'stake_amount',
                    'id',
                ]:
                continue
            _v = platform[k]
            if k == 'next_publish':
                try:
                    _v = datetime.fromisoformat(_v).strftime("%B %d, %Y, %H:%M")
                except:
                    pass
            _plat[k] = _v
        _quick_summary.append(_plat)
    
    # Sort by next_publish
    _quick_summary = sorted(_quick_summary, key=lambda x: x.get('next_publish', datetime.utcnow()) )

    st.subheader("Quick Summary", divider=True)
    
    if st.session_state.get('platform_summary',None):
        # st.write(st.session_state.get('platform_summary',None))
        _changes = st.session_state.get('platform_summary',{})
        if st.button("Save Changes", use_container_width=True, type="primary"):
            st.info("Saving changes...")
            for i, plat in enumerate(_quick_summary):
                # Delete
                if _changes.get('deleted_rows',[]):
                    if i in _changes['deleted_rows']:
                        print("DELETED",i,plat['id'])
                        if to_delete(plat['id']):
                            st.success(":white_check_mark: Platform Deleted")
                        else:
                            st.error("Error deleting platform")
                        continue
                # Update
                if _changes.get('edited_rows',{}):
                    if i in _changes['edited_rows'].keys():
                        print("EDITED",i,plat['id'])
                        if to_update(plat['id'], _changes['edited_rows'][i]):
                            st.success(":white_check_mark: Platform Updated")
                        else:
                            st.error("Error updating platform")

                    
            
            st.balloons()
            st.rerun()
            
    st.data_editor(_quick_summary, use_container_width=True, column_config={
                "next_publish": st.column_config.TextColumn(
                    "Next Publish",
                    help="",
                    default="",
                    max_chars=50,
                ),
                "publish_type": st.column_config.SelectboxColumn("Publish Type", options=default_schema.get('publish_type_options',[])),
                "language": st.column_config.SelectboxColumn("Language", options=default_schema.get('language_options',[])),
                "channel": st.column_config.SelectboxColumn("Channel", options=default_schema.get('channel_options',[])),
                "sort_by": st.column_config.SelectboxColumn("Sort by", options=default_schema.get('sort_by_options',[])),
                "sort_order": st.column_config.SelectboxColumn("Sort Order", options=default_schema.get('sort_order_options',[])),
                "stake_amount": st.column_config.NumberColumn("Stake Amount", min_value=0.00, max_value=1000, step=0.01, format="$ %.2f"),
                "active": st.column_config.CheckboxColumn("Active"),
                "max_tips": st.column_config.NumberColumn("Max Tips", min_value=0, max_value=1000, step=1),
                "tips_days_delta": st.column_config.NumberColumn("Tips Days Delta", min_value=-1000, max_value=1000, step=1),
                "tips_filter": st.column_config.ListColumn("Tips Filter"),
                "name": st.column_config.TextColumn("Name"),
                
        }, column_order=('active', 'name', 'publish_type','tips_filter','language', 'channel', 'next_publish', 'max_tips', 'sort_by', 'sort_order', 'tips_days_delta','stake_amount'),
        key="platform_summary",
        num_rows='dynamic',
        disabled=('tips_filter','next_publish')
    )
    
    
    
    # Form to add new platform
    if st.button("Add New Platform", use_container_width=True):
        st.info("Adding platform...")
        st.balloons()
        # sleep(3)
        # Add platform, and rerun
        # Remove helpful stuff from schema
        save_schema = filter_dict(default_schema, ["_help","_options","_field"], exclude=True)
        # print(save_schema)
        if to_create(save_schema):
            st.success(":white_check_mark: Platform added")
            get_platforms.clear()
            sleep(1)
            st.rerun()
        else:
            st.error("Error adding platform")
            
    
    st.subheader("Platforms", divider=True)
    _names = [f"{'🟢' if x.get('active',False) else '🔴'} [{x.get('channel')}] [{x.get('language').upper()}] [{x.get('publish_type')}] [{','.join(x.get('tips_filter',[]))}] {x.get('name') or '<No Name>'}" for x in platforms]
    selected_platform = st.selectbox("Select Platform", _names, key="hunch_club_selected_platform", index=None)
    
    if selected_platform:
        for platform in platforms:
            
            if selected_platform != f"{'🟢' if platform.get('active',False) else '🔴'} [{platform.get('channel')}] [{platform.get('language').upper()}] [{platform.get('publish_type')}] [{','.join(platform.get('tips_filter',[]))}] {platform.get('name') or '<No Name>'}":
                continue
            
            # st.write(platform['id'])

            # with st.expander(f"{'🟢' if platform.get('active',False) else '🔴'} [{platform.get('channel')}] {platform.get('name') or '<No Name>'}"):
            
            with st.form(key=str(platform['id'])):
                # form = st.form(key=str(module['_id']))
                # form.text_input("ID", module['_id'], disabled=True)
                # form.text_input("ModuleName", module['config']['ModuleName'], key="ModuleName_"+str(module['_id']), disabled=True)
                # Sort items by key

                # c1,c2 = st.columns([1,1])
                # with c1:
                cc1,cc2,cc3,cc4 = st.columns(4)
                with cc1:
                    st.form_submit_button("Save", type="primary", use_container_width=True) 
                with cc2:
                    st.form_submit_button("Delete", type="secondary", use_container_width=True)
                with cc3:
                    st.form_submit_button("Duplicate", type="secondary", use_container_width=True)
                with cc4:
                    st.form_submit_button("Test Platform", type="primary", use_container_width=True)
                
                st.divider()

                items = default_schema.items() #sorted(default_schema.items(), key=lambda x: x[0])
                for k, value in items: # default_schema.items():
                    if k == "id": continue
                    # Get value from platform row
                    # print(k, value)
                    
                    # Merge new dict into old dict, so nested dicts are also updated
                    if isinstance(value, dict): 
                        # print("MERGING DICTS", value, platform.get(k, {}) )
                        merge_dicts(value, platform.get(k, {}))
                        # print("Platform>>>", k, value, type(value))
                    else:
                        value = platform.get(k, value)
                    # if k == "ModuleName": continue
                    _help = None
                    _field = None
                    _options = []
                    _disabled = False
                    # if k == 'CronInterval': _help = "Default Interval in minutes. May be overridden by Cron Job config."
                    # if k == 'CronActive': _help = 'Enable or disable the cron job. Both this AND the cron job must be enabled for the module to run periodically.'
                    if any(l in k for l in ['_help','_options','_field', '_disabled']) : continue
                    
                    if k + "_help" in default_schema:
                        _help = default_schema[k + "_help"]
                    if k + "_options" in default_schema:
                        _options = default_schema[k + "_options"]
                    if k + "_field" in default_schema:
                        _field = default_schema[k + "_field"]
                    if k + "_disabled" in default_schema:
                        _disabled = bool(default_schema[k + "_disabled"])
                    
                    if k in ['next_publish']:
                        value = datetime.fromisoformat(value).strftime("%B %d, %Y, %H:%M")
                        _disabled = True
                        
                        
                    # Override publish_schedule to be a time field for the UI, convert it back before saving it.
                    if k == "publish_schedule":
                        # print(value)
                        if not value or value == "None":
                            value = "30 8 * * *" # Default to 8:30am
                        time_value = value.split(" ")
                        time_value = f"{time_value[1]}:{time_value[0]}"
                        create_form_element(st, k, value=time_value, key = k+"_"+str(platform['id']), help = _help, use_columns=True, options = _options, field="time", disabled=_disabled)
                        
                    # elif k == "platform" or k == "icons":
                        # create_form_element(st, k, value=value, key = k+"_"+str(platform['id']), help = _help, use_columns=True, options = _options, field=_field, disabled=_disabled, use_expander=(True, False))
                        
                    else:
                        create_form_element(st, k, value=value, key = k+"_"+str(platform['id']), help = _help, use_columns=True, options = _options, field=_field, disabled=_disabled, use_expander=(True, False))  
                    
