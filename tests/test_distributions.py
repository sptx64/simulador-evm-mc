import numpy as np
from core.distributions import sample_triangular

def test_triangular_basic():
    o = [1, 2]; m = [2, 3]; p = [3, 5]
    s = sample_triangular(o, m, p, size=100)
    assert s.shape == (100, 2)
    assert np.all(s >= np.array(o) - 1e-9)
    assert np.all(s <= np.array(p) + 1e-9)
