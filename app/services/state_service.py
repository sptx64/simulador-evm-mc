from __future__ import annotations
import streamlit as st

# Claves de estado:
# - project_df: DataFrame del proyecto
# - progress_df: DataFrame de avances
# - baseline: dict con resultado CPM
# - mc_results: dict con resultados MC
# - evm_results: dict con KPIs EVM

DEFAULTS = {
    "project_df": None,
    "progress_df": None,
    "baseline": None,
    "mc_results": None,
    "evm_results": None
}

def get_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v
    return st.session_state

def save_state(state):
    # st.session_state ya actúa como store; esta función existe por claridad
    return True

def reset_state():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
