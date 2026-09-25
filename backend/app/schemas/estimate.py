from typing import Optional

from pydantic import BaseModel


class EstimateRequest(BaseModel):
    wall_id: int
    roll_id: int
    save: bool = False
    note: str = ""
    paste_enabled: bool = False
    paste_coverage: Optional[float] = None  # defaults to the configured setting
