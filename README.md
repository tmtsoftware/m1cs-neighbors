# Neighbors

A Python library modeling the TMT (Thirty Meter Telescope) primary mirror
and the 492 hexagonal segments it is built from. It answers two kinds of
questions: which segments border a given segment, and how the numbered
edge sensors mounted on segments face each other across those shared
edges.

This project was built with Claude, with the conversation logs that
produced it kept alongside the code (`conversation-log.md`,
`conversation-log-2.md`) as a record of the design process.

## The mirror model

The primary mirror is made of 492 hexagonal segments arranged around a
hexagonal hole at its center. The segments are divided into 6 sectors —
A, B, C, D, E, F — arranged counter-clockwise, each containing 82
segments. A segment is identified by its sector letter plus a number
from 1–82 (e.g. `"A15"`), where numbering starts at the segment(s)
closest to the center hole and increases outward, ring by ring. Sectors
B–F are geometrically identical to sector A, just rotated by 60, 120,
180, 240, and 300 degrees respectively.

Internally, every segment is placed on a standard hexagonal grid using
cube coordinates, so once the mirror is modeled this way, finding a
segment's neighbors — of which it can have 3, 4, 5, or 6, depending on
its position in the mirror — is just a lookup.

Each segment also has up to 12 numbered sensor positions around its 6
edges (2 per edge that actually borders another segment). Odd-numbered
sensors are "sense" sensors and even-numbered sensors are "drive"
sensors; a sensor of one type always faces a sensor of the other type
on the neighboring segment across their shared edge.

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency
management.

```bash
uv sync
```

## Quick start

```python
from neighbors import neighbors, sensors, sense_sensors, drive_sensors

neighbors("A15")
# ['A10', 'A16', 'A21', 'A22', 'B20', 'B27']

sensors("A15")
# [Sensor(segment_id='A15', number=1), Sensor(segment_id='A15', number=2), ...]

sense_sensors("A1")
# [(('A1', 2), ('A3', 7)), (('A1', 4), ('B5', 7)), ...]
```

Running the package as a script (or via the `neighbors` console command
installed by `uv sync`) prints a short demo for a sample segment:

```bash
uv run python -m neighbors
```

## Public API

Everything below is importable directly from the `neighbors` package
(e.g. `from neighbors import neighbors, sensors`).

### Segment lookups (`neighbors.mirror`)

- **`neighbors(segment_id: str) -> list[str]`**
  Returns the identifiers of the segments adjacent to `segment_id`. A
  segment identifier is a sector letter (A–F) followed by a segment
  number (1–82), e.g. `"A22"`. Depending on its position in the mirror,
  a segment has 3, 4, 5, or 6 neighbors. Raises `ValueError` if
  `segment_id` is not a valid segment identifier.

- **`neighbor_by_direction(segment_id: str) -> dict[int, str]`**
  Maps each hex-direction index (0–5, indexing into
  `neighbors.hexgrid.HEX_DIRECTIONS`) to the neighbor of `segment_id` in
  that direction. Only directions that actually have a neighboring
  segment are included, so the result has between 3 and 6 entries. This
  is the lower-level building block behind `neighbors()` and the edge
  sensor model, since sensor lookups need to know *which* edge each
  neighbor is on, not just the set of neighbors. Raises `ValueError` if
  `segment_id` is not a valid segment identifier.

### Sensor lookups (`neighbors.sensors`)

- **`sensors(segment_id: str) -> list[Sensor]`**
  Returns the sensors mounted on `segment_id`, in numeric order. There
  are 2 sensors on every edge that borders another segment, so this
  returns between 3 and 12 `Sensor` objects depending on how many
  neighbors the segment has. Raises `ValueError` if `segment_id` is not
  a valid segment identifier.

- **`sensor_count(segment_id: str) -> int`**
  Returns how many sensors are mounted on `segment_id` (3–12). Raises
  `ValueError` if `segment_id` is not a valid segment identifier.

