"""Compatibility shim for legacy `import app.orchestrator` callers."""

from core.orchestrator import ESGOrchestrator

__all__ = ["ESGOrchestrator"]
