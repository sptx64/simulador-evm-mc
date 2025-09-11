from typing import List, Dict, Tuple

def validate_wbs(df) -> tuple[bool, list[str]]:
    errors: list[str] = []
    required = {"id","desc","deps","t_o","t_m","t_p","c_o","c_m","c_p"}
    if not required.issubset(set(df.columns)):
        errors.append("Faltan columnas requeridas: " + str(required - set(df.columns)))
        return False, errors

    ids = set()
    for _, row in df.iterrows():
        i = str(row["id"]).strip()
        if i in ids:
            errors.append(f"ID duplicado: {i}")
        ids.add(i)
        o, m, p = float(row["t_o"]), float(row["t_m"]), float(row["t_p"])
        if not (o <= m <= p):
            errors.append(f"Rango inválido (o<=m<=p) en tarea {i}")
    # ciclo
    try:
        edges = build_edges(df.to_dict(orient='records'))
        # simple detección de ciclo: DFS
        if has_cycle(edges):
            errors.append("Se detectó un ciclo en las dependencias.")
    except Exception as e:
        errors.append(f"Error validando dependencias: {e}")
    return (len(errors)==0), errors

def build_edges(wbs: List[dict]) -> Dict[str, List[str]]:
    edges: Dict[str, List[str]] = {}
    all_ids = {str(r["id"]).strip() for r in wbs}
    for r in wbs:
        u = str(r["id"]).strip()
        deps = str(r.get("deps","")).strip()
        vs = [d.strip() for d in deps.split(",") if d.strip()]
        # validar que existan
        for v in vs:
            if v not in all_ids:
                raise ValueError(f"Dependencia '{v}' no existe (referida por {u})")
        edges[u] = vs  # usamos predecesores como lista asociada
    return edges

def has_cycle(edges: Dict[str, List[str]]) -> bool:
    # DFS detectando back-edges
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {u: WHITE for u in edges.keys()}

    def dfs(u):
        color[u] = GRAY
        for v in edges.get(u, []):
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    return any(dfs(u) for u in list(edges.keys()))
