"""The energy ledger: sources (solar + imports) == load served + curtailed + losses + change in stored energy"""

from dataclasses import dataclass

TOLERANCE_KWH = 1e-9


class ConservationError(AssertionError):
    pass


@dataclass(frozen=True)
class Tick:
    hour: int
    solar_kwh: float
    imports_kwh: float  # anything crossing the fence inward after day one
    load_kwh: float
    load_served_kwh: float
    battery_in_kwh: float  # taken from the bus into the battery
    battery_out_kwh: float  # delivered from the battery to the bus
    curtailed_kwh: float  # produced but nowhere to put it
    losses_kwh: float  # battery charge and discharge losses
    soc_before_kwh: float
    soc_after_kwh: float

    @property
    def unmet_kwh(self) -> float:
        return self.load_kwh - self.load_served_kwh


def check_tick(t: Tick) -> None:
    sources = t.solar_kwh + t.imports_kwh
    sinks = (
        t.load_served_kwh
        + t.curtailed_kwh
        + t.losses_kwh
        + (t.soc_after_kwh - t.soc_before_kwh)
    )
    if abs(sources - sinks) > TOLERANCE_KWH:
        raise ConservationError(
            f"hour {t.hour}: sources {sources:.12f} kWh != sinks {sinks:.12f} kWh"
        )
