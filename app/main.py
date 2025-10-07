import streamlit as st

st.set_page_config(layout="wide")
pages_dict = {
  "HOME"   : [st.Page("pages/Home.py", title="Home", icon=":material/elderly:")],
  "SETUP" : [st.Page("pages/Project.py", title="Project management", icon=":material/upload:")],
  "MINE PLAN" : [
    st.Page("pages/SimulationMC.py", title="MCSimulations", icon=":material/event_list:"),
    st.Page("pages/EVM.py", title="EVM", icon=":material/front_loader:"),
                ],
  "DASHBOARD" : [st.Page("pages/dashboard.py", title="Results", icon=":material/delete:"),],
  "DOCS" : [st.Page("pages/Docs", title="Docs")],
}

pg = st.navigation( pages_dict, )

pg.run()
