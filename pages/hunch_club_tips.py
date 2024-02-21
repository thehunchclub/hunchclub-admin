import streamlit as st
from core.utils import init, server_request, to_snake_case, create_form_element, process_form_submission, merge_dicts
import requests
from loguru import logger as log
from datetime import datetime, timedelta
from core.vars import DEBUG
import pandas as pd
from time import sleep

@st.cache_resource(ttl=3600 if not DEBUG else 5)
def get_tips():
    """
    Gets all tips.
    """
    try:
        res = server_request("hunch_club/tips/all")
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


def update_tips(edited_rows:dict, dataset:dict):
    if edited_rows:
        # st.write(edited_rows)
        errors = []
        for index, row in edited_rows.items():
            # print(index, row, dataset[index])
            try:
                row_id = dataset[index]['_id']
                if update_tip(row_id, row):
                    # st.success(f"Updated Tip {index}")
                    pass
                else:
                    # st.error(f"Error updating Tip {index}")
                    errors.append("Error updating Tip {row_id}")
            except Exception as e:
                log.error(e)
                st.error(str(e))
            pass
        # st.session_state['edit_tips_1']['edited_rows'] = {}
        st.balloons()
        get_tips.clear()
        if errors:
            st.error("\n".join(errors))
        else:
            st.success(":white_check_mark: Tips Updated")
        sleep(3)
        st.rerun()


def update_tip(id:str, tip:dict):
    """
    Updates a tip in the database.
    """
    try:
        res = server_request(f"hunch_club/tips/{id}", method="PATCH", data=tip)
        if res.status_code == 200:
            return True
        else:
            st.error(f"Error updating tip: {res.status_code} {res.text}")
        
    except Exception as e:
        log.error(e)
        st.error(str(e))
        
    return None

