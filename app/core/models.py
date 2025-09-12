from typing import List, Optional, Dict
from pydantic import BaseModel, Field, validator

# Modelos de datos Pydantic (opcional pero útil para validación)

class Activity(BaseModel):
    id: str
    name: str
    predecessors: List[str] = Field(default_factory=list)
    dur_o: float
    dur_m: float
    dur_p: float
    cost_o: float
    cost_m: float
    cost_p: float
    wbs_code: Optional[str] = None
    recursos: Optional[str] = None

    @validator("dur_o","dur_m","dur_p","cost_o","cost_m","cost_p")
    def positive(cls, v):
        if v < 0:
            raise ValueError("Valores de duración/costo deben ser no negativos.")
        return v

    def pert_time(self) -> float:
        return (self.dur_o + 4*self.dur_m + self.dur_p) / 6.0

    def pert_cost(self) -> float:
        return (self.cost_o + 4*self.cost_m + self.cost_p) / 6.0


class RiskEvent(BaseModel):
    name: str
    prob: float
    impact_time: float = 0.0
    impact_cost: float = 0.0
    applies_to: List[str] | str = "GLOBAL"


class ProgressEntry(BaseModel):
    activity_id: str
    percent_complete: float
    actual_cost_to_date: float
    actual_finish_date: Optional[str] = None


class Project(BaseModel):
    activities: List[Activity]
    baseline_start: Optional[str] = None
    time_unit: str = "u.t."
    currency: str = "USD"

    def activity_map(self) -> Dict[str, Activity]:
        return {a.id: a for a in self.activities}
