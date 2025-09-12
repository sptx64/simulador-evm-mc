# --- bootstrap de ruta (Streamlit Cloud / local) ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # raíz del repo
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# --- fin bootstrap ---

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Acerca y Documentación", page_icon="❓", layout="wide")
st.title("5) Acerca de la App y Documentación")

st.markdown("""
Esta aplicación implementa un flujo **híbrido**:
- **Planificación predictiva (PERT/CPM)** para baseline de duración y costo (BAC).
- **Ejecución ágil (Kanban)** como apoyo visual y organizativo externo (pega la URL de tu tablero).
- **Simulación Monte Carlo** para entender la incertidumbre en tiempo y costo.
- **EVM (Earned Value Management)** para control de valor ganado y pronósticos (EAC).

**Consejos**:
- Asegúrate de que el grafo de actividades sea acíclico.
- Revisa IDs duplicadas y que todas las predecesoras existan.
- Si **PV** o **AC** son cero, algunas métricas (SPI, CPI) podrían no estar definidas.
""")

st.subheader("Enlace a tablero Kanban")
kanban = st.text_input("Pega la URL de tu tablero (Jira/Trello/Asana):", value="")
if kanban:
    st.success(f"URL guardada localmente: {kanban}")

st.subheader("Materiales")
st.markdown("- **README**: ver archivo en el repositorio.")
st.markdown("- **Plantilla de reporte**: `docs/report_template.md`.")
st.markdown("- **Guion de video**: `docs/video_outline.md`.")

st.divider()
st.caption("Licencia: MIT. Autoría: Jonathan Amado, Cesar Catalán, Luis Florian - 2025.")
