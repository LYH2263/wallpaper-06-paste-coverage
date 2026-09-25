"""Paste (胶浆) usage: net wall area over coverage rate, rounded up to liters."""

from app.engines.helpers import ceil_units


def net_area_m2(perimeter: float, height: float, door_area_m2: float = 0.0) -> float:
    """Gross area (usable perimeter x floor height) minus registered door openings."""
    gross = float(perimeter) * float(height)
    return round(gross - float(door_area_m2 or 0.0), 3)


def paste_liters(net_area: float, coverage_m2_per_l: float) -> int:
    """Liters of paste = ceil(net area / coverage). Rejects invalid inputs."""
    coverage = float(coverage_m2_per_l)
    if coverage <= 0:
        raise ValueError("coverage must be positive")
    if float(net_area) < 0:
        raise ValueError("net area must not be negative")
    return ceil_units(float(net_area) / coverage)
