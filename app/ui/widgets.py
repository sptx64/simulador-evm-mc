import streamlit as st

def kpi(container, label: str, value: str):
    with container:
        st.metric(label, value)

def toast_success(msg: str):
    st.success(msg)

def file_uploader_row(label: str):
    st.caption(label)
    col1, col2 = st.columns(2)
    with col1:
        proj_file = st.file_uploader("Proyecto (CSV)", type=["csv"], key="proj_file_upl")
    with col2:
        prog_file = st.file_uploader("Avances (CSV)", type=["csv"], key="prog_file_upl")
    return proj_file, prog_file
