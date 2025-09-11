import streamlit as st

def get_state() -> dict:
    if 'state' not in st.session_state:
        st.session_state['state'] = {}
    return st.session_state['state']

def save_state(state: dict):
    st.session_state['state'] = state
