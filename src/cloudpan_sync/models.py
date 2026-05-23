from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ConflictPolicy = Literal["overwrite_existing", "auto_rename_new"]


class FingerprintSet(BaseModel):
    md5: str = ""
    sha1: str = ""
    sha256: str = ""
    crc64: str = ""
    gcid: str = ""
    etag: str = ""
    pickcode: str = ""
    blockListMd5: list[str] = Field(default_factory=list)
    raw: dict[str, object] = Field(default_factory=dict)


class ProviderProfile(BaseModel):
    providerKey: str
    displayName: str
    direction: str = Field(default="bidirectional")
    authModes: list[str] = Field(default_factory=list)
    fastUploadInputs: list[str] = Field(default_factory=list)
    fallbackModes: list[str] = Field(default_factory=list)
    conflictPolicies: list[ConflictPolicy] = Field(default_factory=list)
    supportsOverwrite: bool = False
    supportsAutoRename: bool = False
    overwriteBehavior: str = "not_implemented"
    conflictNotes: str = ""
    status: str = "planned"


class SourceEntry(BaseModel):
    path: str
    size: int
    md5: str = ""
    sha1: str = ""
    sha256: str = ""
    crc64: str = ""
    gcid: str = ""
    etag: str = ""
    pickcode: str = ""
    blockListMd5: list[str] = Field(default_factory=list)
    raw: dict[str, object] = Field(default_factory=dict)
    localPath: str = ""


class PlanItem(BaseModel):
    path: str
    size: int
    strategy: str
    reason: str
    conflictPolicy: ConflictPolicy = "auto_rename_new"
    conflictSupportStatus: str = "unknown"
    conflictNote: str = ""
    normalizedFingerprints: FingerprintSet = Field(default_factory=FingerprintSet)
    availableFastInputs: list[str] = Field(default_factory=list)
    missingFastInputs: list[str] = Field(default_factory=list)


class PlanSummary(BaseModel):
    total: int
    strategyCounts: dict[str, int]


class TransferPlan(BaseModel):
    sourceProvider: str
    targetProvider: str
    thresholdMB: int
    conflictPolicy: ConflictPolicy = "auto_rename_new"
    items: list[PlanItem]
    summary: PlanSummary
    executionGroups: list[dict[str, object]] = Field(default_factory=list)
    pendingItems: list[dict[str, object]] = Field(default_factory=list)


class AuthProfile(BaseModel):
    profileId: str
    providerKey: str
    authMode: str
    displayName: str
    token: str = ""
    cookie: str = ""
    extra: dict[str, str] = Field(default_factory=dict)
    status: str = "unverified"
    lastError: str = ""
    createdAt: str
    updatedAt: str


class AuthProfileInput(BaseModel):
    providerKey: str
    authMode: str
    displayName: str
    token: str = ""
    cookie: str = ""
    extra: dict[str, str] = Field(default_factory=dict)


class TaskCreateRequest(BaseModel):
    sourceProvider: str
    targetProvider: str
    targetProfileId: str = ""
    targetParentId: str = ""
    thresholdMB: int = 0
    conflictPolicy: ConflictPolicy = "auto_rename_new"
    acknowledgePendingManual: bool = False
    acknowledgeDownloadUpload: bool = False
    selectedRoots: list[str] = Field(default_factory=list)
    entries: list[SourceEntry]


class TaskActionRequest(BaseModel):
    action: str


class AuthLiveValidateRequest(BaseModel):
    profileId: str
