import numpy as np
from .cpm import cpm_forward, cpm_backward

def simulate(wbs, edges, sampler, n_iter=2000, seed=None):
    rng = np.random.default_rng(seed)
    ids = [str(r["id"]).strip() for r in wbs]
    o = np.array([float(r["t_o"]) for r in wbs])
    m = np.array([float(r["t_m"]) for r in wbs])
    p = np.array([float(r["t_p"]) for r in wbs])

    durations_samples = sampler(o, m, p, n_iter)  # (n_iter, n_tasks)
    proj_duration = np.empty(n_iter)
    criticity = {i:0 for i in ids}

    for k in range(n_iter):
        dmap = {ids[j]: float(durations_samples[k, j]) for j in range(len(ids))}
        ES, EF = cpm_forward(ids, edges, dmap)
        T = max(EF.values())
        LS, LF = cpm_backward(ids, edges, dmap, T)
        slack = {i: LS[i] - ES[i] for i in ids}
        for i, s in slack.items():
            if abs(s) < 1e-9:
                criticity[i] += 1
        proj_duration[k] = T
    return proj_duration, criticity
