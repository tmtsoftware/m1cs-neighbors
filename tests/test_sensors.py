import contextlib
import io

import pytest

from neighbors import (
    SEGMENT_TO_HEX,
    Sensor,
    SensorPair,
    SensorType,
    drive_sensors,
    facing,
    neighbors,
    print_drive_sensors,
    print_sense_sensors,
    sense_sensors,
    sensor_count,
    sensors,
)


def test_sensor_count_is_twice_the_neighbor_count() -> None:
    for segment_id in SEGMENT_TO_HEX:
        assert sensor_count(segment_id) == 2 * len(neighbors(segment_id))


def test_a15_has_a_full_set_of_12_sensors() -> None:
    # A15 has 6 neighbors, so all 6 of its edges border another segment.
    assert sensor_count("A15") == 12
    assert [s.number for s in sensors("A15")] == list(range(1, 13))


def test_a77_has_6_sensors() -> None:
    # A77 is the 3-neighbor outer-ring-truncation corner from the
    # neighbors() tests, so only 3 of its 6 edges have sensors.
    assert sensor_count("A77") == 6


def test_a1_and_a2_are_missing_sensors_facing_the_hole() -> None:
    # A1 and A2 are the two segments closest to the center hole. A1 has
    # 5 neighbors (missing the edge that faces the hole), and A2 has 4
    # (missing two edges that face the hole), so they have fewer than
    # the maximum 12 sensors.
    assert sensor_count("A1") == 10
    assert sensor_count("A2") == 8


@pytest.mark.parametrize(
    "segment_id,number,expected",
    [
        # Given examples, all within sector A: no sector-boundary
        # rotation is involved, so the neighbor's sensor number is
        # determined purely by going around the hexagon.
        ("A1", 1, ("A3", 8)),
        ("A1", 11, ("A4", 6)),
        # Given examples where the edge crosses the A/B sector
        # boundary. Sector B's numbering is rotated 60 degrees
        # (one edge) further counter-clockwise than sector A's, so
        # the facing sensor's number is different from what the
        # same-sector cases above would suggest.
        ("A1", 5, ("B2", 10)),
        ("A1", 3, ("B5", 8)),
    ],
)
def test_facing_matches_known_examples(
    segment_id: str, number: int, expected: tuple[str, int]
) -> None:
    result = facing(Sensor(segment_id, number))
    assert (result.segment_id, result.number) == expected


def test_facing_is_symmetric() -> None:
    # If sensor X faces sensor Y, sensor Y must face sensor X back.
    for segment_id in SEGMENT_TO_HEX:
        for sensor in sensors(segment_id):
            assert facing(facing(sensor)) == sensor


def test_facing_partner_is_on_an_actual_neighbor() -> None:
    for segment_id in SEGMENT_TO_HEX:
        for sensor in sensors(segment_id):
            partner = facing(sensor)
            assert partner.segment_id in neighbors(segment_id)


def test_every_edge_has_exactly_two_sensors_facing_each_other() -> None:
    for segment_id in SEGMENT_TO_HEX:
        for neighbor_id in neighbors(segment_id):
            partners = {
                sensor.number
                for sensor in sensors(segment_id)
                if facing(sensor).segment_id == neighbor_id
            }
            assert len(partners) == 2


@pytest.mark.parametrize("number", [1, 3, 5, 7, 9, 11])
def test_odd_numbered_sensors_are_sense_sensors(number: int) -> None:
    assert Sensor("A15", number).type is SensorType.SENSE


@pytest.mark.parametrize("number", [2, 4, 6, 8, 10, 12])
def test_even_numbered_sensors_are_drive_sensors(number: int) -> None:
    assert Sensor("A15", number).type is SensorType.DRIVE


def test_a_sensor_always_faces_the_opposite_type() -> None:
    for segment_id in SEGMENT_TO_HEX:
        for sensor in sensors(segment_id):
            assert facing(sensor).type != sensor.type


def test_sensor_id_format() -> None:
    assert Sensor("A1", 5).id == "A1-5"


