"""Data classes for the RAND report pipeline.

No enums — condition, priority, system are all plain strings
so they flex with whatever RAND decides later.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Observation:
    """A single observation extracted from a PowerPoint slide."""
    slide_index: int
    obs_number: str  # e.g. "1-1" (section-sequence)
    section_name: str
    raw_text: str
    image_bytes: Optional[bytes] = None
    image_path: Optional[str] = None


@dataclass
class ProcessedObservation:
    """An observation after AI processing."""
    slide_index: int
    obs_number: str
    section_name: str
    raw_text: str
    image_bytes: Optional[bytes] = None
    image_path: Optional[str] = None
    caption: str = ""
    system: str = ""
    component: str = ""
    location: str = ""
    condition: str = ""
    prose: str = ""
    recommendation: str = ""
    priority: str = ""
    cost_low: float = 0.0
    cost_high: float = 0.0
    flags: list = field(default_factory=list)  # list of dicts, e.g. {"type": "...", "message": "..."}


@dataclass
class Report:
    """Container for a full building survey report."""
    building_name: str = ""
    address: str = ""
    date: str = ""
    observations: list = field(default_factory=list)  # list of Observation
    processed_observations: list = field(default_factory=list)  # list of ProcessedObservation
