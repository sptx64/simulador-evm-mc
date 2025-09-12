import streamlit as st
import pandas as pd

from app.services.state_service import get_state, save_state
from app.core.cpm import compute_baseline_cpm, build_cost_profile
from app.core.evm import compute_bac, compute_evm_kpis
from app.utils.helpers import project_from_df, to_csv_download
from app.ui.charts import evm_s_curve_plotly
from app.ui.widgets import kpi, toast_success

st.set_page_config(page_title="EVM", page_icon="🧮", layout="wide")
st.title("3) Earned Value Management (EVM)")

state = get_state()

if state["project_df"] is None:
    st.info("Primero define o carga un proyecto.")
    st.stop()

project = project_from_df(state["project_df"])
baseline = state.get("baseline") or compute_baseline_cpm(project)
state["baseline"] = baseline

st.caption("Edita el avance real por actividad y su costo real acumulado a la fecha de corte.")
if state["progress_df"] is None:
    progress_df = pd.DataFrame({
        "activity_id": state["project_df"]["id"],
        "percent_complete": [0.0]*len(state["project_df"]),
        "actual_cost_to_date": [0.0]*len(state["project_df"]),
    })
else:
    progress_df = state["progress_df"]

progress_df = st.data_editor(
    progress_df,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "percent_complete": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
        "actual_cost_to_date": st.column_config.NumberColumn(min_value=0.0, step=0.01, format="%.2f"),
    }
)

col_actions = st.columns(3)
with col_actions[0]:
    policy = st.selectbox("Política de BAC por actividad", ["m (más probable)", "pert (media PERT)"], index=0)
with col_actions[1]:
    cut_time = st.slider("Fecha de corte (unidad de tiempo)", min_value=0, max_value=int(baseline["duration"]), value=int(min( int(baseline["duration"]), max(1, int(baseline["duration"]//2)) )))
with col_actions[2]:
    if st.button("💾 Guardar avance en memoria", use_container_width=True):
        state["progress_df"] = progress_df.copy()
        save_state(state)
        toast_success("Avance guardado.")

st.divider()
st.subheader("KPIs EVM")

# Cálculos base
cost_policy = "m" if policy.startswith("m") else "pert"
pv_profile = build_cost_profile(project, baseline, cost_policy=cost_policy)  # Serie temporal PV
bac_map, bac_total = compute_bac(project, policy=cost_policy)

# MC para EAC_mc si existe
mc = state.get("mc_results")
mc_costs = mc["costs"] if mc else None

evm = compute_evm_kpis(
    progress_df=progress_df,
    pv_profile=pv_profile,
    bac_map=bac_map,
    bac_total=bac_total,
    cut_time=int(cut_time),
    mc_cost_samples=mc_costs
)

state["evm_results"] = evm
save_state(state)

c1, c2, c3, c4, c5, c6 = st.columns(6)
kpi(c1, "PV", f"{evm['PV']:,.2f}")
kpi(c2, "EV", f"{evm['EV']:,.2f}")
kpi(c3, "AC", f"{evm['AC']:,.2f}")
kpi(c4, "SV", f"{evm['SV']:,.2f}")
kpi(c5, "CV", f"{evm['CV']:,.2f}")
kpi(c6, "BAC", f"{evm['BAC']:,.2f}")

c7, c8 = st.columns(2)
kpi(c7, "SPI", f"{evm['SPI']:.3f}" if evm['SPI'] is not None else "N/A")
kpi(c8, "CPI", f"{evm['CPI']:.3f}" if evm['CPI'] is not None else "N/A")

c9, c10 = st.columns(2)
kpi(c9, "EAC (AC + (BAC−EV)/CPI)", f"{evm['EAC_cost_1']:,.2f}" if evm['EAC_cost_1'] is not None else "N/A")
kpi(c10, "EAC (BAC/CPI)", f"{evm['EAC_cost_2']:,.2f}" if evm['EAC_cost_2'] is not None else "N/A")

if evm.get("EAC_mc_cost"):
    c11, c12 = st.columns(2)
    kpi(c11, "EAC_mc P50", f"{evm['EAC_mc_cost']['p50']:,.2f}")
    kpi(c12, "EAC_mc P80", f"{evm['EAC_mc_cost']['p80']:,.2f}")
else:
    st.caption("Sugerencia: Ejecuta Monte Carlo para ver EAC basados en simulación (P50/P80).")

st.markdown("**Curva S EVM (PV, EV, AC)**")
fig = evm_s_curve_plotly(pv_profile, evm["EV"], evm["AC"], cut_time=int(cut_time))
st.plotly_chart(fig, use_container_width=True)

st.markdown("**Exportar reporte EVM (CSV)**")
evm_csv = pd.DataFrame([evm])
from app.utils.helpers import to_csv_download
st.download_button(
    "⬇️ Descargar EVM.csv",
    data=to_csv_download(evm_csv),
    file_name="evm_report.csv",
    mime="text/csv",
    use_container_width=True
)
