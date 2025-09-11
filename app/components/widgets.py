import streamlit as st

def section(title: str, help_text: str | None = None):
    st.subheader(title, help=help_text)
