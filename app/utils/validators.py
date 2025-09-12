from __future__ import annotations
from typing import List
import networkx as nx
import pandas as pd

def _norm_preds(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return []
    s = str(val).strip()
    if s == "" or s.lower() in {"nan", "none"}:
        return []
    s = s.replace(";", ",")
    return [x.strip() for x in s.split(",") if x.strip()]

def validate_project_df(df) -> List[str]:
    errors = []
    if df is None or len(df) == 0:
        errors.append("El proyecto está vacío.")
        return errors

    # IDs únicas
    ids = df["id"].astype(str).tolist()
    if len(ids) != len(set(ids)):
        errors.append("Existen IDs de actividades duplicadas.")

    # Números no negativos
    for col in ["dur_o","dur_m","dur_p","cost_o","cost_m","cost_p"]:
        if (df[col] < 0).any():
            errors.append(f"Valores negativos detectados en '{col}'.")

    # Reglas O ≤ M ≤ P para duraciones y costos
    for _, row in df.iterrows():
        o, m, p = float(row["dur_o"]), float(row["dur_m"]), float(row["dur_p"])
        if not (o <= m <= p):
            errors.append(f"[{row['id']}] Duraciones no cumplen O≤M≤P (dur_o={o}, dur_m={m}, dur_p={p}).")
        o, m, p = float(row["cost_o"]), float(row["cost_m"]), float(row["cost_p"])
        if not (o <= m <= p):
            errors.append(f"[{row['id']}] Costos no cumplen O≤M≤P (cost_o={o}, cost_m={m}, cost_p={p}).")

    # Predecesoras existentes
    idset = set(ids)
    for _, row in df.iterrows():
        preds = _norm_preds(row.get("predecessors",""))
        for p in preds:
            if p not in idset:
                errors.append(f"La predecesora '{p}' no existe (actividad {row['id']}).")

    # Acriticidad del grafo
    try:
        G = nx.DiGraph()
        for _, row in df.iterrows():
            G.add_node(str(row["id"]))
        for _, row in df.iterrows():
            for p in _norm_preds(row.get("predecessors","")):
                G.add_edge(p, str(row["id"]))
        if not nx.is_directed_acyclic_graph(G):
            errors.append("El grafo de actividades NO es acíclico (hay ciclos).")
    except Exception:
        errors.append("Error construyendo el grafo de actividades.")

    return errors
