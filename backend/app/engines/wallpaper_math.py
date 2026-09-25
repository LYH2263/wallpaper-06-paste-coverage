"""Wallpaper rolls: perimeter strips, pattern repeat on drop length, strips per roll.

Paste （胶浆）: gross area = usable perimeter * height, net = gross - registered
door openings, liters = ceil(net / coverage). Paste is additive only — roll math
is untouched so disabling paste yields exactly the pre-paste rolls.
"""

from app.engines.helpers import ceil_units, floor_units


def roll_count(
    perimeter: float,
    height: float,
    roll_width: float,
    roll_length: float,
    pattern_cm: float,
) -> dict:
    if roll_width <= 0 or roll_length <= 0:
        raise ValueError("invalid roll size")
    drops = ceil_units(float(perimeter) / float(roll_width))
    pattern_m = max(0.0, float(pattern_cm) / 100.0)
    drop_len = float(height) + pattern_m
    if drop_len <= 0:
        raise ValueError("invalid drop length")
    strips_per_roll = max(1, floor_units(float(roll_length) / drop_len))
    rolls = ceil_units(drops / strips_per_roll)
    return {
        "drops": drops,
        "drop_len_m": round(drop_len, 3),
        "pattern_m": round(pattern_m, 3),
        "strips_per_roll": strips_per_roll,
        "rolls": rolls,
    }


def wall_areas(perimeter: float, height: float, door_area: float) -> dict:
    """Gross/net wall area; net subtracts registered door openings."""
    gross = float(perimeter) * float(height)
    net = gross - float(door_area)
    return {
        "gross_area_m2": round(gross, 3),
        "door_area_m2": round(float(door_area), 3),
        "net_area_m2": round(net, 3),
    }


def paste_liters(perimeter: float, height: float, door_area: float, coverage: float) -> dict:
    """Paste usage in liters: ceil(net_area / coverage). Rejects bad inputs."""
    if float(coverage) <= 0:
        raise ValueError("invalid coverage")
    areas = wall_areas(perimeter, height, door_area)
    if areas["net_area_m2"] < 0:
        raise ValueError("negative net area")
    liters = ceil_units(areas["net_area_m2"] / float(coverage))
    return {**areas, "coverage_m2_per_l": float(coverage), "liters": liters}
