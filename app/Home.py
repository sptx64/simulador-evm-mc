# --- bootstrap de ruta (Streamlit Cloud / local) ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]  # raíz del repo
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# --- fin bootstrap ---

import streamlit as st
import pandas as pd
from pathlib import Path

from app.services.state_service import get_state, save_state, reset_state
from app.services.io_service import load_csv, save_json
from app.core.cpm import compute_baseline_cpm
from app.core.evm import build_pv_profile, compute_bac
from app.utils.helpers import project_from_df
from app.ui.widgets import kpi, file_uploader_row, toast_success
from app.utils.validators import validate_project_df

DATA_DIR = Path("data")

st.set_page_config(page_title="Simulador MC + EVM", page_icon="📈", layout="wide")

st.title("Simulador de Proyecto: Monte Carlo + EVM (PERT/CPM + Kanban)")
st.caption("App multipágina con enfoque híbrido: planificación predictiva (PERT/CPM) + ejecución ágil (Kanban).")

state = get_state()

def _validate_or_stop(df: pd.DataFrame):
    errs = validate_project_df(df)
    if errs:
        for e in errs:
            st.error(e)
        st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📦 Cargar caso de ejemplo", use_container_width=True):
        state["project_df"] = load_csv(DATA_DIR / "sample_project.csv")
        state["progress_df"] = load_csv(DATA_DIR / "sample_progress.csv")
        _validate_or_stop(state["project_df"])
        project = project_from_df(state["project_df"])
        baseline = compute_baseline_cpm(project)
        state["baseline"] = baseline
        save_state(state)
        toast_success("Caso de ejemplo cargado.")
with col2:
    proj_file, prog_file = file_uploader_row("Importar CSVs (proyecto y avance)")
    if proj_file is not None:
        state["project_df"] = pd.read_csv(proj_file)
    if prog_file is not None:
        state["progress_df"] = pd.read_csv(prog_file)
    if proj_file or prog_file:
        if state["project_df"] is not None:
            _validate_or_stop(state["project_df"])
            project = project_from_df(state["project_df"])
            state["baseline"] = compute_baseline_cpm(project)
        save_state(state)
        toast_success("Datos importados.")
with col3:
    if st.button("💾 Exportar estado (JSON)", use_container_width=True):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        out = {
            "project": (state["project_df"].to_dict(orient="list") if state["project_df"] is not None else None),
            "progress": (state["progress_df"].to_dict(orient="list") if state["progress_df"] is not None else None),
            "baseline": state.get("baseline"),
            "mc_results": state.get("mc_results"),
            "evm_results": state.get("evm_results"),
        }
        save_json(DATA_DIR / "state.json", out)
        toast_success("Estado guardado en data/state.json.")

st.divider()

st.subheader("Resumen del proyecto actual")
if state["project_df"] is None:
    st.info("No hay proyecto cargado. Ve a **1_Definición de Proyecto** o usa el botón de ejemplo.")
else:
    project_df = state["project_df"]
    n_acts = len(project_df)
    st.dataframe(project_df, use_container_width=True, hide_index=True)

    if not state.get("baseline"):
        _validate_or_stop(project_df)
        project = project_from_df(project_df)
        baseline = compute_baseline_cpm(project)
        state["baseline"] = baseline
        save_state(state)

    bl = state["baseline"]
    colA, colB, colC = st.columns(3)
    kpi(colA, "Actividades", f"{n_acts}")
    kpi(colB, "Duración base (PERT)", f"{bl['duration']:.2f} u.t.")
    bac_map, bac_total = compute_bac(project_from_df(project_df), policy="m")
    kpi(colC, "BAC (costo base)", f"{bac_total:,.2f} {bl.get('currency','')}")
    st.caption("Nota: Duración base por PERT/CPM; BAC usando costo más probable (cost_m).")

st.divider()
st.markdown(
"""
### Flujo recomendado
1. **1_Definición de Proyecto**: define actividades, dependencias y calcula baseline.
2. **2_Simulación Monte Carlo**: ejecuta N iteraciones para duración y costo.
3. **3_EVM**: registra avances y costos reales; obtén KPIs y pronósticos.
4. **4_Dashboard Resultados**: panel integrado con KPIs y gráficos.
5. **5_Acerca y Documentación**: ayuda, FAQ y materiales para tu reporte/video.
"""
)

with st.expander("⚙️ Utilidades"):
    if st.button("Reiniciar estado en memoria"):
        reset_state()
        st.success("Sesión reiniciada.")
