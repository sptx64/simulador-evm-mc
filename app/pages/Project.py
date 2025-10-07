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

from app.services.state_service import get_state, save_state
from app.core.cpm import compute_baseline_cpm, build_cost_profile
from app.utils.validators import validate_project_df
from app.utils.helpers import project_from_df, to_csv_download
from app.ui.widgets import kpi, toast_success
from app.ui.charts import line_plotly

st.set_page_config(page_title="Definición de Proyecto", page_icon="📝",)
st.title("1) Definición de Proyecto")

state = get_state()
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Editor de tabla
if state["project_df"] is None:
    # Plantilla mínima
    st.info("Carga el caso de ejemplo desde Home o importa tu CSV para empezar.")
    df = pd.DataFrame({
        "id": ["A"],
        "name": ["Actividad A"],
        "predecessors": [""],
        "dur_o": [1.0], "dur_m": [2.0], "dur_p": [3.0],
        "cost_o": [100.0], "cost_m": [200.0], "cost_p": [300.0],
    })
else:
    df = state["project_df"]

st.caption("Edita en la tabla. `predecessors` separadas por coma (ej. A,B).")
edited = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    column_config={
        "predecessors": st.column_config.TextColumn(help="IDs de predecesoras separadas por coma"),
        "dur_o": st.column_config.NumberColumn(format="%.2f", min_value=0.0),
        "dur_m": st.column_config.NumberColumn(format="%.2f", min_value=0.0),
        "dur_p": st.column_config.NumberColumn(format="%.2f", min_value=0.0),
        "cost_o": st.column_config.NumberColumn(format="%.2f", min_value=0.0),
        "cost_m": st.column_config.NumberColumn(format="%.2f", min_value=0.0),
        "cost_p": st.column_config.NumberColumn(format="%.2f", min_value=0.0),
    }
)

col_actions = st.columns(3)
with col_actions[0]:
    if st.button("💾 Guardar cambios en memoria", use_container_width=True):
        state["project_df"] = edited.copy()
        save_state(state)
        toast_success("Proyecto guardado en memoria.")

with col_actions[1]:
    csv_bytes = to_csv_download(edited)
    st.download_button(
        "⬇️ Descargar CSV de proyecto",
        data=csv_bytes,
        file_name="project_export.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_actions[2]:
    if st.button("Calcular Baseline (CPM/PERT)", use_container_width=True):
        errors = validate_project_df(edited)
        if errors:
            for e in errors:
                st.error(e)
        else:
            project = project_from_df(edited)
            baseline = compute_baseline_cpm(project)
            state["baseline"] = baseline
            state["project_df"] = edited.copy()
            save_state(state)
            toast_success("Baseline calculado.")

st.divider()
st.subheader("Resultado Baseline")
if not state.get("baseline"):
    st.info("Calcula el baseline para ver resultados.")
else:
    bl = state["baseline"]
    colA, colB, colC = st.columns(3)
    kpi(colA, "Duración base (u.t.)", f"{bl['duration']:.2f}")
    kpi(colB, "Ruta crítica", " → ".join(bl["critical_path"]))
    kpi(colC, "N actividades críticas", f"{len(bl['critical_path'])}")

    st.markdown("**Tabla CPM (ES/EF/LS/LF/Holgura)**")
    st.dataframe(pd.DataFrame(bl["table"]), use_container_width=True, hide_index=True)

    st.markdown("**Perfil de costo base (PV) por período**")
    pv = build_cost_profile(project_from_df(state["project_df"]), bl, cost_policy="m")
    fig = line_plotly(pv.index.tolist(), pv.values.tolist(), "PV por período", "Tiempo (u.t.)", "PV")
    st.plotly_chart(fig, use_container_width=True)
