from fastapi import HTTPException

from app.engines.wallpaper_math import paste_liters, roll_count
from app.repositories import history, rolls, settings_repo, walls

COVERAGE_KEY = "paste_coverage"


def _resolve_coverage(paste_coverage):
    """Explicit request value wins; otherwise the configured default."""
    if paste_coverage is not None:
        return float(paste_coverage)
    raw = settings_repo.get_all().get(COVERAGE_KEY)
    try:
        return float(raw)
    except (TypeError, ValueError):
        raise HTTPException(422, "paste coverage not configured")


def run_estimate(wall_id: int, roll_id: int, save: bool, note: str,
                 paste_enabled: bool = False, paste_coverage=None):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    calc = roll_count(
        wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"]
    )
    paste = None
    if paste_enabled:
        coverage = _resolve_coverage(paste_coverage)
        try:
            paste = paste_liters(wall["perimeter"], wall["height"], wall.get("door_area") or 0.0, coverage)
        except ValueError as e:
            raise HTTPException(422, str(e))
    run_id = None
    if save:
        # Net area, coverage, liters and rolls persist in one and the same run.
        run_id = history.insert_run(
            wall_id, roll_id, {**calc, "paste": paste, "wall_id": wall_id, "roll_id": roll_id}, note
        )
    return {"wall": wall, "roll": roll, "run_id": run_id, **calc, "paste": paste}
