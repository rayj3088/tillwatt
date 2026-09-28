"""Gate for step 2: wear never goes backward except across a logged replacement,
hazard rises with wear, and a full year of battery cycling stays inside [0, 1]."""

import pytest

from engine.parts import Battery
from engine.run_scene import simulate_scene
from engine.parts import SolarArray
from engine.wear import (
    WearError,
    WearState,
    battery_calendar_rate,
    battery_duty_rate,
    check_wear,
    solar_calendar_rate,
)

CLAIMED_BATTERY_CALENDAR_LIFE_YEARS = 10.0
CLAIMED_BATTERY_CYCLE_LIFE = 3000.0
CLAIMED_SOLAR_LIFE_YEARS = 25.0


def test_wear_starts_new_and_only_climbs():
    w = WearState()
    assert w.cumulative == 0.0
    prev = w.cumulative
    for _ in range(24):
        w.age(calendar_rate=0.0001, duty_rate=0.0002)
        check_wear(prev, w.cumulative, replaced=False)
        assert w.cumulative >= prev
        prev = w.cumulative


def test_wear_never_exceeds_one():
    w = WearState()
    for _ in range(100):
        w.age(calendar_rate=0.05, duty_rate=0.05)
    assert w.cumulative == pytest.approx(1.0)


def test_negative_rate_is_rejected():
    w = WearState()
    with pytest.raises(ValueError):
        w.age(calendar_rate=-0.001)


def test_the_checker_catches_wear_going_backward_unlogged():
    with pytest.raises(WearError):
        check_wear(previous=0.5, current=0.3, replaced=False)


def test_replace_resets_and_is_allowed_to_go_backward():
    w = WearState()
    w.age(calendar_rate=0.4)
    before = w.cumulative
    w.replace()
    check_wear(before, w.cumulative, replaced=True)  # must not raise
    assert w.cumulative == 0.0
    assert w.replacements == 1


def test_hazard_rises_with_wear_and_stays_in_bounds():
    w = WearState()
    assert w.hazard() == 0.0
    haz_values = []
    for _ in range(20):
        w.age(calendar_rate=0.05)
        haz_values.append(w.hazard())
    # monotonically non-decreasing, and every value a valid probability
    for a, b in zip(haz_values, haz_values[1:]):
        assert b >= a - 1e-12
        assert 0.0 <= b <= 1.0
    assert haz_values[-1] == pytest.approx(1.0, abs=1e-6)


def test_hazard_is_low_for_most_of_life_and_steep_only_near_the_end():
    w = WearState(cumulative=0.5)
    mid_life_hazard = w.hazard()
    w2 = WearState(cumulative=0.95)
    near_end_hazard = w2.hazard()
    assert mid_life_hazard < 0.2  # flat part of the bathtub curve
    assert near_end_hazard > 0.8  # steep wear-out tail


def test_battery_duty_rate_is_zero_when_untouched():
    rate = battery_duty_rate(0.0, 0.0, capacity_kwh=60.0, cycle_life=CLAIMED_BATTERY_CYCLE_LIFE)
    assert rate == 0.0


def test_battery_duty_rate_scales_with_throughput():
    light = battery_duty_rate(5.0, 5.0, capacity_kwh=60.0, cycle_life=CLAIMED_BATTERY_CYCLE_LIFE)
    heavy = battery_duty_rate(30.0, 30.0, capacity_kwh=60.0, cycle_life=CLAIMED_BATTERY_CYCLE_LIFE)
    assert heavy > light
    assert heavy == pytest.approx(light * 6.0)


def test_a_full_simulated_year_of_battery_cycling_stays_in_bounds_and_monotone():
    solar = SolarArray(area_m2=100.0, efficiency=0.20)
    battery = Battery(capacity_kwh=60.0, round_trip_eff=0.90,
                       max_charge_kw=20.0, max_discharge_kw=20.0, soc_kwh=30.0)
    ticks = simulate_scene("floodplain", days=365, seed=1, solar=solar, battery=battery, load_kw=4.0)

    wear = WearState()
    prev = wear.cumulative
    for t in ticks:
        duty = battery_duty_rate(t.battery_in_kwh, t.battery_out_kwh,
                                  capacity_kwh=60.0, cycle_life=CLAIMED_BATTERY_CYCLE_LIFE)
        calendar = battery_calendar_rate(CLAIMED_BATTERY_CALENDAR_LIFE_YEARS)
        wear.age(calendar_rate=calendar, duty_rate=duty)
        check_wear(prev, wear.cumulative, replaced=False)
        prev = wear.cumulative

    assert 0.0 < wear.cumulative <= 1.0
    # a battery cycled daily for a year against a 10-year calendar life and a
    # 3000-cycle life shouldn't already be at end-of-life after one year
    assert wear.cumulative < 0.5


def test_solar_calendar_rate_is_harsher_in_stormier_scenes():
    calm = solar_calendar_rate(CLAIMED_SOLAR_LIFE_YEARS, storminess=1)
    stormy = solar_calendar_rate(CLAIMED_SOLAR_LIFE_YEARS, storminess=9)
    assert stormy > calm
