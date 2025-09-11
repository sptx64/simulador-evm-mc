import streamlit as st
import pandas as pd
from app.utils.state import get_state, save_state
from core.validators import validate_wbs
from core.io import load_wbs_csv

st.set_page_config(page_title="Definición del Proyecto", layout="wide")
st.header("1) Definición del Proyecto — WBS y Precedencias")

state = get_state()
st.write("Carga un CSV de WBS o edítalo directamente en la tabla.")

uploaded = st.file_uploader("Sube un CSV de WBS", type=["csv"])
if uploaded is not None:
    df = pd.read_csv(uploaded)
    state['wbs'] = df.to_dict(orient='records')
    save_state(state)

if 'wbs' not in state:
    # Plantilla vacía
    df = pd.DataFrame([
        {"id":"A","desc":"Arranque","deps":"","t_o":3,"t_m":5,"t_p":8,"c_o":1000,"c_m":1200,"c_p":1600},
        {"id":"B","desc":"Planificación","deps":"A","t_o":2,"t_m":3,"t_p":6,"c_o":500,"c_m":700,"c_p":1100},
    ])
else:
    df = pd.DataFrame(state['wbs'])

edited = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True
)

if st.button("Validar WBS"):
    ok, errors = validate_wbs(edited)
    if ok:
        st.success("WBS válida ✔️")
        state['wbs'] = edited.to_dict(orient='records')
        save_state(state)
    else:
        st.error("Se encontraron problemas en la WBS:")
        for e in errors:
            st.write("- ", e)
