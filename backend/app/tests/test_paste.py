import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="wp-paste-test-")

import pytest
from fastapi import HTTPException

from app import seed
from app.engines.paste_math import net_area_m2, paste_liters
from app.repositories import history, settings_repo
from app.services import estimate_service

seed.init_db()


def test_net_area_subtracts_door_openings():
    assert net_area_m2(16.0, 2.7, 1.9) == pytest.approx(41.3)
    assert net_area_m2(16.0, 2.7, 0.0) == pytest.approx(43.2)


def test_paste_liters_rounds_up():
    assert paste_liters(41.3, 5.0) == 9
    assert paste_liters(40.0, 5.0) == 8
    assert paste_liters(0.0, 5.0) == 0


def test_paste_liters_rejects_nonpositive_coverage():
    with pytest.raises(ValueError):
        paste_liters(10.0, 0.0)
    with pytest.raises(ValueError):
        paste_liters(10.0, -2.0)


def test_paste_liters_rejects_negative_net_area():
    with pytest.raises(ValueError):
        paste_liters(-0.1, 5.0)


def test_estimate_paste_off_matches_base_rolls():
    r = estimate_service.run_estimate(1, 1, False, "", paste_enabled=False)
    assert r["rolls"] == 11
    assert "paste" not in r


def test_estimate_paste_on_saved_in_same_run():
    before = len(history.list_runs(1000))
    r = estimate_service.run_estimate(1, 1, True, "t", paste_enabled=True, coverage=5.0)
    assert r["paste"]["net_area_m2"] == pytest.approx(41.3)
    assert r["paste"]["coverage_m2_per_l"] == 5.0
    assert r["paste"]["liters"] == 9
    runs = history.list_runs(1000)
    assert len(runs) == before + 1
    run = history.get_run(r["run_id"])
    assert run["result"]["rolls"] == 11
    assert run["result"]["paste"]["liters"] == 9
    assert run["result"]["paste"]["net_area_m2"] == pytest.approx(41.3)
    # Changing the default coverage afterwards must not move the stored run.
    settings_repo.set_pairs({"paste_coverage_m2_per_l": "8"})
    again = history.get_run(r["run_id"])
    assert again["result"]["paste"]["liters"] == 9
    assert again["result"]["paste"]["coverage_m2_per_l"] == 5.0


def test_estimate_rejects_nonpositive_coverage_without_history():
    before = len(history.list_runs(1000))
    for bad in (0.0, -1.5):
        with pytest.raises(HTTPException):
            estimate_service.run_estimate(1, 1, True, "", paste_enabled=True, coverage=bad)
    assert len(history.list_runs(1000)) == before


def test_estimate_rejects_negative_net_area_without_history():
    # Seed wall 4 registers door openings larger than its gross area.
    before = len(history.list_runs(1000))
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(4, 1, True, "", paste_enabled=True, coverage=5.0)
    assert len(history.list_runs(1000)) == before


def test_estimate_falls_back_to_default_coverage():
    settings_repo.set_pairs({"paste_coverage_m2_per_l": "7"})
    r = estimate_service.run_estimate(1, 1, False, "", paste_enabled=True)
    assert r["paste"]["coverage_m2_per_l"] == 7.0
    assert r["paste"]["liters"] == 6
