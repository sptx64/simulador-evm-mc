from collections import defaultdict, deque

def _preds(edges):
    rev = defaultdict(list)
    for u, vs in edges.items():
        for v in vs:
            rev[v].append(u)
    return rev

def topological_order(nodes, edges):
    indeg = {n:0 for n in nodes}
    for u, vs in edges.items():
        for v in vs:
            indeg[v] = indeg.get(v, 0) + 1
    q = deque([n for n in nodes if indeg.get(n,0)==0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in edges.get(u, []):
            indeg[v] -= 1
            if indeg[v]==0:
                q.append(v)
    if len(order) != len(nodes):
        raise ValueError("Ciclo detectado en precedencias")
    return order

def cpm_forward(nodes, edges, durations):
    preds = _preds(edges)
    ES, EF = {}, {}
    for u in topological_order(nodes, edges):
        ES[u] = max((EF.get(p, 0) for p in preds.get(u, [])), default=0)
        EF[u] = ES[u] + durations[u]
    return ES, EF

def cpm_backward(nodes, edges, durations, project_duration):
    LS, LF = {}, {}
    order = topological_order(nodes, edges)
    for u in reversed(order):
        succ = [s for s, vs in edges.items() if u in vs]  # sucesores del grafo directo
        LF[u] = min((LS[s] for s in succ), default=project_duration)
        LS[u] = LF[u] - durations[u]
    return LS, LF

def critical_path(slack):
    return [n for n, s in slack.items() if abs(s) < 1e-9]
