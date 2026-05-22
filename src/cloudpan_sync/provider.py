from __future__ import annotations

from dataclasses import dataclass

from .models import ProviderProfile


@dataclass
class ProviderAdapter:
    profile: ProviderProfile