if __name__ == "__main__":

    st.set_page_config(
        page_title="Hunch Club - Tips", 
        page_icon=":admission_tickets:", 
        # initial_sidebar_state="collapsed", 
        layout="wide",
    )

    init()

    st.header("🎟️ Hunch Club Tips")
    
    tips = get_tips()
    
    if not tips:
        st.warning("No tips found.")
        get_tips.clear()
    else:
        # Sort tips by datetime in reverse order
        tips = sorted(tips, key=lambda x: x['datetime'], reverse=True)
        # Drop columns: _id, language
        for tip in tips:
            # tip.pop('_id', None)
            tip.pop('language', None)
            # Reformat datetime 
            try:
                tip['datetime'] = datetime.strptime(tip['datetime'], "%Y-%m-%d %H:%M:%S")

                # Change the format to "YYYY-MM-DD HH:MM"
                tip['datetime'] = tip['datetime'].strftime("%Y-%m-%d, %H:%M")
            except:
                pass
        
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.utcnow().strftime("%Y-%m-%d")
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # TODO For Future Tips (today, tomorrow, future) - allow for deletion of tips (in case of duplicates)
        
        st.subheader("Future Tips", divider=True)
        # Filter all tips results before yesterday
        future_tips = [tip for tip in tips if tip['datetime'] > tomorrow]
        st.data_editor(future_tips, key="edit_tips_future", use_container_width=True, column_config={
                "_id" : None,
                "datetime" : "Date",
                "participants" : "Participants",
                "event_name" : "Event Name",
                "event_type" : "Event Type",
                "selection" : "Selection",
                "odds" : "Odds",
                "event_result" : None,
                "bet_result" : None,
                "free_tips": st.column_config.CheckboxColumn(label="Free Tip"),
                "premium_tip": st.column_config.CheckboxColumn(label="Premium Tip"),
            }, disabled=("datetime", "participants","event_type"),
            column_order=("datetime",  "event_type", "event_name", "participants",  "free_tips", "premium_tip", "event_result", "bet_result", "selection", "odds", "description")
        )
        edited_rows = st.session_state.get("edit_tips_future", {}).get("edited_rows", {}) 
        if edited_rows:
            if st.button("Save Changes", use_container_width=True, type="primary"):
                update_tips(edited_rows, future_tips)
                
        # Tips for tomorrow only
        tomorrow_tips = [tip for tip in tips if tip['datetime'].startswith(tomorrow)]
        st.subheader(f"Tomorrow's Tips ({len(tomorrow_tips)})", divider=True)
        st.data_editor(tomorrow_tips, key="edit_tips_tomorrow", use_container_width=True, column_config={
                "_id" : None,
                "datetime" : "Date",
                "participants" : "Participants",
                "event_name" : "Event Name",
                "event_type" : "Event Type",
                "selection" : "Selection",
                "odds" : "Odds",
                "event_result" : None,
                "bet_result" : None,
                "free_tips": st.column_config.CheckboxColumn(label="Free Tip"),
                "premium_tip": st.column_config.CheckboxColumn(label="Premium Tip"),
            }, disabled=("datetime", "participants","event_type"),
            column_order=("datetime",  "event_type", "event_name", "participants",  "free_tips", "premium_tip", "event_result", "bet_result", "selection", "odds", "description")
        )
        edited_rows = st.session_state.get("edit_tips_tomorrow", {}).get("edited_rows", {}) 
        if edited_rows:
            if st.button("Save Changes", use_container_width=True, type="primary"):
                update_tips(edited_rows, tomorrow_tips)


        # Tips for today only
        todays_tips = [tip for tip in tips if tip['datetime'].startswith(today)]
        
        st.subheader(f"Today's Tips ({len(todays_tips)})", divider=True)
        st.data_editor(todays_tips, key="edit_tips_today", use_container_width=True, column_config={
                "_id" : None,
                "datetime" : "Date",
                "participants" : "Participants",
                "event_name" : "Event Name",
                "event_type" : "Event Type",
                "selection" : "Selection",
                "odds" : "Odds",
                "event_result" : None,
                "bet_result" : None,
                "free_tips": st.column_config.CheckboxColumn(label="Free Tip"),
                "premium_tip": st.column_config.CheckboxColumn(label="Premium Tip"),
            }, disabled=("datetime", "participants","event_type"),
            column_order=("datetime",  "event_type", "event_name", "participants",  "free_tips", "premium_tip", "event_result", "bet_result", "selection", "odds", "description")
        )
        edited_rows = st.session_state.get("edit_tips_today", {}).get("edited_rows", {}) 
        if edited_rows:
            if st.button("Save Changes", use_container_width=True, type="primary"):
                update_tips(edited_rows, todays_tips)

        # Tips for yesterday
        yesterdays_tips = [tip for tip in tips if tip['datetime'].startswith(yesterday)]

        st.subheader(f"Yesterday's Tips ({len(yesterdays_tips)})", divider=True)
        st.data_editor(yesterdays_tips, key="edit_tips_yesterday", use_container_width=True, hide_index=True, disabled=("datetime", "participants","odds","selection","event_type","event_name"), column_config={
                    "_id" : None,
                    "description" : None,
                    "datetime" : "Date",
                    "participants" : "Participants",
                    "event_name" : "Event Name",
                    "event_type" : "Event Type",
                    "selection" : "Selection",
                    "odds" : "Odds",
                    "event_result" : "Event Result",
                    "bet_result" :st.column_config.SelectboxColumn(label="Bet Result", options=["Win", "Lose", "Void"]),
                    "free_tips": st.column_config.CheckboxColumn(label="Free Tip", disabled=True),
                    "premium_tip": st.column_config.CheckboxColumn(label="Premium Tip", disabled=True),
                }, column_order=("datetime",  "event_type", "event_name", "participants",  "free_tips", "premium_tip", "event_result", "bet_result", "selection", "odds", "description")
        )
        edited_rows = st.session_state.get("edit_tips_yesterday", {}).get("edited_rows", {}) 
        if edited_rows:
            if st.button("Save Changes", use_container_width=True, type="primary"):
                update_tips(edited_rows, yesterdays_tips)


        st.subheader("Previous Tips", divider=True)
        # Filter all tips results before yesterday
        previous_tips = [tip for tip in tips if tip['datetime'] < yesterday]
        # previous_tips = [tip for tip in tips if tip['datetime'].startswith(yesterday)]
        
        st.dataframe(previous_tips, use_container_width=True, column_config={
            "_id" : None
        }, column_order=("datetime",  "event_type", "event_name", "participants",  "free_tips", "premium_tip", "event_result", "bet_result", "selection", "odds", "description"))


    # if DEBUG:
    #     with st.expander("Debug"):
    #         st.subheader("Session State")
    #         st.write(st.session_state)
