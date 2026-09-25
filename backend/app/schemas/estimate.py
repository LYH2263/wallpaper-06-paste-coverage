from pydantic import BaseModel


class EstimateRequest(BaseModel):
    wall_id: int
    roll_id: int
    save: bool = False
    note: str = ""
    paste_enabled: bool = False
    coverage: float | None = None
