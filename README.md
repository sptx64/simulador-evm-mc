# Simulador de Proyecto: Monte Carlo + EVM (PERT/CPM + Kanban)

**Integrantes del proyecto**
- Cesar Roberto Catalán Escobar  
- Jonathan Jose Amado Moreno  
- Luis Florian  

Aplicación **Streamlit** multipágina para:
- Definir un proyecto (actividades, dependencias, O/M/P en tiempo y costo)
- Calcular **baseline** con **PERT/CPM**
- Ejecutar **Monte Carlo** (duración y costo; ruta crítica por iteración)
- Registrar avance real y costos (**EVM**: PV, EV, AC, SV, CV, SPI, CPI + **EAC** y **EAC_mc**)
- Visualizar **histogramas**, **curvas S** y un **dashboard** integral

---


## Cómo ejecutar

**Ejecuta las simulaciones en línea:**  
[**App de Streamlit – Proyecto Final**](https://simulador-evm-mc.streamlit.app)  

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app/Home.py
```

---

## Flujo de uso

1. **Definición de Proyecto**: edita la tabla (IDs, predecesoras separadas por coma, O/M/P).
2. **Baseline (CPM)**: calcula ES/EF/LS/LF, holguras y **ruta crítica**.
3. **Simulación Monte Carlo**: define N/semilla/distribución y ejecuta.
4. **EVM**: registra `percent_complete` y `actual_cost_to_date`; obtiene PV/EV/AC, SPI/CPI, EAC y **EAC_mc**.
5. **Dashboard**: consulta KPIs y gráficos clave. Exporta CSVs si necesitas.

---

## Estructura del repo (resumen)

```
app/                # Código de la app
  core/             # Lógica de dominio: CPM, MC, EVM
  services/         # Estado y E/S
  ui/               # Widgets y gráficos plotly
  utils/            # Validaciones y utilidades
data/               # Ejemplos y estado
tests/              # Pruebas (pytest)
docs/               # Plantillas de reporte y video
```

---

## FAQ

- **Ciclos en el grafo**: revisa tus `predecessors`; la app valida aciclicidad.
- **IDs duplicadas**: cada actividad debe tener un `id` único.
- **PV o AC cero**: SPI/CPI pueden no estar definidos; revisa datos y fecha de corte.
- **Error de importación en páginas**: el paquete `app/` trae `__init__.py` para evitar `ModuleNotFoundError`.
- **Distribución PERT**: se usa Beta-PERT (λ=4). Alternativamente triangular.

---

## Licencia
MIT
