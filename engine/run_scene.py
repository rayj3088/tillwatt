"""Runs the ledger-checked engine on a designed scene's weather — no coordinates,
no external API, no real location anywhere."""

from typing import List

from engine.ledger import Tick, check_tick
from engine.parts import Battery, SolarArray
from engine.scenes import DEFAULT_SCENE, get_scene
from engine.weather_from_rating import hourly_weather


def simulate_scene(scene_name: str, days: int, seed: int,
                    solar: SolarArray, battery: Battery, load_kw: float) -> List[Tick]:
    scene = get_scene(scene_name)
    ticks = []
    for hour, (irradiance, ambient_c) in enumerate(hourly_weather(scene, days, seed)):
        solar_kwh = solar.output_kwh(irradiance, ambient_c)
        load_kwh = load_kw
        soc_before = battery.soc_kwh

        direct = min(solar_kwh, load_kwh)
        surplus = solar_kwh - direct
        deficit = load_kwh - direct

        b_in = battery.charge(surplus) if surplus > 0 else 0.0
        b_out = battery.discharge(deficit) if deficit > 0 else 0.0

        curtailed = surplus - b_in
        served = direct + b_out
        losses = b_in * (1.0 - battery.eta) + b_out * (1.0 / battery.eta - 1.0)

        tick = Tick(hour=hour, solar_kwh=solar_kwh, imports_kwh=0.0, load_kwh=load_kwh,
                    load_served_kwh=served, battery_in_kwh=b_in, battery_out_kwh=b_out,
                    curtailed_kwh=curtailed, losses_kwh=losses,
                    soc_before_kwh=soc_before, soc_after_kwh=battery.soc_kwh)
        check_tick(tick)
        ticks.append(tick)
    return ticks


if __name__ == "__main__":
    solar = SolarArray(area_m2=100.0, efficiency=0.20)
    for name in ("field", "plateau", "floodplain", "island"):
        battery = Battery(capacity_kwh=60.0, round_trip_eff=0.90,
                          max_charge_kw=20.0, max_discharge_kw=20.0, soc_kwh=30.0)
        ticks = simulate_scene(name, days=365, seed=1, solar=solar, battery=battery, load_kw=4.0)
        unmet = sum(t.unmet_kwh for t in ticks)
        dark_hours = sum(1 for t in ticks if t.unmet_kwh > 1e-9)
        print(f"{name:12s} | solar {sum(t.solar_kwh for t in ticks):6.0f} kWh"
              f" | unmet {unmet:6.1f} kWh in {dark_hours:4d} hours")
    print("Ledger balanced every hour, every scene.")
