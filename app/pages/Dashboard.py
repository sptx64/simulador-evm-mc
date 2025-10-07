# --- bootstrap de ruta (Streamlit Cloud / local) ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # raíz del repo
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# --- fin bootstrap ---

import streamlit as st
import pandas as pd

from app.services.state_service import get_state
from app.utils.helpers import project_from_df
from app.core.cpm import compute_baseline_cpm, build_cost_profile
from app.core.evm import compute_bac
from app.ui.widgets import kpi
from app.ui.charts import hist_plotly, cdf_plotly, evm_s_curve_plotly

st.set_page_config(page_title="Dashboard Resultados", page_icon="📊", layout="wide")
st.title("Results")

state = get_state()

if state["project_df"] is None:
    st.info("First load or define a project.")
    st.stop()

project = project_from_df(state["project_df"])
baseline = state.get("baseline") or compute_baseline_cpm(project)

# KPIs
colA, colB, colC, colD = st.columns(4)
kpi(colA, "Duración base", f"{baseline['duration']:.2f} u.t.")
bac_map, bac_total = compute_bac(project, policy="m")
kpi(colB, "BAC (M)", f"{bac_total:,.2f}")
evm = state.get("evm_results")
if evm:
    kpi(colC, "SPI", f"{evm['SPI']:.3f}" if evm['SPI'] is not None else "N/A")
    kpi(colD, "CPI", f"{evm['CPI']:.3f}" if evm['CPI'] is not None else "N/A")
else:
    kpi(colC, "SPI", "N/A")
    kpi(colD, "CPI", "N/A")

st.divider()

# Gráficos clave
mc = state.get("mc_results")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Monte Carlo - Duración")
    if mc:
        st.plotly_chart(hist_plotly(mc["durations"], "Histograma Duración", "Duración"), use_container_width=True)
        st.plotly_chart(cdf_plotly(mc["durations"], "Curva S Duración (CDF)", "Duración"), use_container_width=True)
    else:
        st.info("Corre la simulación Monte Carlo para ver histogramas y curvas S.")
with col2:
    st.subheader("Monte Carlo - Costo")
    if mc:
        st.plotly_chart(hist_plotly(mc["costs"], "Histograma Costo", "Costo"), use_container_width=True)
        st.plotly_chart(cdf_plotly(mc["costs"], "Curva S Costo (CDF)", "Costo"), use_container_width=True)
    else:
        st.info("Corre la simulación Monte Carlo para ver histogramas y curvas S.")

st.subheader("Curva S EVM (PV, EV, AC)")
if evm:
    pv_profile = build_cost_profile(project, baseline, cost_policy="m")
    cut_time = evm.get("cut_time", int(baseline["duration"]))
    fig = evm_s_curve_plotly(pv_profile, evm["EV"], evm["AC"], cut_time=cut_time)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Registra avance en EVM para visualizar la curva S.")
