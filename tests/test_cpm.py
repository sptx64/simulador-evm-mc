import pandas as pd
from app.utils.helpers import project_from_df
from app.core.cpm import compute_baseline_cpm

def test_cpm_small():
    df = pd.DataFrame({
        "id": ["A","B","C","D"],
        "name": ["A","B","C","D"],
        "predecessors": ["","A","A","B,C"],
        "dur_o": [1,1,1,1],
        "dur_m": [2,2,2,2],
        "dur_p": [3,3,3,3],
        "cost_o":[0,0,0,0],
        "cost_m":[0,0,0,0],
        "cost_p":[0,0,0,0],
    })
    project = project_from_df(df)
    bl = compute_baseline_cpm(project)
    assert bl["duration"] > 0
    assert isinstance(bl["critical_path"], list)
    ids = set(df["id"])
    assert all(n in ids for n in bl["critical_path"])
