"""Part models. Placeholders: every number here needs a row in sources/SOURCES.csv
before it counts as more than 'claimed'."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SolarArray:
    area_m2: float
    efficiency: float  # fraction, e.g. 0.20
    temp_coeff_per_c: float = 0.004  # ~0.4% power loss per degree C above 25 (claimed)
    noct_slope: float = 0.03125  # cell temp rise per W/m2 (roughly NOCT 45 C) (claimed)

    def output_kwh(self, irradiance_w_m2: float, ambient_c: float, dt_h: float = 1.0) -> float:
        cell_c = ambient_c + self.noct_slope * irradiance_w_m2
        derate = max(0.0, 1.0 - self.temp_coeff_per_c * (cell_c - 25.0))
        kw = self.area_m2 * (irradiance_w_m2 / 1000.0) * self.efficiency * derate
        return max(0.0, kw) * dt_h


@dataclass
class Battery:
    capacity_kwh: float
    round_trip_eff: float  # e.g. 0.90; split evenly between charge and discharge
    max_charge_kw: float
    max_discharge_kw: float
    soc_kwh: float = 0.0

    def __post_init__(self) -> None:
        self.eta = math.sqrt(self.round_trip_eff)

    def charge(self, offered_kwh: float, dt_h: float = 1.0) -> float:
        """Take up to offered_kwh from the bus. Returns energy actually taken."""
        headroom = self.capacity_kwh - self.soc_kwh
        taken = min(offered_kwh, self.max_charge_kw * dt_h, headroom / self.eta)
        taken = max(0.0, taken)
        self.soc_kwh = min(self.capacity_kwh, self.soc_kwh + taken * self.eta)
        return taken

    def discharge(self, requested_kwh: float, dt_h: float = 1.0) -> float:
        """Deliver up to requested_kwh to the bus. Returns energy actually delivered."""
        delivered = min(requested_kwh, self.max_discharge_kw * dt_h, self.soc_kwh * self.eta)
        delivered = max(0.0, delivered)
        self.soc_kwh = max(0.0, self.soc_kwh - delivered / self.eta)
        return delivered
