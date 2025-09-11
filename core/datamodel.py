from typing import TypedDict, List

class WBSRow(TypedDict):
    id: str
    desc: str
    deps: str
    t_o: float
    t_m: float
    t_p: float
    c_o: float
    c_m: float
    c_p: float
