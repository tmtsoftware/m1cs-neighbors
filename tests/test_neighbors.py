import pytest

from neighbors import (
    SECTORS,
    SEGMENTS_PER_SECTOR,
    SEGMENT_COUNT,
    SEGMENT_TO_HEX,
    neighbors,
)


def test_segment_count() -> None:
    assert SEGMENT_COUNT == 492
    assert len(SEGMENT_TO_HEX) == SEGMENT_COUNT


def test_every_sector_has_82_unique_segments() -> None:
    for sector in SECTORS:
        numbers = {
            int(segment_id[1:])
            for segment_id in SEGMENT_TO_HEX
            if segment_id[0] == sector
        }
        assert numbers == set(range(1, SEGMENTS_PER_SECTOR + 1))


def test_a15_neighbors_match_known_example() -> None:
    assert neighbors("A15") == sorted(
        ["A10", "A16", "A22", "A21", "B27", "B20"],
        key=lambda s: (s[0], int(s[1:])),
    )


def test_a77_is_a_three_neighbor_corner_segment() -> None:
    assert neighbors("A77") == ["A68", "A69", "A78"]


def test_c21_neighbors_cross_into_sector_d() -> None:
    # C21 sits on the boundary between sectors C and D, but away from both
    # the center hole and the outer edge, so it has a full 6 neighbors: 4
    # within sector C and 2 across the boundary in sector D.
    assert neighbors("C21") == ["C15", "C22", "C28", "C29", "D27", "D35"]


def test_e1_neighbors_cross_into_sector_f_next_to_the_hole() -> None:
    # E1 is one of the two segments closest to the center hole, on the
    # boundary with sector F. Being next to the hole costs it one of its
    # six potential neighbors, leaving 3 within sector E and 2 in sector F.
    assert neighbors("E1") == ["E2", "E3", "E4", "F2", "F5"]


def test_f55_neighbors_cross_into_sector_a_at_the_outer_edge() -> None:
    # F55 sits on the boundary with sector A, at the outer edge of the
    # mirror where the outermost ring is truncated. That truncation costs
    # it one of its six potential neighbors, leaving 3 within sector F and
    # 2 in sector A.
    assert neighbors("F55") == ["A65", "A76", "F45", "F56", "F66"]


def test_b82_is_a_three_neighbor_segment_within_its_own_sector() -> None:
    # B82 is the last segment of sector B's short outer ring, tucked in
    # the angular middle of the sector rather than on a sector boundary.
    # Like A77, the outer-ring truncation leaves it with only 3
    # neighbors, and all of them stay within sector B.
    assert neighbors("B82") == ["B73", "B74", "B81"]


def test_a76_neighbors_cross_into_sector_f_at_the_outer_edge() -> None:
    # A76 sits right on the boundary with sector F, at the same truncated
    # outer ring as A77 and F55 (it's the reciprocal of F55's cross-sector
    # neighbor). Unlike A77, which is tucked away from any sector
    # boundary, A76 loses a neighbor to the truncation *and* crosses the
    # boundary, leaving 2 within sector A and 1 in sector F.
    assert neighbors("A76") == ["A65", "A75", "F55"]


