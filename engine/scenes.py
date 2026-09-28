"""Scenes are designed climates, not real places. Each one is a set of
ratings that drive a synthetic weather generator — no coordinates, no API
call, nothing tied to any real location on Earth.

Ratings are 1-10 unless noted:
  sun       - how much clear-sky sun the scene gets on average
  wind      - how much wind the scene gets on average
  storminess- how often bad weather (low sun, high wind swings) shows up
  temp_c    - (min, max) plausible daily mean temperature range
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Scene:
    label: str
    sun: int
    wind: int
    storminess: int
    temp_c: tuple


SCENES = {
    "field":      Scene("Open Field",       sun=7, wind=4, storminess=3, temp_c=(-5, 30)),
    "plateau":    Scene("Mountain Plateau",  sun=8, wind=7, storminess=5, temp_c=(-15, 22)),
    "floodplain": Scene("River Floodplain",  sun=6, wind=3, storminess=6, temp_c=(2, 34)),
    "island":     Scene("Coastal Island",    sun=8, wind=8, storminess=4, temp_c=(15, 32)),
}

DEFAULT_SCENE = "field"


def get_scene(name: str = DEFAULT_SCENE) -> Scene:
    if name not in SCENES:
        raise ValueError(f"unknown scene '{name}'. choices: {list(SCENES)}")
    return SCENES[name]
