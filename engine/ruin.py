"""Chance of ruin: how often does a design's battery reach end-of-life before
the horizon you built it for, across many plausible weather years for a scene?

This runs the exact same ledger + wear math as everywhere else, just many
times with different weather seeds, and counts how often cumulative wear
crosses 1.0 (end of rated life) before the target horizon. It deliberately
does NOT sample wear.hazard() as a per-hour coin flip — that number is a
relative shape (flat, then steep near end-of-life), not yet a calibrated
absolute probability, and turning it into one needs real MTBF data this
project doesn't have yet. "Reaches end of life early" is the falsifiable,
unit-free question this can honestly answer today.
"""

from dataclasses import dataclass
from typing import Callable, List, Optional

from engine.parts import Battery, SolarArray
from engine.run_scene import simulate_scene
from engine.wear import WearState, battery_calendar_rate, battery_duty_rate


@dataclass(frozen=True)
class RuinTrial:
    seed: int
    failed: bool
    failure_hour: Optional[int]  # None if it survived the whole horizon
    final_wear: float


@dataclass(frozen=True)
class RuinResult:
    trials: List[RuinTrial]

    @property
    def chance_of_ruin(self) -> float:
        if not self.trials:
            return 0.0
        return sum(1 for t in self.trials if t.failed) / len(self.trials)

    @property
    def median_failure_hour(self) -> Optional[int]:
        failed_hours = sorted(t.failure_hour for t in self.trials if t.failed)
        if not failed_hours:
            return None
        return failed_hours[len(failed_hours) // 2]


def chance_of_ruin(
    scene_name: str,
    days: int,
    trials: int,
    load_kw: float,
    solar: SolarArray,
    make_battery: Callable[[], Battery],
    calendar_life_years: float = 10.0,
    cycle_life: float = 3000.0,
    base_seed: int = 0,
) -> RuinResult:
    """Runs `trials` independent weather draws (seeds base_seed..base_seed+trials-1)
    against the same design and reports how often the battery wears out first."""
    results = []
    calendar_rate = battery_calendar_rate(calendar_life_years)
    for i in range(trials):
        seed = base_seed + i
        battery = make_battery()
        ticks = simulate_scene(scene_name, days=days, seed=seed,
                                solar=solar, battery=battery, load_kw=load_kw)
        wear = WearState()
        failed = False
        failure_hour = None
        for t in ticks:
            duty_rate = battery_duty_rate(t.battery_in_kwh, t.battery_out_kwh,
                                           capacity_kwh=battery.capacity_kwh, cycle_life=cycle_life)
            wear.age(calendar_rate=calendar_rate, duty_rate=duty_rate)
            if wear.cumulative >= 1.0:
                failed = True
                failure_hour = t.hour
                break
        results.append(RuinTrial(seed=seed, failed=failed, failure_hour=failure_hour,
                                  final_wear=wear.cumulative))
    return RuinResult(trials=results)