def test_sensor_requires_valid_number() -> None:
    with pytest.raises(ValueError):
        Sensor("A1", 0)
    with pytest.raises(ValueError):
        Sensor("A1", 13)


def test_facing_raises_for_a_sensor_that_does_not_exist() -> None:
    # A1 has no neighbor facing the center hole, so it has no sensors 7
    # or 8 (see test_a1_and_a2_are_missing_sensors_facing_the_hole).
    numbers = {s.number for s in sensors("A1")}
    assert 7 not in numbers
    with pytest.raises(ValueError):
        facing(Sensor("A1", 7))


@pytest.mark.parametrize("bad_id", ["", "G1", "A0", "A83", "A", "1A", "AA1"])
def test_invalid_segment_id_raises(bad_id: str) -> None:
    with pytest.raises(ValueError):
        sensors(bad_id)
    with pytest.raises(ValueError):
        sensor_count(bad_id)


def test_sense_sensors_matches_given_example_for_a1() -> None:
    # A1 has neighbors A2, A3, A4 (within sector A) and B2, B5 (crossing
    # the sector boundary into B). Each pair is (A1's own drive sensor,
    # the neighbor's sense sensor that faces it).
    assert sense_sensors("A1") == [
        (("A1", 2), ("A3", 7)),
        (("A1", 4), ("B5", 7)),
        (("A1", 6), ("B2", 9)),
        (("A1", 10), ("A2", 3)),
        (("A1", 12), ("A4", 5)),
    ]


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # The "number 1" segment of each sector has the same layout as
        # A1, just rotated into that sector: 3 neighbors within its own
        # sector and 2 crossing into the next sector counter-clockwise.
        # This exercises sense_sensors() for a segment in every sector,
        # and every one of these cases also crosses a sector boundary.
        (
            "A1",
            [
                (("A1", 2), ("A3", 7)),
                (("A1", 4), ("B5", 7)),
                (("A1", 6), ("B2", 9)),
                (("A1", 10), ("A2", 3)),
                (("A1", 12), ("A4", 5)),
            ],
        ),
        (
            "B1",
            [
                (("B1", 2), ("B3", 7)),
                (("B1", 4), ("C5", 7)),
                (("B1", 6), ("C2", 9)),
                (("B1", 10), ("B2", 3)),
                (("B1", 12), ("B4", 5)),
            ],
        ),
        (
            "C1",
            [
                (("C1", 2), ("C3", 7)),
                (("C1", 4), ("D5", 7)),
                (("C1", 6), ("D2", 9)),
                (("C1", 10), ("C2", 3)),
                (("C1", 12), ("C4", 5)),
            ],
        ),
        (
            "D1",
            [
                (("D1", 2), ("D3", 7)),
                (("D1", 4), ("E5", 7)),
                (("D1", 6), ("E2", 9)),
                (("D1", 10), ("D2", 3)),
                (("D1", 12), ("D4", 5)),
            ],
        ),
        (
            "E1",
            [
                (("E1", 2), ("E3", 7)),
                (("E1", 4), ("F5", 7)),
                (("E1", 6), ("F2", 9)),
                (("E1", 10), ("E2", 3)),
                (("E1", 12), ("E4", 5)),
            ],
        ),
        # F wraps back around to sector A.
        (
            "F1",
            [
                (("F1", 2), ("F3", 7)),
                (("F1", 4), ("A5", 7)),
                (("F1", 6), ("A2", 9)),
                (("F1", 10), ("F2", 3)),
                (("F1", 12), ("F4", 5)),
            ],
        ),
    ],
)
def test_sense_sensors_works_in_every_sector(
    segment_id: str, expected: list[SensorPair]
) -> None:
    assert sense_sensors(segment_id) == expected


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # C21 sits on the C/D sector boundary (see the neighbors() and
        # facing() tests), with a full 6 neighbors.
        (
            "C21",
            [
                (("C21", 2), ("C28", 7)),
                (("C21", 4), ("D35", 7)),
                (("C21", 6), ("D27", 9)),
                (("C21", 8), ("C15", 1)),
                (("C21", 10), ("C22", 3)),
                (("C21", 12), ("C29", 5)),
            ],
        ),
        # F55 sits on the F/A sector boundary, at the truncated outer
        # ring, with only 5 neighbors.
        (
            "F55",
            [
                (("F55", 4), ("A76", 7)),
                (("F55", 6), ("A65", 9)),
                (("F55", 8), ("F45", 1)),
                (("F55", 10), ("F56", 3)),
                (("F55", 12), ("F66", 5)),
            ],
        ),
    ],
)
def test_sense_sensors_on_segments_facing_another_sector(
    segment_id: str, expected: list[SensorPair]
) -> None:
    assert sense_sensors(segment_id) == expected


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # Entirely within one sector: every neighbor is in the same
        # sector as segment_id, away from both the center hole and the
        # outer edge, so this is a "typical interior" segment with a
        # full 6 neighbors and no sector-boundary crossing at all.
        (
            "A16",
            [
                (("A16", 2), ("A22", 7)),
                (("A16", 4), ("A15", 9)),
                (("A16", 6), ("A10", 11)),
                (("A16", 8), ("A11", 1)),
                (("A16", 10), ("A17", 3)),
                (("A16", 12), ("A23", 5)),
            ],
        ),
        (
            "D17",
            [
                (("D17", 2), ("D23", 7)),
                (("D17", 4), ("D16", 9)),
                (("D17", 6), ("D11", 11)),
                (("D17", 8), ("D12", 1)),
                (("D17", 10), ("D18", 3)),
                (("D17", 12), ("D24", 5)),
            ],
        ),
    ],
)
def test_sense_sensors_entirely_within_one_sector(
    segment_id: str, expected: list[SensorPair]
) -> None:
    assert all(neighbor[0] == segment_id[0] for neighbor in neighbors(segment_id))
    assert len(neighbors(segment_id)) == 6
    assert sense_sensors(segment_id) == expected


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # On a sector boundary, but away from the center hole and the
        # outer edge: a full 6 neighbors, most within segment_id's own
        # sector but some across the boundary in the next sector.
        (
            "A15",
            [
                (("A15", 2), ("A21", 7)),
                (("A15", 4), ("B27", 7)),
                (("A15", 6), ("B20", 9)),
                (("A15", 8), ("A10", 1)),
                (("A15", 10), ("A16", 3)),
                (("A15", 12), ("A22", 5)),
            ],
        ),
        (
            "E21",
            [
                (("E21", 2), ("E28", 7)),
                (("E21", 4), ("F35", 7)),
                (("E21", 6), ("F27", 9)),
                (("E21", 8), ("E15", 1)),
                (("E21", 10), ("E22", 3)),
                (("E21", 12), ("E29", 5)),
            ],
        ),
    ],
)
def test_sense_sensors_on_sector_boundary_away_from_hole_and_outer_edge(
    segment_id: str, expected: list[SensorPair]
) -> None:
    neighbor_ids = neighbors(segment_id)
    assert len(neighbor_ids) == 6
    assert any(neighbor[0] != segment_id[0] for neighbor in neighbor_ids)
    assert sense_sensors(segment_id) == expected


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # On the outer edge (the mirror's outermost ring is truncated,
        # see neighbors.mirror), but entirely within one sector: fewer
        # than 6 neighbors, none of them across a sector boundary.
        (
            "A77",
            [
                (("A77", 6), ("A68", 11)),
                (("A77", 8), ("A69", 1)),
                (("A77", 10), ("A78", 3)),
            ],
        ),
        (
            "D82",
            [
                (("D82", 4), ("D81", 9)),
                (("D82", 6), ("D73", 11)),
                (("D82", 8), ("D74", 1)),
            ],
        ),
        # On the outer edge *and* on a sector boundary at the same
        # time, in the two different ways that combination happens:
        # A55 keeps all 3 same-sector neighbors but loses one
        # outward-facing neighbor to the truncation, while A76 is the
        # opposite -- it's the truncated corner itself, so it keeps
        # only 2 same-sector neighbors plus the 1 that crosses into F.
        (
            "A55",
            [
                (("A55", 4), ("B76", 7)),
                (("A55", 6), ("B65", 9)),
                (("A55", 8), ("A45", 1)),
                (("A55", 10), ("A56", 3)),
                (("A55", 12), ("A66", 5)),
            ],
        ),
        (
            "A76",
            [
                (("A76", 4), ("A75", 9)),
                (("A76", 6), ("A65", 11)),
                (("A76", 8), ("F55", 3)),
            ],
        ),
    ],
)
def test_sense_sensors_on_the_outer_edge(
    segment_id: str, expected: list[SensorPair]
) -> None:
    assert len(neighbors(segment_id)) < 6
    assert sense_sensors(segment_id) == expected


