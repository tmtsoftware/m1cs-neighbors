"""Neighbors: a model of the TMT primary mirror's 492 hexagonal segments.

See :mod:`neighbors.mirror` for the mirror model and :mod:`neighbors.hexgrid`
for the underlying hex-grid coordinate system.
"""

from neighbors.hexgrid import HEX_DIRECTIONS, Hex
from neighbors.mirror import (
    HEX_TO_SEGMENT,
    SECTORS,
    SEGMENT_COUNT,
    SEGMENT_TO_HEX,
    SEGMENTS_PER_SECTOR,
    neighbors,
)

__all__ = [
    "HEX_DIRECTIONS",
    "HEX_TO_SEGMENT",
    "Hex",
    "SECTORS",
    "SEGMENT_COUNT",
    "SEGMENT_TO_HEX",
    "SEGMENTS_PER_SECTOR",
    "neighbors",
]


def main() -> None:
    segment_id = "A15"
    print(f"Neighbors of {segment_id}: {neighbors(segment_id)}")


if __name__ == "__main__":
    main()
