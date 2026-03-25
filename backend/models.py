from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GaitFeatures:
    ankle_tilt_deg: float
    knee_angle_deg: float
    hip_drop_ratio: float
    stride_symmetry: float
    cadence_spm: int
    strike_bias: float


@dataclass
class GaitProfile:
    pronation_type: str
    strike_pattern: str
    knee_alignment: str
    arch_type: str
    pelvic_symmetry: float
    cadence_spm: int
    confidence: float
    gait_insight: str
    raw_features: dict[str, Any] = field(default_factory=dict)


@dataclass
class Recommendation:
    shoe_type: str
    match_score: float
    why_this_fits: str