def test_sense_sensors_has_one_entry_per_neighbor() -> None:
    for segment_id in SEGMENT_TO_HEX:
        result = sense_sensors(segment_id)
        assert len(result) == len(neighbors(segment_id))
        assert {neighbor_id for _, (neighbor_id, _) in result} == set(
            neighbors(segment_id)
        )


def test_sense_sensors_own_side_is_all_of_this_segments_drive_sensors() -> None:
    for segment_id in SEGMENT_TO_HEX:
        own_numbers = {number for (_, number), _ in sense_sensors(segment_id)}
        expected = {s.number for s in sensors(segment_id) if s.type is SensorType.DRIVE}
        assert own_numbers == expected


def test_sense_sensors_facing_side_is_always_a_sense_sensor() -> None:
    for segment_id in SEGMENT_TO_HEX:
        for _, (neighbor_id, number) in sense_sensors(segment_id):
            assert Sensor(neighbor_id, number).type is SensorType.SENSE


def test_sense_sensors_pairs_are_mutually_facing() -> None:
    # Each (own, facing) pair returned by sense_sensors should be exactly
    # the pair of sensors that face each other across that edge -- i.e.
    # facing(own) == facing_sensor and facing(facing_sensor) == own.
    for segment_id in SEGMENT_TO_HEX:
        for own, facing_pair in sense_sensors(segment_id):
            own_sensor = Sensor(*own)
            facing_sensor = Sensor(*facing_pair)
            assert facing(own_sensor) == facing_sensor
            assert facing(facing_sensor) == own_sensor


