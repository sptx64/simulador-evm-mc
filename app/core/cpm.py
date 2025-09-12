from __future__ import annotations
from typing import Dict, List, Tuple
import pandas as pd
import networkx as nx

from app.core.models import Project, Activity

# -----------------------
# CPM / PERT
# -----------------------

def build_graph(project: Project, durations: Dict[str, float] | None = None) -> nx.DiGraph:
    """Construye el DAG de actividades. 'durations' permite sustituir duraciones por iteración MC."""
    G = nx.DiGraph()
    for act in project.activities:
        dur = durations[act.id] if durations and act.id in durations else act.pert_time()
        G.add_node(act.id, duration=float(dur), name=act.name)
    ids = {a.id for a in project.activities}
    for act in project.activities:
        for p in act.predecessors:
            if not p:
                continue
            if p not in ids:
                raise ValueError(f"La predecesora '{p}' no existe (actividad {act.id}).")
            G.add_edge(p, act.id)
    return G

def topological_order_or_raise(G: nx.DiGraph) -> List[str]:
    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("El grafo de actividades tiene al menos un ciclo. Corrige predecesoras.")
    return list(nx.topological_sort(G))

def cpm_tables(G: nx.DiGraph) -> Tuple[Dict[str, Dict], float, List[str]]:
    """Calcula ES/EF/LS/LF/Holgura y ruta crítica."""
    order = topological_order_or_raise(G)

    ES, EF = {}, {}
    for n in order:
        preds = list(G.predecessors(n))
        ES[n] = max([EF[p] for p in preds], default=0.0)
        d = G.nodes[n]["duration"]
        EF[n] = ES[n] + d

    project_duration = max(EF.values()) if EF else 0.0

    LS, LF = {}, {}
    for n in reversed(order):
        succs = list(G.successors(n))
        d = G.nodes[n]["duration"]
        if len(succs) == 0:
            LF[n] = project_duration
        else:
            LF[n] = min([LS[s] for s in succs])
        LS[n] = LF[n] - d

    slack = {n: LS[n] - ES[n] for n in order}
    critical_path = [n for n in order if abs(slack[n]) < 1e-9]

    table = []
    for n in order:
        table.append({
            "id": n,
            "name": G.nodes[n].get("name",""),
            "duration": G.nodes[n]["duration"],
            "ES": ES[n],
            "EF": EF[n],
            "LS": LS[n],
            "LF": LF[n],
            "holgura": slack[n]
        })

    return {row["id"]: row for row in table}, project_duration, critical_path

def compute_baseline_cpm(project: Project) -> Dict:
    """Calcula baseline con duraciones PERT por defecto."""
    G = build_graph(project)
    table, duration, critical_path = cpm_tables(G)
    return {
        "duration": duration,
        "critical_path": critical_path,
        "table": list(table.values()),
        "time_unit": project.time_unit,
        "currency": project.currency
    }

def build_cost_profile(project: Project, baseline: Dict, cost_policy: str = "m") -> pd.Series:
    """Distribuye linealmente el BAC de cada actividad en su duración base (discreta, 1 u.t.)."""
    # Mapas rápidos
    acts = project.activity_map()
    rows = {r["id"]: r for r in baseline["table"]}
    T = int(round(baseline["duration"]))
    if T <= 0:
        return pd.Series(dtype=float)

    pv = pd.Series([0.0]*(T+1))  # índice 0..T
    for aid, row in rows.items():
        d = max(1, int(round(row["duration"])))  # duración en enteros
        es = int(round(row["ES"]))
        ef = es + d
        act = acts[aid]
        if cost_policy == "pert":
            bac_i = act.pert_cost()
        else:
            bac_i = act.cost_m
        # Distribuir uniformemente por periodos [es+1 .. ef]
        if ef > es:
            per = bac_i / (ef - es)
            for t in range(es+1, ef+1):
                if t <= T:
                    pv.iloc[t] += per

    pv.index.name = "time"
    pv.name = "PV"
    return pv
