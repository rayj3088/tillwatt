"""SYNTHETIC weather for step 1 only. Not sourced, not real.
Step 2 replaces this with real historical data (Open-Meteo / NASA POWER) for the example site."""

import math
import random
from typing import Iterator, Tuple


def hourly_weather(days: int, seed: int = 0) -> Iterator[Tuple[float, float]]:
    """Yields (irradiance_w_m2, ambient_c) for every hour. Same seed, same weather."""
    rng = random.Random(seed)
    for _day in range(days):
        cloud = rng.uniform(0.15, 1.0)  # one cloudiness factor per day
        for hour in range(24):
            if 6 <= hour < 18:
                sun = 800.0 * math.sin(math.pi * (hour - 6 + 0.5) / 12.0)
                irradiance = sun * cloud * rng.uniform(0.9, 1.0)
            else:
                irradiance = 0.0
            temp_c = 12.0 + 8.0 * math.sin(2.0 * math.pi * (hour - 9) / 24.0)
            yield irradiance, temp_c
