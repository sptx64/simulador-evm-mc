import pandas as pd
from app.utils.helpers import project_from_df
from app.core.cpm import compute_baseline_cpm, build_cost_profile
from app.core.evm import compute_bac, compute_evm_kpis

def test_evm_kpis():
    df = pd.DataFrame({
        "id": ["A","B"],
        "name": ["A","B"],
        "predecessors": ["","A"],
        "dur_o":[1,2], "dur_m":[2,3], "dur_p":[3,4],
        "cost_o":[10,20], "cost_m":[20,30], "cost_p":[30,40]
    })
    project = project_from_df(df)
    bl = compute_baseline_cpm(project)
    pv = build_cost_profile(project, bl, cost_policy="m")
    bac_map, bac_total = compute_bac(project, policy="m")
    progress = pd.DataFrame({
        "activity_id":["A","B"],
        "percent_complete":[50,0],
        "actual_cost_to_date":[8,0]
    })
    evm = compute_evm_kpis(progress, pv, bac_map, bac_total, cut_time=1, mc_cost_samples=None)
    assert "PV" in evm and "EV" in evm and "AC" in evm
    assert evm["BAC"] == bac_total