@pytest.mark.parametrize("bad_id", ["", "G1", "A0", "A83", "A", "1A", "AA1"])
def test_sense_sensors_invalid_segment_id_raises(bad_id: str) -> None:
    with pytest.raises(ValueError):
        sense_sensors(bad_id)


def test_drive_sensors_matches_given_example_for_a1() -> None:
    # A1 has neighbors A2, A3, A4 (within sector A) and B2, B5 (crossing
    # the sector boundary into B). Each pair is (A1's own sense sensor,
    # the neighbor's drive sensor that faces it).
    assert drive_sensors("A1") == [
        (("A1", 1), ("A3", 8)),
        (("A1", 3), ("B5", 8)),
        (("A1", 5), ("B2", 10)),
        (("A1", 9), ("A2", 4)),
        (("A1", 11), ("A4", 6)),
    ]


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # The "number 1" segment of each sector has the same layout as
        # A1, just rotated into that sector: 3 neighbors within its own
        # sector and 2 crossing into the next sector counter-clockwise.
        # This exercises drive_sensors() for a segment in every sector,
        # and every one of these cases also crosses a sector boundary.
        (
            "A1",
            [
                (("A1", 1), ("A3", 8)),
                (("A1", 3), ("B5", 8)),
                (("A1", 5), ("B2", 10)),
                (("A1", 9), ("A2", 4)),
                (("A1", 11), ("A4", 6)),
            ],
        ),
        (
            "B1",
            [
                (("B1", 1), ("B3", 8)),
                (("B1", 3), ("C5", 8)),
                (("B1", 5), ("C2", 10)),
                (("B1", 9), ("B2", 4)),
                (("B1", 11), ("B4", 6)),
            ],
        ),
        (
            "C1",
            [
                (("C1", 1), ("C3", 8)),
                (("C1", 3), ("D5", 8)),
                (("C1", 5), ("D2", 10)),
                (("C1", 9), ("C2", 4)),
                (("C1", 11), ("C4", 6)),
            ],
        ),
        (
            "D1",
            [
                (("D1", 1), ("D3", 8)),
                (("D1", 3), ("E5", 8)),
                (("D1", 5), ("E2", 10)),
                (("D1", 9), ("D2", 4)),
                (("D1", 11), ("D4", 6)),
            ],
        ),
        (
            "E1",
            [
                (("E1", 1), ("E3", 8)),
                (("E1", 3), ("F5", 8)),
                (("E1", 5), ("F2", 10)),
                (("E1", 9), ("E2", 4)),
                (("E1", 11), ("E4", 6)),
            ],
        ),
        # F wraps back around to sector A.
        (
            "F1",
            [
                (("F1", 1), ("F3", 8)),
                (("F1", 3), ("A5", 8)),
                (("F1", 5), ("A2", 10)),
                (("F1", 9), ("F2", 4)),
                (("F1", 11), ("F4", 6)),
            ],
        ),
    ],
)
def test_drive_sensors_works_in_every_sector(
    segment_id: str, expected: list[SensorPair]
) -> None:
    assert drive_sensors(segment_id) == expected


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # C21 sits on the C/D sector boundary (see the neighbors() and
        # facing() tests), with a full 6 neighbors.
        (
            "C21",
            [
                (("C21", 1), ("C28", 8)),
                (("C21", 3), ("D35", 8)),
                (("C21", 5), ("D27", 10)),
                (("C21", 7), ("C15", 2)),
                (("C21", 9), ("C22", 4)),
                (("C21", 11), ("C29", 6)),
            ],
        ),
        # F55 sits on the F/A sector boundary, at the truncated outer
        # ring, with only 5 neighbors.
        (
            "F55",
            [
                (("F55", 3), ("A76", 8)),
                (("F55", 5), ("A65", 10)),
                (("F55", 7), ("F45", 2)),
                (("F55", 9), ("F56", 4)),
                (("F55", 11), ("F66", 6)),
            ],
        ),
    ],
)
def test_drive_sensors_on_segments_facing_another_sector(
    segment_id: str, expected: list[SensorPair]
) -> None:
    assert drive_sensors(segment_id) == expected


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # Entirely within one sector: every neighbor is in the same
        # sector as segment_id, away from both the center hole and the
        # outer edge, so this is a "typical interior" segment with a
        # full 6 neighbors and no sector-boundary crossing at all.
        (
            "A16",
            [
                (("A16", 1), ("A22", 8)),
                (("A16", 3), ("A15", 10)),
                (("A16", 5), ("A10", 12)),
                (("A16", 7), ("A11", 2)),
                (("A16", 9), ("A17", 4)),
                (("A16", 11), ("A23", 6)),
            ],
        ),
        (
            "D17",
            [
                (("D17", 1), ("D23", 8)),
                (("D17", 3), ("D16", 10)),
                (("D17", 5), ("D11", 12)),
                (("D17", 7), ("D12", 2)),
                (("D17", 9), ("D18", 4)),
                (("D17", 11), ("D24", 6)),
            ],
        ),
    ],
)
def test_drive_sensors_entirely_within_one_sector(
    segment_id: str, expected: list[SensorPair]
) -> None:
    assert all(neighbor[0] == segment_id[0] for neighbor in neighbors(segment_id))
    assert len(neighbors(segment_id)) == 6
    assert drive_sensors(segment_id) == expected


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # On a sector boundary, but away from the center hole and the
        # outer edge: a full 6 neighbors, most within segment_id's own
        # sector but some across the boundary in the next sector.
        (
            "A15",
            [
                (("A15", 1), ("A21", 8)),
                (("A15", 3), ("B27", 8)),
                (("A15", 5), ("B20", 10)),
                (("A15", 7), ("A10", 2)),
                (("A15", 9), ("A16", 4)),
                (("A15", 11), ("A22", 6)),
            ],
        ),
        (
            "E21",
            [
                (("E21", 1), ("E28", 8)),
                (("E21", 3), ("F35", 8)),
                (("E21", 5), ("F27", 10)),
                (("E21", 7), ("E15", 2)),
                (("E21", 9), ("E22", 4)),
                (("E21", 11), ("E29", 6)),
            ],
        ),
    ],
)
def test_drive_sensors_on_sector_boundary_away_from_hole_and_outer_edge(
    segment_id: str, expected: list[SensorPair]
) -> None:
    neighbor_ids = neighbors(segment_id)
    assert len(neighbor_ids) == 6
    assert any(neighbor[0] != segment_id[0] for neighbor in neighbor_ids)
    assert drive_sensors(segment_id) == expected


