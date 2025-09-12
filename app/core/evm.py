from __future__ import annotations
from typing import Dict, Optional
import numpy as np
import pandas as pd

from app.core.models import Project

def compute_bac(project: Project, policy: str = "m") -> tuple[Dict[str,float], float]:
    """BAC por actividad y total. policy: 'm' o 'pert'."""
    bac_map = {}
    for a in project.activities:
        bac_map[a.id] = a.cost_m if policy == "m" else a.pert_cost()
    total = float(sum(bac_map.values()))
    return bac_map, total

def build_pv_profile(*args, **kwargs):
    """Compatibilidad retro: la función real vive en cpm.build_cost_profile."""
    from app.core.cpm import build_cost_profile
    return build_cost_profile(*args, **kwargs)

def compute_evm_kpis(
    progress_df: pd.DataFrame,
    pv_profile: pd.Series,
    bac_map: Dict[str,float],
    bac_total: float,
    cut_time: int,
    mc_cost_samples: Optional[list[float]] = None
) -> Dict:
    """Calcula PV, EV, AC, SV, CV, SPI, CPI y EACs."""
    # EV y AC por actividad
    ev = 0.0
    ac = 0.0
    for _, row in progress_df.iterrows():
        aid = str(row["activity_id"])
        pc = float(row.get("percent_complete", 0.0)) / 100.0
        ac_i = float(row.get("actual_cost_to_date", 0.0))
        bac_i = bac_map.get(aid, 0.0)
        ev += bac_i * pc
        ac += ac_i

    # PV acumulado hasta cut_time
    if pv_profile is not None and len(pv_profile) > 0:
        ct = int(min(max(0, cut_time), pv_profile.index.max()))
        pv = float(pv_profile.iloc[:ct+1].sum())
    else:
        pv = 0.0

    sv = ev - pv
    cv = ev - ac
    spi = (ev / pv) if pv > 0 else None
    cpi = (ev / ac) if ac > 0 else None

    eac1 = None
    eac2 = None
    if cpi and cpi > 0:
        eac1 = ac + (bac_total - ev) / cpi
        eac2 = bac_total / cpi

    eac_mc = None
    if mc_cost_samples and len(mc_cost_samples) > 0:
        s = np.array(mc_cost_samples, dtype=float)
        eac_mc = {
            "p50": float(np.percentile(s, 50)),
            "p80": float(np.percentile(s, 80))
        }

    return {
        "PV": pv, "EV": ev, "AC": ac,
        "SV": sv, "CV": cv,
        "SPI": spi if spi is not None else None,
        "CPI": cpi if cpi is not None else None,
        "EAC_cost_1": eac1,
        "EAC_cost_2": eac2,
        "EAC_mc_cost": eac_mc,
        "BAC": bac_total,
        "cut_time": int(cut_time)
    }
