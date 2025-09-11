import pandas as pd

def compute_pv(schedule: pd.DataFrame, bac: float) -> pd.DataFrame:
    s = schedule.sort_values("fecha").copy()
    if abs(s["peso"].sum() - 1.0) > 1e-6:
        s["peso"] = s["peso"] / s["peso"].sum()
    s["pv"] = bac * s["peso"].cumsum()
    return s[["fecha","pv"]]

def compute_ev_ac(avances: pd.DataFrame):
    # Supone entradas por fecha de porcentaje completado incremental (no acumulado)
    ev = avances.groupby("fecha_pct")["pct_completo"].sum().cumsum()
    ac = avances.groupby("fecha_pct")["acumulado_AC"].max()
    return ev, ac

def metrics(pv_t: pd.Series, ev_t: pd.Series, ac_t: pd.Series, bac: float) -> pd.DataFrame:
    df = pd.DataFrame({"PV": pv_t, "EV": ev_t, "AC": ac_t}).sort_index().fillna(method="ffill")
    df["SPI"] = df["EV"] / df["PV"].clip(lower=1e-9)
    df["CPI"] = df["EV"] / df["AC"].replace(0, pd.NA)
    df["EAC_BAC_over_CPI"] = bac / df["CPI"]
    df["ETC"] = df["EAC_BAC_over_CPI"] - df["AC"]
    return df
