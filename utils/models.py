"""Pydantic v2 validation models for RegOps Shield.

All API request/response bodies and internal data structures
are validated here to ensure type safety and data integrity.
"""
from __future__ import annotations

import hashlib
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SeverityLevel(str, Enum):
    """Compliance finding severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class AgentStatus(str, Enum):
    """Agent run lifecycle status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SHADOW = "shadow"


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class AnalyseRepoRequest(BaseModel):
    """Request payload to trigger repository compliance analysis."""

    repo_url: HttpUrl = Field(
        ...,
        description="HTTPS URL of the GitHub repository to analyse.",
        examples=["https://github.com/example/my-repo"],
    )
    branch: str = Field(
        default="main",
        min_length=1,
        max_length=255,
        description="Target branch name.",
    )
    shadow_run: bool = Field(
        default=True,
        description="If True, runs in observation mode without enforcing changes.",
    )
    policy_override: Optional[str] = Field(
        default=None,
        max_length=10_000,
        description="Optional inline policy text to override stored policy.",
    )

    @field_validator("repo_url", mode="before")
    @classmethod
    def must_be_github_url(cls, v: Any) -> Any:
        """Ensure repo_url points to github.com."""
        url = str(v)
        if "github.com" not in url:
            raise ValueError("repo_url must be a github.com URL")
        return v


class PolicyUpdateRequest(BaseModel):
    """Request payload to update the active compliance policy."""

    policy_text: str = Field(
        ...,
        min_length=10,
        max_length=50_000,
        description="Full policy document text.",
    )
    policy_version: str = Field(
        ...,
        pattern=r"^v\d+\.\d+\.\d+$",
        description="Semantic version string, e.g. v1.2.0.",
    )
    sha256_checksum: Optional[str] = Field(
        default=None,
        description="Optional SHA-256 checksum for integrity verification.",
    )

    @model_validator(mode="after")
    def verify_checksum(self) -> PolicyUpdateRequest:
        """If checksum supplied, verify it matches policy_text."""
        if self.sha256_checksum is not None:
            computed = hashlib.sha256(
                self.policy_text.encode("utf-8")
            ).hexdigest()
            if computed != self.sha256_checksum:
                raise ValueError(
                    f"SHA-256 mismatch: expected {computed}, got {self.sha256_checksum}"
                )
        return self


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class ComplianceFinding(BaseModel):
    """A single compliance finding from an agent run."""

    rule_id: str = Field(..., description="Unique rule identifier.")
    severity: SeverityLevel
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=2000)
    file_path: Optional[str] = Field(default=None)
    line_number: Optional[int] = Field(default=None, ge=1)
    remediation: Optional[str] = Field(default=None, max_length=1000)


class AnalysisResult(BaseModel):
    """Full analysis result returned after a repository compliance scan."""

    run_id: str = Field(..., description="Unique identifier for this analysis run.")
    repo_url: str
    branch: str
    status: AgentStatus
    shadow_run: bool
    findings: list[ComplianceFinding] = Field(default_factory=list)
    summary: Optional[str] = Field(default=None, max_length=5000)
    duration_seconds: Optional[float] = Field(default=None, ge=0)

    @property
    def critical_count(self) -> int:
        """Number of CRITICAL severity findings."""
        return sum(1 for f in self.findings if f.severity == SeverityLevel.CRITICAL)

    @property
    def passed(self) -> bool:
        """True if no CRITICAL or HIGH findings."""
        return not any(
            f.severity in (SeverityLevel.CRITICAL, SeverityLevel.HIGH)
            for f in self.findings
        )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str
    environment: str
