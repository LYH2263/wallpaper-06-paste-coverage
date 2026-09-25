from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.repositories import settings_repo

router = APIRouter()


class SettingIn(BaseModel):
    value: str


@router.get("/settings")
def settings():
    return settings_repo.get_all()


@router.put("/settings/{key}")
def put_setting(key: str, body: SettingIn):
    if key == "paste_coverage":
        try:
            coverage = float(body.value)
        except ValueError:
            raise HTTPException(422, "paste coverage must be a number")
        if coverage <= 0:
            raise HTTPException(422, "paste coverage must be > 0")
    settings_repo.set_value(key, body.value)
    return {key: body.value}
