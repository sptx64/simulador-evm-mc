# --- bootstrap de ruta (Streamlit Cloud / local) ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # raíz del repo
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# --- fin bootstrap ---

import streamlit as st
import pandas as pd
from pathlib import Path
from collections import Counter

from app.services.state_service import get_state, save_state
from app.core.montecarlo import run_monte_carlo
from app.utils.validators import validate_project_df
from app.utils.helpers import project_from_df, to_csv_download
from app.ui.charts import hist_plotly, cdf_plotly, bar_plotly
from app.ui.widgets import toast_success

st.set_page_config(page_title="Simulación Monte Carlo", page_icon="🎲", layout="wide")
st.title("2) Simulación Monte Carlo")

state = get_state()

if state["project_df"] is None:
    st.info("Primero define o carga un proyecto en **1_Definición de Proyecto**.")
    st.stop()

errors = validate_project_df(state["project_df"])
if errors:
    st.error("Corrige los errores en la definición del proyecto antes de simular:")
    for e in errors:
        st.error(f"• {e}")
    st.stop()

with st.sidebar:
    st.header("Parámetros de simulación")
    N = st.number_input("Iteraciones (N)", min_value=100, max_value=100_000, value=5000, step=100)
    seed = st.number_input("Semilla aleatoria", min_value=0, max_value=1_000_000, value=42, step=1)
    dist = st.selectbox("Distribución", options=["triangular", "beta-pert"], index=0)
    use_risks = st.checkbox("Activar eventos de riesgo (opcional)", value=False)
    risks_df = None
    if use_risks:
        st.caption("Riesgos discretos: prob ∈ [0,1], impactos en tiempo y costo; applies_to: 'GLOBAL' o lista de IDs")
        empty_risks = pd.DataFrame({
            "name": pd.Series(dtype="object"),
            "prob": pd.Series(dtype="float"),
            "impact_time": pd.Series(dtype="float"),
            "impact_cost": pd.Series(dtype="float"),
            "applies_to": pd.Series(dtype="object"),
        })
        risks_df = st.data_editor(
            empty_risks,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            column_config={
                "name": st.column_config.TextColumn("name", help="Nombre del riesgo"),
                "prob": st.column_config.NumberColumn("prob", min_value=0.0, max_value=1.0, step=0.01, format="%.2f"),
                "impact_time": st.column_config.NumberColumn("impact_time", step=0.01, format="%.2f"),
                "impact_cost": st.column_config.NumberColumn("impact_cost", step=0.01, format="%.2f"),
                "applies_to": st.column_config.TextColumn("applies_to", help="GLOBAL o IDs separados por coma o ';'"),
            },
        )

if st.button("Ejecutar simulación", type="primary"):
    project = project_from_df(state["project_df"])
    with st.spinner("Simulando..."):
        results = run_monte_carlo(
            project=project,
            N=int(N),
            seed=int(seed),
            dist=dist,
            risks_df=risks_df
        )
    state["mc_results"] = results
    save_state(state)
    toast_success("Simulación completada.")

st.divider()
st.subheader("Resultados")

mc = state.get("mc_results")
if not mc:
    st.info("Aún no hay resultados. Ejecuta la simulación.")
    st.stop()

# KPIs
colA, colB, colC, colD = st.columns(4)
colA.metric("Duración media", f"{mc['duration_stats']['mean']:.2f}")
colB.metric("Duración P50", f"{mc['duration_stats']['p50']:.2f}")
colC.metric("Costo medio", f"{mc['cost_stats']['mean']:.2f}")
colD.metric("Costo P80", f"{mc['cost_stats']['p80']:.2f}")

# Gráficos
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(hist_plotly(mc["durations"], "Histograma de duración", "Duración (u.t.)"), use_container_width=True)
    st.plotly_chart(cdf_plotly(mc["durations"], "Curva S (CDF) - Duración", "Duración (u.t.)"), use_container_width=True)
with col2:
    st.plotly_chart(hist_plotly(mc["costs"], "Histograma de costo", "Costo"), use_container_width=True)
    st.plotly_chart(cdf_plotly(mc["costs"], "Curva S (CDF) - Costo", "Costo"), use_container_width=True)

# Frecuencia de rutas críticas
st.markdown("**Frecuencia de rutas críticas (Top 10)**")
cp_counts = Counter([tuple(x) for x in mc["critical_paths"]])
top = cp_counts.most_common(10)
labels = [" → ".join(k) for k,_ in top]
vals = [v for _,v in top]
st.plotly_chart(bar_plotly(labels, vals, "Rutas críticas más frecuentes", "Ruta", "Frecuencia"), use_container_width=True)

# Exportables
colx, coly = st.columns(2)
with colx:
    st.download_button(
        "⬇️ Exportar resultados (duración & costo) CSV",
        data=to_csv_download(pd.DataFrame({"duration": mc["durations"], "cost": mc["costs"]})),
        file_name="mc_results.csv",
        mime="text/csv",
        use_container_width=True
    )
with coly:
    st.download_button(
        "⬇️ Exportar rutas críticas (iteración por iteración) CSV",
        data=to_csv_download(pd.DataFrame({"critical_path": ["-".join(cp) for cp in mc["critical_paths"]]})),
        file_name="mc_critical_paths.csv",
        mime="text/csv",
        use_container_width=True
    )
