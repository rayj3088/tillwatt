"""The wear ledger: the sixth universal number ("failure curve") finally wired up.

Every part loses a fraction of its rated life every tick — a slow calendar
component (aging just from existing in a place) plus, for parts that cycle,
a duty component (aging from how hard they ran that hour). Wear is scored
0.0 (new) to 1.0 (end of rated life) so completely different parts — a
battery's charge cycles, a solar panel's UV exposure, a robot's duty hours —
sit on one comparable scale.

The law: cumulative wear never decreases. The one exception is an explicit,
logged replace() — a maintenance event, costed elsewhere (money, energy,
maybe a human-hour) — never a silent reset. If this ever fails, either the
aging math has a sign error or a replacement went unlogged.

Cumulative wear feeds a hazard: the instantaneous odds of failure this hour,
using a Weibull-shaped wear-out curve (hazard = wear ** shape). shape > 1
means "flat and low most of life, climbs steeply near the end" — the
standard reliability-engineering bathtub-curve tail, not a straight line to
failure. This hazard is what a future Monte Carlo "chance of ruin" pass
would sample every hour, across many simulated lifetimes.
"""

from dataclasses import dataclass

DEFAULT_WEIBULL_SHAPE = 3.0


class WearError(Exception):
    pass


@dataclass
class WearState:
    """Cumulative wear as a fraction of rated life, 0.0 (new) to 1.0 (end of life)."""

    cumulative: float = 0.0
    replacements: int = 0

    def hazard(self, shape: float = DEFAULT_WEIBULL_SHAPE) -> float:
        """This hour's odds of failure, 0-1. Rises steeply only near end of life."""
        w = min(max(self.cumulative, 0.0), 1.0)
        return w**shape

    def age(self, calendar_rate: float, duty_rate: float = 0.0) -> None:
        """Advance one tick's worth of wear. Never decreases except via replace()."""
        if calendar_rate < 0 or duty_rate < 0:
            raise ValueError("wear rates cannot be negative")
        self.cumulative = min(1.0, self.cumulative + calendar_rate + duty_rate)

    def replace(self) -> None:
        """A maintenance/replacement event. The caller is responsible for costing
        it (money + energy + possibly human-hours) — this just resets the clock."""
        self.cumulative = 0.0
        self.replacements += 1


def check_wear(previous: float, current: float, replaced: bool) -> None:
    """The wear law: cumulative wear never decreases, except across a logged
    replacement event. Same role check_tick() plays for energy conservation."""
    if not replaced and current < previous - 1e-9:
        raise WearError(f"wear went backward with no replacement: {previous:.6f} -> {current:.6f}")


# ---- rate models -----------------------------------------------------------
# These read scene/tick data already produced elsewhere (weather_from_rating.py,
# ledger.Tick) rather than opening a second bookkeeping system. The rated-life
# numbers below are CLAIMED defaults for illustration — same tier as the
# numbers in parts.py — and need a sources/SOURCES.csv row before they count
# as more than "claimed."

HOURS_PER_YEAR = 8760.0


def battery_calendar_rate(calendar_life_years: float) -> float:
    """Aging just from existing, independent of how much it's cycled."""
    return 1.0 / (calendar_life_years * HOURS_PER_YEAR)


def battery_duty_rate(battery_in_kwh: float, battery_out_kwh: float,
                       capacity_kwh: float, cycle_life: float) -> float:
    """Aging from use: a full cycle is one full charge + one full discharge, so
    a full cycle's worth of throughput is 2x capacity. Fractional cycles count
    fractionally — an hour that moves half the battery's capacity is a
    quarter of a full cycle."""
    equivalent_full_cycles = (battery_in_kwh + battery_out_kwh) / (2.0 * capacity_kwh)
    return equivalent_full_cycles / cycle_life


def solar_calendar_rate(rated_life_years: float, storminess: int) -> float:
    """Aging from UV/thermal exposure. Harsher (stormier) scenes age panels
    faster even though nothing about solar output or wiring changes."""
    harshness = 1.0 + 0.05 * storminess
    return harshness / (rated_life_years * HOURS_PER_YEAR)
