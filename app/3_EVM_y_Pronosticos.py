import streamlit as st
import pandas as pd
from app.utils.state import get_state
from core.evm import compute_pv, compute_ev_ac, metrics

st.set_page_config(page_title="EVM y Pronósticos", layout="wide")
st.header("3) EVM — PV, EV, AC y Pronósticos (EAC/ETC)")

state = get_state()

st.subheader("1) Línea base (BAC) y calendario PV")
bac = st.number_input("BAC (costo total planificado)", min_value=0.0, value=5000.0, step=100.0)
pv_sched = pd.DataFrame({
    "fecha": pd.date_range("2025-09-01", periods=5, freq="D"),
    "peso": [0.1,0.2,0.3,0.3,0.1],
})
st.dataframe(pv_sched, use_container_width=True)
pv_t = compute_pv(pv_sched, bac)

st.subheader("2) Avance real y AC")
avances = pd.DataFrame({
    "id":["A","B","C","D","E"],
    "fecha_pct": pd.date_range("2025-09-01", periods=5, freq="D"),
    "pct_completo":[1.0,1.0,0.4,0.25,0.0],
    "acumulado_AC":[1200,750,1300,200,0],
})
st.dataframe(avances, use_container_width=True)

ev, ac = compute_ev_ac(avances)
df_metrics = metrics(pv_t.set_index("fecha")["pv"], ev, ac, bac)
st.subheader("Métricas EVM")
st.dataframe(df_metrics, use_container_width=True)
