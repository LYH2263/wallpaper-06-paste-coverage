from fastapi import HTTPException

from app.engines.paste_math import net_area_m2, paste_liters
from app.engines.wallpaper_math import roll_count
from app.repositories import history, rolls, settings_repo, walls

DEFAULT_COVERAGE_M2_PER_L = 5.0


def run_estimate(wall_id: int, roll_id: int, save: bool, note: str,
                 paste_enabled: bool = False, coverage: float | None = None):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    result = roll_count(
        wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"]
    )
    if paste_enabled:
        cov = coverage
        if cov is None:
            raw = settings_repo.get_all().get("paste_coverage_m2_per_l")
            cov = float(raw) if raw is not None else DEFAULT_COVERAGE_M2_PER_L
        net = net_area_m2(wall["perimeter"], wall["height"], wall.get("door_area_m2") or 0.0)
        try:
            liters = paste_liters(net, cov)
        except ValueError as exc:
            raise HTTPException(422, str(exc))
        result["paste"] = {
            "net_area_m2": net,
            "coverage_m2_per_l": cov,
            "liters": liters,
        }
    run_id = None
    if save:
        run_id = history.insert_run(wall_id, roll_id, {**result, "wall_id": wall_id, "roll_id": roll_id}, note)
    return {"wall": wall, "roll": roll, "run_id": run_id, **result}
