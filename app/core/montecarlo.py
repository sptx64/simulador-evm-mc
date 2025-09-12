from __future__ import annotations
from typing import Dict, List
import numpy as np

from app.core.models import Project, RiskEvent
from app.core.cpm import build_graph, cpm_tables

def _triangular_safe(o: float, m: float, p: float, size: int, rng: np.random.Generator) -> np.ndarray:
    # Asegurar orden y modo válido
    left = min(o, m, p)
    right = max(o, m, p)
    mode = min(max(m, left), right)
    if right == left:
        return np.full(size, mode)
    return rng.triangular(left=left, mode=mode, right=right, size=size)

def _beta_pert_safe(o: float, m: float, p: float, size: int, rng: np.random.Generator, lam: float = 4.0) -> np.ndarray:
    # Ordenar para asegurar o<=m<=p
    o_, m_, p_ = sorted([o, m, p])
    if p_ == o_:
        return np.full(size, m_)
    alpha = 1 + lam * (m_ - o_) / (p_ - o_ + 1e-12)
    beta = 1 + lam * (p_ - m_) / (p_ - o_ + 1e-12)
    # Evitar parámetros inválidos
    alpha = max(alpha, 1e-6)
    beta = max(beta, 1e-6)
    x = rng.beta(alpha, beta, size=size)
    return o_ + x * (p_ - o_)

def _sample_activity(o: float, m: float, p: float, size: int, dist: str, rng: np.random.Generator) -> np.ndarray:
    if dist == "triangular":
        return _triangular_safe(o, m, p, size, rng)
    elif dist == "beta-pert":
        return _beta_pert_safe(o, m, p, size, rng)
    else:
        raise ValueError("Distribución no soportada.")

def _apply_risks(dur_map: Dict[str, float],
                 cost_map: Dict[str, float],
                 risks: List[RiskEvent],
                 rng: np.random.Generator) -> None:
    for r in risks:
        hit = rng.random() < max(0.0, min(1.0, r.prob))
        if not hit:
            continue
        targets: List[str]
        if isinstance(r.applies_to, list):
            targets = r.applies_to
        else:
            targets = list(dur_map.keys()) if str(r.applies_to).upper() == "GLOBAL" else [str(r.applies_to)]
        for t in targets:
            if t in dur_map:
                dur_map[t] += max(0.0, r.impact_time)
            if t in cost_map:
                cost_map[t] += max(0.0, r.impact_cost)

def run_monte_carlo(project: Project, N: int = 5000, seed: int = 42, dist: str = "triangular", risks_df=None) -> Dict:
    rng = np.random.default_rng(seed)
    acts = project.activities

    # Preparar riesgos
    risks: List[RiskEvent] = []
    if risks_df is not None and len(risks_df) > 0:
        for _, r in risks_df.iterrows():
            try:
                applies = r.get("applies_to", "GLOBAL")
                if isinstance(applies, str) and applies and applies != "GLOBAL":
                    applies = [x.strip() for x in applies.replace(";", ",").split(",") if x.strip()]
                risks.append(RiskEvent(
                    name=str(r.get("name","Riesgo")),
                    prob=float(r.get("prob",0.0)),
                    impact_time=float(r.get("impact_time",0.0)),
                    impact_cost=float(r.get("impact_cost",0.0)),
                    applies_to=applies if applies else "GLOBAL"
                ))
            except Exception:
                # Ignorar filas inválidas de riesgos
                pass

    durations = []
    costs = []
    critical_paths = []

    # Muestreo vectorizado por actividad
    dur_samples = {a.id: _sample_activity(a.dur_o, a.dur_m, a.dur_p, N, dist, rng) for a in acts}
    cost_samples = {a.id: _sample_activity(a.cost_o, a.cost_m, a.cost_p, N, "triangular", rng) for a in acts}

    for i in range(N):
        dur_map = {aid: float(dur_samples[aid][i]) for aid in dur_samples}
        cost_map = {aid: float(cost_samples[aid][i]) for aid in cost_samples}

        if risks:
            _apply_risks(dur_map, cost_map, risks, rng)

        # CPM para esta iteración
        G = build_graph(project, durations=dur_map)
        table, d, cp = cpm_tables(G)
        durations.append(d)
        c_total = sum(cost_map.values())
        costs.append(c_total)
        critical_paths.append(cp)

    durations = np.array(durations, dtype=float)
    costs = np.array(costs, dtype=float)

    def stats(arr: np.ndarray) -> Dict[str, float]:
        return {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
            "p10": float(np.percentile(arr, 10)),
            "p50": float(np.percentile(arr, 50)),
            "p80": float(np.percentile(arr, 80)),
            "p90": float(np.percentile(arr, 90)),
        }

    return {
        "durations": durations.tolist(),
        "costs": costs.tolist(),
        "critical_paths": [list(x) for x in critical_paths],
        "duration_stats": stats(durations),
        "cost_stats": stats(costs),
        "N": int(N),
        "seed": int(seed),
        "dist": dist
    }
