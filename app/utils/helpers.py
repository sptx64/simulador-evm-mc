from __future__ import annotations
from io import BytesIO
import pandas as pd
from typing import Any
from app.core.models import Project, Activity

def parse_preds(txt: Any):
    # Trata None/NaN/'nan'/'None' como vacío; soporta ';' y ','
    if txt is None:
        return []
    try:
        if pd.isna(txt):
            return []
    except Exception:
        pass
    s = str(txt).strip()
    if s == "" or s.lower() in {"nan", "none"}:
        return []
    s = s.replace(";", ",")
    return [x.strip() for x in s.split(",") if x.strip()]

def project_from_df(df) -> Project:
    acts = []
    for _, r in df.iterrows():
        acts.append(Activity(
            id=str(r["id"]),
            name=str(r["name"]),
            predecessors=parse_preds(r.get("predecessors","")),
            dur_o=float(r["dur_o"]), dur_m=float(r["dur_m"]), dur_p=float(r["dur_p"]),
            cost_o=float(r["cost_o"]), cost_m=float(r["cost_m"]), cost_p=float(r["cost_p"]),
        ))
    return Project(activities=acts, time_unit="u.t.", currency="USD")

def to_csv_download(df) -> bytes:
    bio = BytesIO()
    df.to_csv(bio, index=False)
    return bio.getvalue()