@pytest.mark.parametrize(
    "segment_id,expected",
    [
        # On the outer edge (the mirror's outermost ring is truncated,
        # see neighbors.mirror), but entirely within one sector: fewer
        # than 6 neighbors, none of them across a sector boundary.
        (
            "A77",
            [
                (("A77", 5), ("A68", 12)),
                (("A77", 7), ("A69", 2)),
                (("A77", 9), ("A78", 4)),
            ],
        ),
        (
            "D82",
            [
                (("D82", 3), ("D81", 10)),
                (("D82", 5), ("D73", 12)),
                (("D82", 7), ("D74", 2)),
            ],
        ),
        # On the outer edge *and* on a sector boundary at the same
        # time, in the two different ways that combination happens:
        # A55 keeps all 3 same-sector neighbors but loses one
        # outward-facing neighbor to the truncation, while A76 is the
        # opposite -- it's the truncated corner itself, so it keeps
        # only 2 same-sector neighbors plus the 1 that crosses into F.
        (
            "A55",
            [
                (("A55", 3), ("B76", 8)),
                (("A55", 5), ("B65", 10)),
                (("A55", 7), ("A45", 2)),
                (("A55", 9), ("A56", 4)),
                (("A55", 11), ("A66", 6)),
            ],
        ),
        (
            "A76",
            [
                (("A76", 3), ("A75", 10)),
                (("A76", 5), ("A65", 12)),
                (("A76", 7), ("F55", 4)),
            ],
        ),
    ],
)
def test_drive_sensors_on_the_outer_edge(
    segment_id: str, expected: list[SensorPair]
) -> None:
    assert len(neighbors(segment_id)) < 6
    assert drive_sensors(segment_id) == expected


