from __future__ import annotations
import json
import pandas as pd
from pathlib import Path

EXPECTED_COLS = ["id","name","predecessors","dur_o","dur_m","dur_p","cost_o","cost_m","cost_p"]

def _try_fix_rows(raw: str) -> str:
    # Reconstruye líneas con más de 9 columnas juntando el campo 'predecessors' (y posibles comas internas).
    out_lines = []
    lines = [l for l in raw.splitlines() if l.strip() != ""]
    if not lines:
        return raw
    header = lines[0]
    out_lines.append(header)
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) == 9:
            out_lines.append(line)
            continue
        if len(parts) < 9:
            # no podemos arreglarla de forma segura
            out_lines.append(line)
            continue
        # Tenemos más de 9: unimos todo lo que excede entre 'name' y el resto en 'predecessors'
        # Esperamos formato: id, name, predecessors, dur_o, dur_m, dur_p, cost_o, cost_m, cost_p
        # Tomamos últimos 6 campos como numéricos y el resto entre name..antes de esos 6 como predecessors
        tail = parts[-6:]  # dur_o..cost_p
        head = parts[:2]   # id, name
        middle = parts[2:-6]
        # Si el 'middle' tiene comas, las unimos con ';' para que la app luego las convierta
        predecessors = ";".join([p.strip() for p in middle if p.strip() != ""])
        fixed = head + [predecessors] + tail
        out_lines.append(",".join(fixed))
    return "\n".join(out_lines)

def load_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception:
        # Fallback: intentar arreglar filas con más columnas
        raw = Path(path).read_text(encoding="utf-8")
        fixed_raw = _try_fix_rows(raw)
        return pd.read_csv(pd.io.common.StringIO(fixed_raw))

def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def read_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
