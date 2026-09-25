from fastapi import APIRouter, HTTPException

from app.engines.wallpaper_math import wall_areas
from app.repositories import walls as repo

router = APIRouter()


@router.get("/walls")
def list_walls():
    return {"items": repo.list_walls()}


@router.get("/walls/{wall_id}")
def get_wall(wall_id: int):
    row = repo.get_wall(wall_id)
    if not row:
        raise HTTPException(404)
    return {**row, **wall_areas(row["perimeter"], row["height"], row.get("door_area") or 0.0)}
