from core.montecarlo import simulate
from core.distributions import sample_triangular

def test_simulate_runs():
    wbs = [
        {"id":"A","t_o":1,"t_m":2,"t_p":3},
        {"id":"B","t_o":2,"t_m":3,"t_p":4},
    ]
    edges = {"A":[], "B":["A"]}
    durations, crit = simulate(wbs, edges, sample_triangular, n_iter=50, seed=123)
    assert len(durations) == 50
    assert set(crit.keys()) == {"A","B"}
