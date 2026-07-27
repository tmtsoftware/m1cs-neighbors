"""Model of the numbered edge sensors mounted on each mirror segment.

Each segment has up to 12 sensor positions, numbered 1-12, two per edge
around its 6 edges. Numbering starts at the segment's top-right vertex
and increases counter-clockwise: sensors 1-2 sit on the edge facing
"up", 3-4 on the next edge counter-clockwise, and so on around to 11-12
on the edge facing "upper-right". Within a pair, the odd (leading)
sensor is the one reached first going counter-clockwise; the even
(trailing) sensor is the other one.

An edge only has sensors if it actually borders another segment,
matching :func:`neighbors.mirror.neighbors`: edges facing the center
hole or the outer boundary of the mirror have no sensors at all.

All segments share one physical orientation, but sector B's numbering is
itself rotated 60 degrees (one edge) further counter-clockwise than
sector A's, sector C another 60 degrees further, and so on -- the same
per-sector rotation used to build the segment layout in
:mod:`neighbors.mirror`. That means a sensor's number generally changes
when its edge crosses a sector boundary: e.g. sensor 5 on A1 faces
sensor 10 on B2, not sensor 5.

Every sensor is also one of two types: odd-numbered sensors (1, 3, 5, 7,
9, 11) are "sense" sensors, and even-numbered sensors (2, 4, 6, 8, 10,
12) are "drive" sensors. Because the leading (odd) sensor of a pair
always faces the trailing (even) sensor of the neighbor's pair and vice
versa, a sense sensor always faces a drive sensor, and a drive sensor
always faces a sense sensor.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from neighbors.mirror import SECTORS, neighbor_by_direction


class SensorType(Enum):
    """Whether a sensor is "sense" (odd-numbered) or "drive" (even)."""

    SENSE = "sense"
    DRIVE = "drive"


SENSORS_PER_SEGMENT = 12
SENSORS_PER_EDGE = 2

# Sensor numbering starts at the top-right vertex and goes
# counter-clockwise through hex directions 2, 3, 4, 5, 0, 1 (using the
# indices from neighbors.hexgrid.HEX_DIRECTIONS), two sensors per
# direction. So direction 2 is "pair 0" (sensors 1-2), direction 3 is
# "pair 1" (sensors 3-4), and so on.
_FIRST_PAIR_DIRECTION = 2


def _pair_index(sector_index: int, direction_index: int) -> int:
    """Return the sensor pair (0-5) on ``direction_index`` for a segment
    in sector number ``sector_index`` (0 for A, 1 for B, ... 5 for F).

    Each sector's numbering is rotated one direction step (60 degrees)
    further counter-clockwise than the previous sector's, so the sector
    index shifts which pair lands on which absolute direction.
    """
    return (direction_index - _FIRST_PAIR_DIRECTION - sector_index) % 6


def _direction_index(sector_index: int, pair_index: int) -> int:
    return (pair_index + _FIRST_PAIR_DIRECTION + sector_index) % 6


@dataclass(frozen=True)
class Sensor:
    """One numbered sensor mounted on a segment."""

    segment_id: str
    number: int  # 1-12

    def __post_init__(self) -> None:
        if not 1 <= self.number <= SENSORS_PER_SEGMENT:
            raise ValueError(f"sensor number must be 1-{SENSORS_PER_SEGMENT}")

    @property
    def id(self) -> str:
        """A human-readable identifier, e.g. "A1-5"."""
        return f"{self.segment_id}-{self.number}"

    @property
    def type(self) -> SensorType:
        """Whether this is a "sense" (odd) or "drive" (even) sensor."""
        return SensorType.SENSE if self.number % 2 == 1 else SensorType.DRIVE


def sensors(segment_id: str) -> list[Sensor]:
    """Return the sensors mounted on ``segment_id``, in numeric order.

    There are 2 sensors on every edge that borders another segment, so
    this returns between 3 and 12 sensors depending on how many
    neighbors ``segment_id`` has (see
    :func:`neighbors.mirror.neighbors`).

    Raises:
        ValueError: If ``segment_id`` is not a valid segment identifier.
    """
    neighbor_directions = neighbor_by_direction(segment_id)
    sector_index = SECTORS.index(segment_id[0])

    numbers: list[int] = []
    for direction_index in neighbor_directions:
        pair = _pair_index(sector_index, direction_index)
        numbers.extend((2 * pair + 1, 2 * pair + 2))
    return [Sensor(segment_id, number) for number in sorted(numbers)]


def sensor_count(segment_id: str) -> int:
    """Return how many sensors are mounted on ``segment_id`` (3-12).

    Raises:
        ValueError: If ``segment_id`` is not a valid segment identifier.
    """
    return len(sensors(segment_id))


def facing(sensor: Sensor) -> Sensor:
    """Return the sensor across the edge from ``sensor``.

    Every mounted sensor faces exactly one sensor on the neighboring
    segment across their shared edge, and it is always the opposite
    :class:`SensorType`: a sense sensor faces a drive sensor, and a
    drive sensor faces a sense sensor.

    Raises:
        ValueError: If ``sensor`` isn't actually mounted (its edge has
            no neighboring segment) on its segment.
    """
    sector_index = SECTORS.index(sensor.segment_id[0])
    pair = (sensor.number - 1) // 2
    direction_index = _direction_index(sector_index, pair)

    neighbor_id = neighbor_by_direction(sensor.segment_id).get(direction_index)
    if neighbor_id is None:
        raise ValueError(f"{sensor.segment_id} has no sensor {sensor.number}")

    opposite_direction = (direction_index + 3) % 6
    neighbor_sector_index = SECTORS.index(neighbor_id[0])
    opposite_pair = _pair_index(neighbor_sector_index, opposite_direction)
    leading, trailing = 2 * opposite_pair + 1, 2 * opposite_pair + 2

    is_leading = sensor.number % 2 == 1
    return Sensor(neighbor_id, trailing if is_leading else leading)


SensorPair = tuple[tuple[str, int], tuple[str, int]]


def _facing_sensors_of_type(segment_id: str, own_type: SensorType) -> list[SensorPair]:
    """Return, for each of ``segment_id``'s own sensors of ``own_type``,
    a ``(own, facing)`` pair -- ``own`` being ``(segment_id, number)``
    and ``facing`` being the ``(neighbor_id, number)`` it faces across
    their shared edge.

    Since a sense sensor always faces a drive sensor and vice versa
    (see this module's docstring), the ``facing`` side is always the
    opposite type from ``own_type``. Pairs are in ascending order of
    ``own``'s sensor number (see :func:`sensors`).
    """
    result: list[SensorPair] = []
    for sensor in sensors(segment_id):
        if sensor.type is own_type:
            partner = facing(sensor)
            own = (sensor.segment_id, sensor.number)
            facing_pair = (partner.segment_id, partner.number)
            result.append((own, facing_pair))
    return result


def sense_sensors(segment_id: str) -> list[SensorPair]:
    """Return, for each of ``segment_id``'s own drive sensors, a pair of
    that drive sensor and the sense sensor -- on a neighbor -- that
    faces it across their shared edge.

    Each edge has two sense/drive pairs, one mounted on each side, so
    ``segment_id`` has both a drive sensor of its own on that edge (see
    :func:`sensors`) and, facing it from across the edge, a sense
    sensor mounted on the neighbor. This returns one
    ``((segment_id, drive_number), (neighbor_id, sense_number))`` tuple
    per edge that has sensors, in ascending order of ``segment_id``'s
    own sensor number.

    For example, ``sense_sensors("A1")`` returns::

        [
            (("A1", 2), ("A3", 7)),
            (("A1", 4), ("B5", 7)),
            (("A1", 6), ("B2", 9)),
            (("A1", 10), ("A2", 3)),
            (("A1", 12), ("A4", 5)),
        ]

    Raises:
        ValueError: If ``segment_id`` is not a valid segment identifier.
    """
    return _facing_sensors_of_type(segment_id, SensorType.DRIVE)


def drive_sensors(segment_id: str) -> list[SensorPair]:
    """Return, for each of ``segment_id``'s own sense sensors, a pair of
    that sense sensor and the drive sensor -- on a neighbor -- that
    faces it across their shared edge.

    This is the mirror image of :func:`sense_sensors`: ``segment_id``
    has its own sense sensor on every edge (see :func:`sensors`), and
    this instead pairs each one with the neighbor's drive sensor that
    faces it, as ``((segment_id, sense_number), (neighbor_id,
    drive_number))`` tuples, in ascending order of ``segment_id``'s own
    sensor number.

    For example, ``drive_sensors("A1")`` returns::

        [
            (("A1", 1), ("A3", 8)),
            (("A1", 3), ("B5", 8)),
            (("A1", 5), ("B2", 10)),
            (("A1", 9), ("A2", 4)),
            (("A1", 11), ("A4", 6)),
        ]

    Raises:
        ValueError: If ``segment_id`` is not a valid segment identifier.
    """
    return _facing_sensors_of_type(segment_id, SensorType.SENSE)


def _print_sensor_pairs(pairs: list[SensorPair]) -> None:
    for own, neighbor in pairs:
        print(f"{Sensor(*own).id} faces {Sensor(*neighbor).id}")


def print_sense_sensors(segment_id: str) -> None:
    """Print ``sense_sensors(segment_id)`` in a human-readable form.

    A convenience wrapper for demos: instead of the raw list of nested
    tuples, prints one line per pair, in the form ``A1-2 faces A3-7``.

    For example, ``print_sense_sensors("A1")`` prints::

        A1-2 faces A3-7
        A1-4 faces B5-7
        A1-6 faces B2-9
        A1-10 faces A2-3
        A1-12 faces A4-5

    Raises:
        ValueError: If ``segment_id`` is not a valid segment identifier.
    """
    _print_sensor_pairs(sense_sensors(segment_id))


def print_drive_sensors(segment_id: str) -> None:
    """Print ``drive_sensors(segment_id)`` in a human-readable form.

    A convenience wrapper for demos: instead of the raw list of nested
    tuples, prints one line per pair, in the form ``A1-1 faces A3-8``.

    For example, ``print_drive_sensors("A1")`` prints::

        A1-1 faces A3-8
        A1-3 faces B5-8
        A1-5 faces B2-10
        A1-9 faces A2-4
        A1-11 faces A4-6

    Raises:
        ValueError: If ``segment_id`` is not a valid segment identifier.
    """
    _print_sensor_pairs(drive_sensors(segment_id))
