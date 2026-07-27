"""Neighbors: a model of the TMT primary mirror's 492 hexagonal segments.

See :mod:`neighbors.mirror` for the mirror model, :mod:`neighbors.sensors`
for the edge-sensor model, and :mod:`neighbors.hexgrid` for the underlying
hex-grid coordinate system.
"""

from neighbors.hexgrid import HEX_DIRECTIONS, Hex
from neighbors.mirror import (
    HEX_TO_SEGMENT,
    SECTORS,
    SEGMENTS_PER_SECTOR,
    SEGMENT_COUNT,
    SEGMENT_TO_HEX,
    neighbor_by_direction,
    neighbors,
    segment_sort_key,
)
from neighbors.sensors import (
    SENSORS_PER_EDGE,
    SENSORS_PER_SEGMENT,
    Sensor,
    SensorPair,
    SensorType,
    drive_sensors,
    facing,
    print_drive_sensors,
    print_sense_sensors,
    sense_sensors,
    sensor_count,
    sensors,
)

__all__ = [
    "HEX_DIRECTIONS",
    "HEX_TO_SEGMENT",
    "Hex",
    "SECTORS",
    "SEGMENTS_PER_SECTOR",
    "SEGMENT_COUNT",
    "SEGMENT_TO_HEX",
    "SENSORS_PER_EDGE",
    "SENSORS_PER_SEGMENT",
    "Sensor",
    "SensorPair",
    "SensorType",
    "drive_sensors",
    "facing",
    "neighbor_by_direction",
    "neighbors",
    "print_drive_sensors",
    "print_sense_sensors",
    "segment_sort_key",
    "sense_sensors",
    "sensor_count",
    "sensors",
]


def main() -> None:
    segment_id = "A15"
    print(f"Neighbors of {segment_id}: {neighbors(segment_id)}")
    print(f"Sensors on {segment_id}: {[s.id for s in sensors(segment_id)]}")
    print(f"Sense sensors facing {segment_id}: {sense_sensors(segment_id)}")
    print(f"Drive sensors facing {segment_id}: {drive_sensors(segment_id)}")
    print(f"Sense sensors facing {segment_id}, formatted:")
    print_sense_sensors(segment_id)
    print(f"Drive sensors facing {segment_id}, formatted:")
    print_drive_sensors(segment_id)


if __name__ == "__main__":
    main()
