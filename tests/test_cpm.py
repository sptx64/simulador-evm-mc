from core.cpm import cpm_forward, cpm_backward

def test_cpm_small():
    nodes = ["A","B","C"]
    edges = {"A":[], "B":["A"], "C":["B"]}  # deps (preds) por nodo
    d = {"A":2.0,"B":3.0,"C":4.0}
    ES, EF = cpm_forward(nodes, edges, d)
    T = max(EF.values())
    LS, LF = cpm_backward(nodes, edges, d, T)
    assert round(T,2) == 9.0
    slack = {i: LS[i]-ES[i] for i in nodes}
    assert all(abs(s) < 1e-9 for s in slack.values())
