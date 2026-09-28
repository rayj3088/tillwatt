"""Gate for step 1: the ledger must balance, always."""

import pytest

from engine.ledger import ConservationError, Tick, check_tick
from engine.parts import Battery, SolarArray
from engine.sim import simulate


def make_world(soc=30.0):
    solar = SolarArray(area_m2=100.0, efficiency=0.20)
    battery = Battery(capacity_kwh=60.0, round_trip_eff=0.90,
                      max_charge_kw=20.0, max_discharge_kw=20.0, soc_kwh=soc)
    return solar, battery


def test_ledger_balances_every_hour_for_a_year():
    solar, battery = make_world()
    ticks = simulate(days=365, seed=7, solar=solar, battery=battery, load_kw=4.0)
    assert len(ticks) == 365 * 24  # simulate() already calls check_tick each hour


def test_battery_never_leaves_its_bounds():
    solar, battery = make_world()
    ticks = simulate(days=90, seed=3, solar=solar, battery=battery, load_kw=6.0)
    for t in ticks:
        assert -1e-9 <= t.soc_after_kwh <= battery.capacity_kwh + 1e-9


def test_nothing_crosses_the_fence():
    solar, battery = make_world()
    ticks = simulate(days=30, seed=1, solar=solar, battery=battery, load_kw=4.0)
    assert all(t.imports_kwh == 0.0 for t in ticks)


def test_no_free_energy_with_no_sun_and_empty_battery():
    solar = SolarArray(area_m2=100.0, efficiency=0.20)
    battery = Battery(capacity_kwh=60.0, round_trip_eff=0.90,
                      max_charge_kw=20.0, max_discharge_kw=20.0, soc_kwh=0.0)
    from engine.sim import step
    t = step(0, solar, battery, irradiance=0.0, ambient_c=10.0, load_kw=4.0)
    assert t.load_served_kwh == 0.0
    assert t.unmet_kwh == pytest.approx(4.0)


def test_same_seed_same_result():
    a = simulate(30, 5, *make_world(), load_kw=4.0)
    b = simulate(30, 5, *make_world(), load_kw=4.0)
    assert [t.soc_after_kwh for t in a] == [t.soc_after_kwh for t in b]


def test_the_checker_catches_free_energy():
    cheat = Tick(hour=0, solar_kwh=0.0, imports_kwh=0.0, load_kwh=5.0,
                 load_served_kwh=5.0, battery_in_kwh=0.0, battery_out_kwh=0.0,
                 curtailed_kwh=0.0, losses_kwh=0.0, soc_before_kwh=0.0, soc_after_kwh=0.0)
    with pytest.raises(ConservationError):
        check_tick(cheat)
