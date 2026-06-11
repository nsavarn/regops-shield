"""RegOps Shield - Agents Package

This package contains all AI agent implementations for the
RegOps Shield compliance orchestration platform.
"""

from .compliance_agent import ComplianceAgent
from .shadow_run_agent import ShadowRunAgent
from .policy_agent import PolicyAgent
from .report_agent import ReportAgent

__all__ = [
    "ComplianceAgent",
    "ShadowRunAgent",
    "PolicyAgent",
    "ReportAgent",
]

__version__ = "1.0.0"
__author__ = "nsavarn"
__description__ = "AI-powered compliance agents for RegOps Shield"
