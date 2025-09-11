import streamlit as st
import numpy as np
import pandas as pd
from app.utils.state import get_state
from core.distributions import sample_triangular, sample_beta_pert
from core.montecarlo import simulate
from core.validators import build_edges

st.set_page_config(page_title="Simulación Monte Carlo", layout="wide")
st.header("2) Simulación Monte Carlo — Duración y Costo")

state = get_state()
if 'wbs' not in state:
    st.warning("Primero define una WBS en la página 'Definición del Proyecto'.")
    st.stop()

wbs = state['wbs']
distro = st.radio("Distribución de tiempos", ["Triangular (o/m/p)", "Beta-PERT (o/m/p)"], horizontal=True)
n_iter = st.slider("Iteraciones", 100, 10000, 2000, step=100)
seed = st.number_input("Semilla aleatoria (opcional)", value=42)

edges = build_edges(wbs)

if st.button("Ejecutar simulación"):
    with st.status("Simulando...", expanded=False) as status:
        if "Triangular" in distro:
            sampler = sample_triangular
        else:
            sampler = lambda o,m,p,size: sample_beta_pert(o,m,p,size,lam=4.0)
        durations, criticity = simulate(wbs, edges, sampler, n_iter=n_iter, seed=int(seed))
        status.update(label="Listo ✔️", state="complete")

    st.subheader("Resultados — Duración de proyecto")
    p10, p50, p80 = np.percentile(durations, [10,50,80])
    st.write(f"P10: **{p10:.2f}**, P50: **{p50:.2f}**, P80: **{p80:.2f}**")

    st.bar_chart(pd.DataFrame({"duracion":durations}))

    st.subheader("Criticidad por actividad")
    total = sum(criticity.values()) if criticity else 1
    crit_df = pd.DataFrame([{"id":k, "criticidad": v/ n_iter} for k,v in criticity.items()])
    st.dataframe(crit_df, use_container_width=True)
