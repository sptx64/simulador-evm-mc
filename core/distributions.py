import numpy as np

def sample_triangular(o, m, p, size: int):
    o = np.asarray(o); m = np.asarray(m); p = np.asarray(p)
    u = np.random.random(size=(size, len(o)))
    c = (m - o) / (p - o + 1e-12)
    left = o + np.sqrt(u * (p - o) * (m - o))
    right = p - np.sqrt((1 - u) * (p - o) * (p - m))
    return np.where(u <= c, left, right)

def _alpha_beta_pert(o, m, p, lam=4.0):
    mean = (o + lam * m + p) / (lam + 2)
    a = 1 + lam * (mean - o) / (p - o + 1e-12)
    b = 1 + lam * (p - mean) / (p - o + 1e-12)
    return a, b

def sample_beta_pert(o, m, p, size: int, lam=4.0):
    o = np.asarray(o); m = np.asarray(m); p = np.asarray(p)
    a, b = _alpha_beta_pert(o, m, p, lam)
    u = np.random.beta(a, b, size=(size, len(o)))
    return o + u * (p - o)