def test_drive_sensors_has_one_entry_per_neighbor() -> None:
    for segment_id in SEGMENT_TO_HEX:
        result = drive_sensors(segment_id)
        assert len(result) == len(neighbors(segment_id))
        assert {neighbor_id for _, (neighbor_id, _) in result} == set(
            neighbors(segment_id)
        )


def test_drive_sensors_own_side_is_all_of_this_segments_sense_sensors() -> None:
    for segment_id in SEGMENT_TO_HEX:
        own_numbers = {number for (_, number), _ in drive_sensors(segment_id)}
        expected = {s.number for s in sensors(segment_id) if s.type is SensorType.SENSE}
        assert own_numbers == expected


def test_drive_sensors_facing_side_is_always_a_drive_sensor() -> None:
    for segment_id in SEGMENT_TO_HEX:
        for _, (neighbor_id, number) in drive_sensors(segment_id):
            assert Sensor(neighbor_id, number).type is SensorType.DRIVE


def test_drive_sensors_pairs_are_mutually_facing() -> None:
    # Each (own, facing) pair returned by drive_sensors should be
    # exactly the pair of sensors that face each other across that
    # edge -- i.e. facing(own) == facing_sensor and
    # facing(facing_sensor) == own.
    for segment_id in SEGMENT_TO_HEX:
        for own, facing_pair in drive_sensors(segment_id):
            own_sensor = Sensor(*own)
            facing_sensor = Sensor(*facing_pair)
            assert facing(own_sensor) == facing_sensor
            assert facing(facing_sensor) == own_sensor


