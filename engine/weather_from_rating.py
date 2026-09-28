"""Turns a scene's ratings into an hourly synthetic weather stream.
Same seed + same scene = same weather, every time (for replayable comparisons)."""

import math
import random
from typing import Iterator, Tuple

from engine.scenes import Scene


def hourly_weather(scene: Scene, days: int, seed: int = 0) -> Iterator[Tuple[float, float]]:
    """Yields (irradiance_w_m2, ambient_c) for every hour, days*24 total."""
    rng = random.Random(seed)
    peak_irradiance = 400.0 + 60.0 * scene.sun          # higher sun rating -> higher clear-sky peak
    base_clearness = 0.35 + 0.05 * scene.sun            # 0.4-0.85ish average clearness
    storm_chance = 0.03 * scene.storminess              # per-day chance of a rough day
    t_min, t_max = scene.temp_c
    t_mid = (t_min + t_max) / 2.0
    t_swing = (t_max - t_min) / 2.0

    for day in range(days):
        season = math.sin(2.0 * math.pi * (day - 80) / 365.0)  # crude summer/winter cycle
        day_temp_mid = t_mid + t_swing * 0.6 * season
        clearness = base_clearness
        if rng.random() < storm_chance:
            clearness *= rng.uniform(0.1, 0.4)  # a rough day
        else:
            clearness *= rng.uniform(0.85, 1.05)
        clearness = max(0.05, min(1.0, clearness))

        for hour in range(24):
            if 6 <= hour < 18:
                shape = math.sin(math.pi * (hour - 6 + 0.5) / 12.0)
                irradiance = peak_irradiance * shape * clearness * rng.uniform(0.92, 1.0)
            else:
                irradiance = 0.0
            hour_temp = day_temp_mid + t_swing * 0.4 * math.sin(2.0 * math.pi * (hour - 9) / 24.0)
            yield max(0.0, irradiance), hour_temp
