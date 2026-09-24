"""Every threshold from DEFINITIONS.md, one-to-one by parameter name."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # 1. Universe
    min_price: float = 5.0
    min_dollar_volume: float = 20e6
    dollar_volume_window: int = 20
    # 2. Ignition
    ignition_sigma: float = 2.5
    vol_window: int = 60  # beta and sigma; also sets min_history (61 sessions)
    # 3. Volume
    volume_mult: float = 3.0
    volume_window: int = 50
    # 4. Consolidation
    consol_min: int = 2
    consol_max: int = 4
    consol_sigma: float = 1.0
    min_hold: float = 0.5
    # 6. Lean
    lean_close_loc: float = 2 / 3
    lean_volume_ratio: float = 0.5