def test_sense_sensors_and_drive_sensors_cover_every_sensor_exactly_once() -> None:
    # Between them, sense_sensors (own side = drive sensors) and
    # drive_sensors (own side = sense sensors) should account for every
    # sensor on a segment exactly once.
    for segment_id in SEGMENT_TO_HEX:
        sense_own = {number for (_, number), _ in sense_sensors(segment_id)}
        drive_own = {number for (_, number), _ in drive_sensors(segment_id)}
        assert sense_own.isdisjoint(drive_own)
        assert sense_own | drive_own == {s.number for s in sensors(segment_id)}


@pytest.mark.parametrize("bad_id", ["", "G1", "A0", "A83", "A", "1A", "AA1"])
def test_drive_sensors_invalid_segment_id_raises(bad_id: str) -> None:
    with pytest.raises(ValueError):
        drive_sensors(bad_id)


def _captured_output(print_func, segment_id: str) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        print_func(segment_id)
    return buffer.getvalue()


def test_print_sense_sensors_matches_given_example_for_a1() -> None:
    assert _captured_output(print_sense_sensors, "A1") == (
        "A1-2 faces A3-7\n"
        "A1-4 faces B5-7\n"
        "A1-6 faces B2-9\n"
        "A1-10 faces A2-3\n"
        "A1-12 faces A4-5\n"
    )


def test_print_sense_sensors_has_no_parentheses() -> None:
    output = _captured_output(print_sense_sensors, "A1")
    assert "(" not in output
    assert ")" not in output


def test_print_sense_sensors_matches_sense_sensors_for_every_segment() -> None:
    for segment_id in SEGMENT_TO_HEX:
        expected_lines = [
            f"{Sensor(*own).id} faces {Sensor(*neighbor).id}"
            for own, neighbor in sense_sensors(segment_id)
        ]
        expected = "".join(line + "\n" for line in expected_lines)
        assert _captured_output(print_sense_sensors, segment_id) == expected


@pytest.mark.parametrize("bad_id", ["", "G1", "A0", "A83", "A", "1A", "AA1"])
def test_print_sense_sensors_invalid_segment_id_raises(bad_id: str) -> None:
    with pytest.raises(ValueError):
        print_sense_sensors(bad_id)


def test_print_drive_sensors_matches_given_example_for_a1() -> None:
    assert _captured_output(print_drive_sensors, "A1") == (
        "A1-1 faces A3-8\n"
        "A1-3 faces B5-8\n"
        "A1-5 faces B2-10\n"
        "A1-9 faces A2-4\n"
        "A1-11 faces A4-6\n"
    )


def test_print_drive_sensors_has_no_parentheses() -> None:
    output = _captured_output(print_drive_sensors, "A1")
    assert "(" not in output
    assert ")" not in output


def test_print_drive_sensors_matches_drive_sensors_for_every_segment() -> None:
    for segment_id in SEGMENT_TO_HEX:
        expected_lines = [
            f"{Sensor(*own).id} faces {Sensor(*neighbor).id}"
            for own, neighbor in drive_sensors(segment_id)
        ]
        expected = "".join(line + "\n" for line in expected_lines)
        assert _captured_output(print_drive_sensors, segment_id) == expected


@pytest.mark.parametrize("bad_id", ["", "G1", "A0", "A83", "A", "1A", "AA1"])
def test_print_drive_sensors_invalid_segment_id_raises(bad_id: str) -> None:
    with pytest.raises(ValueError):
        print_drive_sensors(bad_id)
