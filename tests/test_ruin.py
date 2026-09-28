"""Gate for step 3: chance-of-ruin is a real probability, a design with headroom
almost never fails, a design pushed past its cycle life fails a lot more, and
running it twice with the same seeds gives the same answer."""

import pytest

from engine.parts import Battery, SolarArray
from engine.ruin import chance_of_ruin

SOLAR = SolarArray(area_m2=100.0, efficiency=0.20)


def make_battery(capacity_kwh=60.0):
    return Battery(capacity_kwh=capacity_kwh, round_trip_eff=0.90,
                    max_charge_kw=20.0, max_discharge_kw=20.0, soc_kwh=capacity_kwh * 0.5)


def test_chance_of_ruin_is_a_probability():
    result = chance_of_ruin("field", days=365, trials=10, load_kw=4.0,
                             solar=SOLAR, make_battery=make_battery,
                             calendar_life_years=10.0, cycle_life=3000.0)
    assert 0.0 <= result.chance_of_ruin <= 1.0
    assert len(result.trials) == 10


def test_a_design_with_huge_headroom_almost_never_reaches_ruin():
    # tiny load, big cycle life, long calendar life relative to a 1-year horizon
    result = chance_of_ruin("field", days=365, trials=20, load_kw=1.0,
                             solar=SOLAR, make_battery=make_battery,
                             calendar_life_years=50.0, cycle_life=20000.0)
    assert result.chance_of_ruin == 0.0


def test_a_design_pushed_past_its_cycle_life_fails_far_more_often():
    easy = chance_of_ruin("field", days=730, trials=30, load_kw=4.0,
                           solar=SOLAR, make_battery=make_battery,
                           calendar_life_years=100.0, cycle_life=3000.0)
    hard = chance_of_ruin("field", days=730, trials=30, load_kw=4.0,
                           solar=SOLAR, make_battery=make_battery,
                           calendar_life_years=100.0, cycle_life=30.0)
    assert hard.chance_of_ruin > easy.chance_of_ruin
    assert hard.chance_of_ruin > 0.8
    assert easy.chance_of_ruin < 0.2


def test_same_seeds_give_the_same_answer():
    a = chance_of_ruin("plateau", days=365, trials=15, load_kw=4.0,
                        solar=SOLAR, make_battery=make_battery,
                        calendar_life_years=10.0, cycle_life=200.0, base_seed=7)
    b = chance_of_ruin("plateau", days=365, trials=15, load_kw=4.0,
                        solar=SOLAR, make_battery=make_battery,
                        calendar_life_years=10.0, cycle_life=200.0, base_seed=7)
    assert a.chance_of_ruin == b.chance_of_ruin
    assert [t.failure_hour for t in a.trials] == [t.failure_hour for t in b.trials]


def test_failure_hour_is_only_set_when_failed():
    result = chance_of_ruin("field", days=730, trials=20, load_kw=4.0,
                             solar=SOLAR, make_battery=make_battery,
                             calendar_life_years=100.0, cycle_life=30.0)
    for t in result.trials:
        if t.failed:
            assert t.failure_hour is not None
            assert t.final_wear >= 1.0
        else:
            assert t.failure_hour is None


def test_median_failure_hour_is_none_when_nothing_fails():
    result = chance_of_ruin("field", days=365, trials=10, load_kw=1.0,
                             solar=SOLAR, make_battery=make_battery,
                             calendar_life_years=50.0, cycle_life=20000.0)
    assert result.median_failure_hour is None


def test_median_failure_hour_is_set_when_things_fail():
    result = chance_of_ruin("field", days=730, trials=20, load_kw=4.0,
                             solar=SOLAR, make_battery=make_battery,
                             calendar_life_years=100.0, cycle_life=30.0)
    assert result.median_failure_hour is not None
    assert result.median_failure_hour > 0
