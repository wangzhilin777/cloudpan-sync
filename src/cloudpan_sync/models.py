from __future__ import annotations

from pydantic import BaseModel, Field


class ProviderProfile(BaseModel):
    providerKey: str
    displayName: str
    direction: str = Field(default="bidirectional")
    authModes: list[str] = Field(default_factory=list)
    fastUploadInputs: list[str] = Field(default_factory=list)
    fallbackModes: list[str] = Field(default_factory=list)
    status: str = "planned"


class SourceEntry(BaseModel):
    path: str
    size: int
    md5: str = ""
    sha1: str = ""
    sha256: str = ""
    gcid: str = ""
    etag: str = ""


class PlanItem(BaseModel):
    path: str
    size: int
    strategy: str
    reason: str
    missingFastInputs: list[str] = Field(default_factory=list)


class PlanSummary(BaseModel):
    total: int
    strategyCounts: dict[str, int]


class TransferPlan(BaseModel):
    sourceProvider: str
    targetProvider: str
    thresholdMB: int
    items: list[PlanItem]
    summary: PlanSummary
