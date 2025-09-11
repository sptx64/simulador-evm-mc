# Simulador Web de Gestión de Proyectos con Riesgo (Monte Carlo) y EVM

App multipágina en **Streamlit** para:
- Definir WBS + precedencias con escenarios (optimista, más probable, pesimista).
- Simular **Monte Carlo** (duración y costo) y estimar percentiles P10/P50/P80.
- Calcular **ruta crítica por iteración** (criticidad).
- Registrar avances y **EVM** (PV, EV, AC, SPI, CPI) y proyectar **EAC/ETC** con bandas.

> Nota: Por preferencia del usuario, **no se usa `ace_tools`** en ningún archivo.

## Inicio rápido
```bash
# 1) Crear entorno virtual (opcional, recomendado)
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)

# 2) Instalar paquete y dependencias
pip install -e .

# 3) Ejecutar la app
streamlit run app/Home.py
```

## Estructura
Ver el árbol de carpetas y descripciones en los archivos dentro de `app/` y `core/`.
