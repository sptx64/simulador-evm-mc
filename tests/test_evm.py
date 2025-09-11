import pandas as pd
from core.evm import compute_pv, compute_ev_ac, metrics

def test_evm_basic():
    sched = pd.DataFrame({
        "fecha": pd.date_range("2025-01-01", periods=3, freq="D"),
        "peso": [0.2,0.5,0.3]
    })
    pv = compute_pv(sched, bac=1000.0)
    avances = pd.DataFrame({
        "id":["A","B","C"],
        "fecha_pct": pd.date_range("2025-01-01", periods=3, freq="D"),
        "pct_completo":[0.2,0.4,0.3],
        "acumulado_AC":[100,300,700],
    })
    ev, ac = compute_ev_ac(avances)
    df = metrics(pv.set_index("fecha")["pv"], ev, ac, 1000.0)
    assert "SPI" in df.columns and "CPI" in df.columns
