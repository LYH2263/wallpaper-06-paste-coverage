import pytest

from app.engines.wallpaper_math import paste_liters, roll_count


def test_plain_master_bed():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    assert r["drops"] == 31
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11


def test_pattern_wall():
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64)
    assert r["drops"] == 38
    assert r["drop_len_m"] == 3.44
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19


def test_paste_liters_basic():
    p = paste_liters(16.0, 2.7, 1.8, 5.0)
    assert p["gross_area_m2"] == 43.2
    assert p["door_area_m2"] == 1.8
    assert p["net_area_m2"] == 41.4
    assert p["coverage_m2_per_l"] == 5.0
    assert p["liters"] == 9  # ceil(41.4 / 5)


def test_paste_liters_exact_division_not_rounded_up():
    assert paste_liters(10.0, 2.5, 0.0, 5.0)["liters"] == 5  # 25 / 5 exactly


def test_paste_zero_net_area():
    assert paste_liters(4.0, 2.5, 10.0, 5.0)["liters"] == 0


def test_paste_non_positive_coverage_rejected():
    with pytest.raises(ValueError):
        paste_liters(16.0, 2.7, 1.8, 0.0)
    with pytest.raises(ValueError):
        paste_liters(16.0, 2.7, 1.8, -1.0)


def test_paste_negative_net_area_rejected():
    with pytest.raises(ValueError):
        paste_liters(4.0, 2.5, 99.0, 5.0)
