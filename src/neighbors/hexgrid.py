"""Generic hexagonal grid primitives.

This is a small, self-contained implementation of cube coordinates for a
hexagonal grid, following the conventions described at
https://www.redblobgames.com/grids/hexagons/. It has no knowledge of the
mirror itself; see :mod:`neighbors.mirror` for that.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hex:
    """A location on a hexagonal grid, in cube coordinates."""

    q: int
    r: int
    s: int

    def __post_init__(self) -> None:
        if self.q + self.r + self.s != 0:
            raise ValueError("q + r + s must equal 0")

    def __add__(self, other: Hex) -> Hex:
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)

    def rotated_left(self) -> Hex:
        """Return this location rotated 60 degrees about the origin."""
        return Hex(-self.s, -self.q, -self.r)


# The six directions of adjacency on a hex grid, as unit cube-coordinate
# steps (see https://www.redblobgames.com/grids/hexagons/#neighbors).
HEX_DIRECTIONS = (
    Hex(1, 0, -1),
    Hex(1, -1, 0),
    Hex(0, -1, 1),
    Hex(-1, 0, 1),
    Hex(-1, 1, 0),
    Hex(0, 1, -1),
)
