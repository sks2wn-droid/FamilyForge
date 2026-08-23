"""FamilyForge - toolkit for family photo scanning, restoration & organization."""

__version__ = "0.1.0"

from .preprocess import (
    deskew,
    auto_crop,
    reduce_artifacts,
    enhance,
    process_photo,
    process_batch,
)

__all__ = [
    "deskew",
    "auto_crop",
    "reduce_artifacts",
    "enhance",
    "process_photo",
    "process_batch",
]
