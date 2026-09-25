from fastapi import APIRouter, Body
from app.repositories import settings_repo

router = APIRouter()


@router.get("/settings")
def settings():
    return settings_repo.get_all()


@router.put("/settings")
def update_settings(pairs: dict[str, str] = Body(...)):
    settings_repo.set_pairs(pairs)
    return settings_repo.get_all()
