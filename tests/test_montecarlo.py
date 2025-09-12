import pandas as pd
from app.utils.helpers import project_from_df
from app.core.montecarlo import run_montecarlo as run_monte_carlo  # alias para nombre amigable

def test_mc_basic():
    df = pd.DataFrame({
        "id": ["A","B"],
        "name": ["A","B"],
        "predecessors": ["","A"],
        "dur_o":[1,2], "dur_m":[2,3], "dur_p":[3,4],
        "cost_o":[10,20], "cost_m":[20,30], "cost_p":[30,40]
    })
    project = project_from_df(df)
    res = run_monte_carlo(project, N=200, seed=1, dist="triangular")
    assert len(res["durations"]) == 200
    assert len(res["costs"]) == 200
    assert res["duration_stats"]["p10"] <= res["duration_stats"]["p50"] <= res["duration_stats"]["p90"]
