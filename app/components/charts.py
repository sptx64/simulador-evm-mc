# Separación intencional: las funciones de `core.reporting` devuelven figuras.
# Aquí solo las presentamos en Streamlit cuando haga falta.
import streamlit as st

def show_figure(fig):
    st.pyplot(fig)