- **`facing(sensor: Sensor) -> Sensor`**
  Returns the sensor across the shared edge from `sensor`. Every mounted
  sensor faces exactly one sensor on the neighboring segment, and it is
  always the opposite type: a sense sensor faces a drive sensor, and a
  drive sensor faces a sense sensor. Raises `ValueError` if `sensor`
  isn't actually mounted (its edge has no neighboring segment).

- **`sense_sensors(segment_id: str) -> list[SensorPair]`**
  For each of `segment_id`'s own drive sensors, returns a
  `((segment_id, drive_number), (neighbor_id, sense_number))` pair
  giving that drive sensor and the sense sensor — on a neighbor — that
  faces it across their shared edge. Ordered by `segment_id`'s own
  sensor number. Raises `ValueError` if `segment_id` is not a valid
  segment identifier.

- **`drive_sensors(segment_id: str) -> list[SensorPair]`**
  The mirror image of `sense_sensors()`: for each of `segment_id`'s own
  sense sensors, returns a `((segment_id, sense_number), (neighbor_id,
  drive_number))` pair giving that sense sensor and the drive sensor —
  on a neighbor — that faces it. Raises `ValueError` if `segment_id` is
  not a valid segment identifier.

- **`print_sense_sensors(segment_id: str) -> None`** /
  **`print_drive_sensors(segment_id: str) -> None`**
  Convenience wrappers that print `sense_sensors()` / `drive_sensors()`
  in a human-readable form, one line per pair (e.g. `A1-2 faces A3-7`),
  instead of returning the raw nested tuples.

### Data types

- **`Hex(q: int, r: int, s: int)`**
  A frozen dataclass representing a location on a hexagonal grid in
  cube coordinates, where `q + r + s == 0` (raises `ValueError`
  otherwise). Supports addition (`hex_a + hex_b`) and has a
  `rotated_left()` method that returns the location rotated 60 degrees
  about the origin — the building block used to generate sectors B–F
  from sector A's layout.

- **`Sensor(segment_id: str, number: int)`**
  A frozen dataclass representing one numbered sensor (1–12) mounted on
  a segment. Raises `ValueError` if `number` is out of range. Exposes
  two read-only properties: `id` (a human-readable identifier, e.g.
  `"A1-5"`) and `type` (the sensor's `SensorType`, derived from whether
  its number is odd or even).

- **`SensorType`**
  An `Enum` with two members, `SENSE` and `DRIVE`, identifying whether a
  sensor is odd-numbered (sense) or even-numbered (drive).

- **`SensorPair`**
  A type alias for `tuple[tuple[str, int], tuple[str, int]]` — the
  `(own, facing)` shape returned by `sense_sensors()` and
  `drive_sensors()`.

### Constants

- **`SECTORS`** — the string `"ABCDEF"`, the six sector letters in order.
- **`SEGMENTS_PER_SECTOR`** — `82`, the number of segments per sector.
- **`SEGMENT_COUNT`** — `492`, the total number of segments in the mirror.
- **`SEGMENT_TO_HEX`** / **`HEX_TO_SEGMENT`** — the mirror's full data
  model: dictionaries mapping every segment id to its `Hex` location and
  back.
- **`SENSORS_PER_SEGMENT`** — `12`, the maximum number of sensor
  positions on a segment.
- **`SENSORS_PER_EDGE`** — `2`, the number of sensor positions per edge.
- **`HEX_DIRECTIONS`** — the six unit `Hex` steps corresponding to the
  six directions of adjacency on the hex grid.

## Development

```bash
uv run pytest                   # run all tests
uv run ruff check .             # lint
uv run ruff format .            # format
```

Every public function is fully covered by the test suite in `tests/`
(61 test cases across `test_neighbors.py` and `test_sensors.py` as of
this writing), including the edge cases that make this library tricky
to get right: segments with the minimum (3) and maximum (6) number of
neighbors, sector-boundary crossings, and every sense/drive sensor
pairing. A passing run looks like:

```
$ uv run pytest
======================== test session starts =========================
collected 61 items

tests/test_neighbors.py ...............                          [ 24%]
tests/test_sensors.py ..........................................  [100%]

========================= 61 passed in 0.15s ==========================
```
