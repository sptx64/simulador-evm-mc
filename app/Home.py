import streamlit as st

st.set_page_config(page_title="Simulador EVM & Monte Carlo", layout="wide")
st.title("Simulador de Gestión de Proyectos con Riesgo (Monte Carlo) y EVM")
st.markdown(
    """        Esta aplicación te permite:
    1) Definir un proyecto (WBS + precedencias) con escenarios (o/m/p).
    2) Simular Monte Carlo para duración y costo, y analizar percentiles.
    3) Calcular criticidad (prob. de estar en ruta crítica).
    4) Registrar avances y calcular EVM (PV, EV, AC, SPI, CPI) y EAC/ETC.

    **Nota**: evitamos el uso de `ace_tools` por preferencia del usuario.
    """
)
st.info("Navega con el menú lateral para empezar.")
