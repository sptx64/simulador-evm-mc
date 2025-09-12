import numpy as np
import plotly.graph_objects as go
import pandas as pd

def hist_plotly(data, title, x_title):
    hist = go.Figure()
    hist.add_trace(go.Histogram(x=data))
    hist.update_layout(title=title, xaxis_title=x_title, yaxis_title="Frecuencia", bargap=0.02)
    return hist

def cdf_plotly(data, title, x_title):
    arr = np.array(data, dtype=float)
    arr = np.sort(arr)
    y = np.linspace(0, 1, len(arr), endpoint=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=arr, y=y, mode="lines", name="CDF"))
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title="Probabilidad acumulada")
    return fig

def bar_plotly(labels, values, title, x_title, y_title):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=values))
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title)
    return fig

def evm_s_curve_plotly(pv_series: pd.Series, EV: float, AC: float, cut_time: int):
    fig = go.Figure()
    # PV acumulado
    x = pv_series.index
    y = pv_series.cumsum()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="PV"))
    # EV y AC como puntos (a la fecha)
    ct = int(min(max(0, cut_time), int(x.max()) if len(x) else 0))
    fig.add_trace(go.Scatter(x=[ct], y=[EV], mode="markers", name="EV", marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=[ct], y=[AC], mode="markers", name="AC", marker=dict(size=10)))
    fig.update_layout(title="Curva S EVM", xaxis_title="Tiempo (u.t.)", yaxis_title="Costo acumulado")
    return fig

def line_plotly(xs, ys, title, x_title, y_title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=title))
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title)
    return fig