# Expected neighbors for every one of sector F's 82 segments. These were
# derived independently of this module, by locating each segment's
# hexagon in the mirror figure and reading off its physical neighbors
# directly, rather than from the neighbors() implementation. Checking
# every segment in a sector (rather than a handful of examples) exercises
# the full range of interior, hole-adjacent, sector-boundary, and
# outer-edge-truncation cases in one place.
SECTOR_F_EXPECTED_NEIGHBORS = {
    "F1": ["A2", "A5", "F2", "F3", "F4"],
    "F2": ["E1", "F1", "F4", "F5"],
    "F3": ["A5", "A9", "F1", "F4", "F6", "F7"],
    "F4": ["F1", "F2", "F3", "F5", "F7", "F8"],
    "F5": ["E1", "E3", "F2", "F4", "F8", "F9"],
    "F6": ["A9", "A14", "F3", "F7", "F10", "F11"],
    "F7": ["F3", "F4", "F6", "F8", "F11", "F12"],
    "F8": ["F4", "F5", "F7", "F9", "F12", "F13"],
    "F9": ["E3", "E6", "F5", "F8", "F13", "F14"],
    "F10": ["A14", "A20", "F6", "F11", "F15", "F16"],
    "F11": ["F6", "F7", "F10", "F12", "F16", "F17"],
    "F12": ["F7", "F8", "F11", "F13", "F17", "F18"],
    "F13": ["F8", "F9", "F12", "F14", "F18", "F19"],
    "F14": ["E6", "E10", "F9", "F13", "F19", "F20"],
    "F15": ["A20", "A27", "F10", "F16", "F21", "F22"],
    "F16": ["F10", "F11", "F15", "F17", "F22", "F23"],
    "F17": ["F11", "F12", "F16", "F18", "F23", "F24"],
    "F18": ["F12", "F13", "F17", "F19", "F24", "F25"],
    "F19": ["F13", "F14", "F18", "F20", "F25", "F26"],
    "F20": ["E10", "E15", "F14", "F19", "F26", "F27"],
    "F21": ["A27", "A35", "F15", "F22", "F28", "F29"],
    "F22": ["F15", "F16", "F21", "F23", "F29", "F30"],
    "F23": ["F16", "F17", "F22", "F24", "F30", "F31"],
    "F24": ["F17", "F18", "F23", "F25", "F31", "F32"],
    "F25": ["F18", "F19", "F24", "F26", "F32", "F33"],
    "F26": ["F19", "F20", "F25", "F27", "F33", "F34"],
    "F27": ["E15", "E21", "F20", "F26", "F34", "F35"],
    "F28": ["A35", "A44", "F21", "F29", "F36", "F37"],
    "F29": ["F21", "F22", "F28", "F30", "F37", "F38"],
    "F30": ["F22", "F23", "F29", "F31", "F38", "F39"],
    "F31": ["F23", "F24", "F30", "F32", "F39", "F40"],
    "F32": ["F24", "F25", "F31", "F33", "F40", "F41"],
    "F33": ["F25", "F26", "F32", "F34", "F41", "F42"],
    "F34": ["F26", "F27", "F33", "F35", "F42", "F43"],
    "F35": ["E21", "E28", "F27", "F34", "F43", "F44"],
    "F36": ["A44", "A54", "F28", "F37", "F45", "F46"],
    "F37": ["F28", "F29", "F36", "F38", "F46", "F47"],
    "F38": ["F29", "F30", "F37", "F39", "F47", "F48"],
    "F39": ["F30", "F31", "F38", "F40", "F48", "F49"],
    "F40": ["F31", "F32", "F39", "F41", "F49", "F50"],
    "F41": ["F32", "F33", "F40", "F42", "F50", "F51"],
    "F42": ["F33", "F34", "F41", "F43", "F51", "F52"],
    "F43": ["F34", "F35", "F42", "F44", "F52", "F53"],
    "F44": ["E28", "E36", "F35", "F43", "F53", "F54"],
    "F45": ["A54", "A65", "F36", "F46", "F55", "F56"],
    "F46": ["F36", "F37", "F45", "F47", "F56", "F57"],
    "F47": ["F37", "F38", "F46", "F48", "F57", "F58"],
    "F48": ["F38", "F39", "F47", "F49", "F58", "F59"],
    "F49": ["F39", "F40", "F48", "F50", "F59", "F60"],
    "F50": ["F40", "F41", "F49", "F51", "F60", "F61"],
    "F51": ["F41", "F42", "F50", "F52", "F61", "F62"],
    "F52": ["F42", "F43", "F51", "F53", "F62", "F63"],
    "F53": ["F43", "F44", "F52", "F54", "F63", "F64"],
    "F54": ["E36", "E45", "F44", "F53", "F64", "F65"],
    "F55": ["A65", "A76", "F45", "F56", "F66"],
    "F56": ["F45", "F46", "F55", "F57", "F66", "F67"],
    "F57": ["F46", "F47", "F56", "F58", "F67", "F68"],
    "F58": ["F47", "F48", "F57", "F59", "F68", "F69"],
    "F59": ["F48", "F49", "F58", "F60", "F69", "F70"],
    "F60": ["F49", "F50", "F59", "F61", "F70", "F71"],
    "F61": ["F50", "F51", "F60", "F62", "F71", "F72"],
    "F62": ["F51", "F52", "F61", "F63", "F72", "F73"],
    "F63": ["F52", "F53", "F62", "F64", "F73", "F74"],
    "F64": ["F53", "F54", "F63", "F65", "F74", "F75"],
    "F65": ["E45", "E55", "F54", "F64", "F75", "F76"],
    "F66": ["F55", "F56", "F67"],
    "F67": ["F56", "F57", "F66", "F68"],
    "F68": ["F57", "F58", "F67", "F69", "F77"],
    "F69": ["F58", "F59", "F68", "F70", "F77", "F78"],
    "F70": ["F59", "F60", "F69", "F71", "F78", "F79"],
    "F71": ["F60", "F61", "F70", "F72", "F79", "F80"],
    "F72": ["F61", "F62", "F71", "F73", "F80", "F81"],
    "F73": ["F62", "F63", "F72", "F74", "F81", "F82"],
    "F74": ["F63", "F64", "F73", "F75", "F82"],
    "F75": ["F64", "F65", "F74", "F76"],
    "F76": ["E55", "F65", "F75"],
    "F77": ["F68", "F69", "F78"],
    "F78": ["F69", "F70", "F77", "F79"],
    "F79": ["F70", "F71", "F78", "F80"],
    "F80": ["F71", "F72", "F79", "F81"],
    "F81": ["F72", "F73", "F80", "F82"],
    "F82": ["F73", "F74", "F81"],
}


def test_sector_f_expected_neighbors_cover_every_segment() -> None:
    assert set(SECTOR_F_EXPECTED_NEIGHBORS) == {f"F{n}" for n in range(1, 83)}


@pytest.mark.parametrize("segment_id", sorted(SECTOR_F_EXPECTED_NEIGHBORS))
def test_neighbors_for_every_segment_in_sector_f(segment_id: str) -> None:
    assert neighbors(segment_id) == SECTOR_F_EXPECTED_NEIGHBORS[segment_id]


def test_neighbor_counts_are_in_valid_range() -> None:
    counts = {len(neighbors(segment_id)) for segment_id in SEGMENT_TO_HEX}
    assert counts <= {3, 4, 5, 6}


def test_neighbor_relationship_is_symmetric() -> None:
    for segment_id in SEGMENT_TO_HEX:
        for neighbor_id in neighbors(segment_id):
            assert segment_id in neighbors(neighbor_id)


def test_no_segment_is_its_own_neighbor() -> None:
    for segment_id in SEGMENT_TO_HEX:
        assert segment_id not in neighbors(segment_id)


@pytest.mark.parametrize("bad_id", ["", "G1", "A0", "A83", "A", "1A", "AA1"])
def test_invalid_segment_id_raises(bad_id: str) -> None:
    with pytest.raises(ValueError):
        neighbors(bad_id)
