"""World tick: solar in, battery as buffer, robots as load. Runs the ledger check every hour."""

from typing import List

from engine.ledger import Tick, check_tick
from engine.parts import Battery, SolarArray
from engine.weather_synthetic import hourly_weather


def step(hour: int, solar: SolarArray, battery: Battery,
         irradiance: float, ambient_c: float, load_kw: float, dt_h: float = 1.0) -> Tick:
    solar_kwh = solar.output_kwh(irradiance, ambient_c, dt_h)
    load_kwh = load_kw * dt_h
    soc_before = battery.soc_kwh

    direct = min(solar_kwh, load_kwh)  # sun feeds the load first
    surplus = solar_kwh - direct
    deficit = load_kwh - direct

    b_in = battery.charge(surplus, dt_h) if surplus > 0 else 0.0
    b_out = battery.discharge(deficit, dt_h) if deficit > 0 else 0.0

    curtailed = surplus - b_in
    served = direct + b_out
    losses = b_in * (1.0 - battery.eta) + b_out * (1.0 / battery.eta - 1.0)

    tick = Tick(
        hour=hour,
        solar_kwh=solar_kwh,
        imports_kwh=0.0,  # the fence: nothing comes in after day one
        load_kwh=load_kwh,
        load_served_kwh=served,
        battery_in_kwh=b_in,
        battery_out_kwh=b_out,
        curtailed_kwh=curtailed,
        losses_kwh=losses,
        soc_before_kwh=soc_before,
        soc_after_kwh=battery.soc_kwh,
    )
    check_tick(tick)
    return tick


def simulate(days: int, seed: int, solar: SolarArray, battery: Battery, load_kw: float) -> List[Tick]:
    ticks = []
    for hour, (irradiance, ambient_c) in enumerate(hourly_weather(days, seed)):
        ticks.append(step(hour, solar, battery, irradiance, ambient_c, load_kw))
    return ticks


if __name__ == "__main__":
    solar = SolarArray(area_m2=100.0, efficiency=0.20)
    battery = Battery(capacity_kwh=60.0, round_trip_eff=0.90,
                      max_charge_kw=20.0, max_discharge_kw=20.0, soc_kwh=30.0)
    ticks = simulate(days=30, seed=1, solar=solar, battery=battery, load_kw=4.0)
    unmet = sum(t.unmet_kwh for t in ticks)
    dark_hours = sum(1 for t in ticks if t.unmet_kwh > 1e-9)
    print(f"30 synthetic days | solar {sum(t.solar_kwh for t in ticks):.0f} kWh"
          f" | load {sum(t.load_kwh for t in ticks):.0f} kWh"
          f" | unmet {unmet:.1f} kWh in {dark_hours} hours"
          f" | curtailed {sum(t.curtailed_kwh for t in ticks):.0f} kWh"
          f" | losses {sum(t.losses_kwh for t in ticks):.0f} kWh")
    print("Ledger balanced every hour." if dark_hours >= 0 else "")
