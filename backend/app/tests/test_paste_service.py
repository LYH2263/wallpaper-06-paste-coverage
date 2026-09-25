import pytest
from fastapi import HTTPException

from app import seed
from app.db import connect
from app.repositories import history, settings_repo
from app.services import estimate_service


@pytest.fixture()
def db(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    return tmp_path / "test.db"


def _add_wall(name, perimeter, height, door_area):
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO walls(name,perimeter,height,door_area) VALUES (?,?,?,?)",
            (name, perimeter, height, door_area),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def test_paste_off_rolls_match_pre_change(db):
    r = estimate_service.run_estimate(1, 1, False, "")
    assert r["paste"] is None
    assert r["rolls"] == 11  # untouched roll math


def test_paste_on_uses_default_coverage(db):
    r = estimate_service.run_estimate(1, 1, False, "", paste_enabled=True)
    assert r["rolls"] == 11
    assert r["paste"]["net_area_m2"] == 41.4
    assert r["paste"]["coverage_m2_per_l"] == 5.0
    assert r["paste"]["liters"] == 9


def test_trial_run_writes_nothing(db):
    estimate_service.run_estimate(1, 1, False, "", paste_enabled=True)
    assert history.list_runs() == []


def test_saved_run_keeps_areas_coverage_liters_rolls_together(db):
    r = estimate_service.run_estimate(1, 1, True, "n", paste_enabled=True)
    run = history.get_run(r["run_id"])
    assert run["result"]["rolls"] == 11
    assert run["result"]["paste"]["net_area_m2"] == 41.4
    assert run["result"]["paste"]["coverage_m2_per_l"] == 5.0
    assert run["result"]["paste"]["liters"] == 9


def test_non_positive_coverage_rejected_no_history(db):
    before = len(history.list_runs())
    with pytest.raises(HTTPException) as e:
        estimate_service.run_estimate(1, 1, True, "", paste_enabled=True, paste_coverage=0.0)
    assert e.value.status_code == 422
    assert len(history.list_runs()) == before


def test_negative_net_area_rejected_no_history(db):
    wid = _add_wall("门洞超限", 4.0, 2.5, 99.0)
    before = len(history.list_runs())
    with pytest.raises(HTTPException) as e:
        estimate_service.run_estimate(wid, 1, True, "", paste_enabled=True)
    assert e.value.status_code == 422
    assert len(history.list_runs()) == before


def test_default_coverage_change_does_not_rewrite_old_runs(db):
    r = estimate_service.run_estimate(1, 1, True, "", paste_enabled=True)
    settings_repo.set_value("paste_coverage", "8")
    # new calculations pick up the new default
    assert estimate_service.run_estimate(1, 1, False, "", paste_enabled=True)["paste"]["liters"] == 6
    # the old run still shows what was written at the time
    old = history.get_run(r["run_id"])
    assert old["result"]["paste"]["coverage_m2_per_l"] == 5.0
    assert old["result"]["paste"]["liters"] == 9
