import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.segments.base import SegmentHandler

SEGMENT_LABELS = {
    "university_he": "University / Higher Education",
    "smb_landlord": "Commercial Landlord",
    "smb_industrial": "SMB Industrial",
    "individual_selfbuild": "Individual Self-Build",
}

SEGMENT_ICONS = {
    "university_he": "🏛️",
    "smb_landlord": "🏢",
    "smb_industrial": "🏭",
    "individual_selfbuild": "🏠",
}


def get_segment_display_label(segment_id: str) -> str:
    """Returns a text label prefixed with the segment icon."""
    icon = SEGMENT_ICONS.get(segment_id, "📁")
    label = SEGMENT_LABELS.get(segment_id, segment_id)
    return f"{icon} {label}"

SEGMENT_IDS = list(SEGMENT_LABELS.keys())

_HANDLER_MAP = {
    "university_he": ("app.segments.university_he", "UniversityHEHandler"),
    "smb_landlord": ("app.segments.commercial_landlord", "CommercialLandlordHandler"),
    "smb_industrial": ("app.segments.smb_industrial", "SMBIndustrialHandler"),
    "individual_selfbuild": ("app.segments.individual_selfbuild", "IndividualSelfBuildHandler"),
}

def get_segment_handler(segment_id: str) -> "SegmentHandler":
    if segment_id not in _HANDLER_MAP:
        raise ValueError(f"Unknown segment ID: {segment_id}")
    
    module_name, class_name = _HANDLER_MAP[segment_id]
    module = importlib.import_module(module_name)
    handler_class = getattr(module, class_name)
    return handler_class()
