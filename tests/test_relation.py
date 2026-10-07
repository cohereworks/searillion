from math import comb

import pytest

from searillion.relation import Carrier, RelationUniverse


def make_2x2():
    a = Carrier("A", ["a0", "a1"])
    b = Carrier("B", ["b0", "b1"])
    return RelationUniverse(a, b)


def test_all_relations_matches_power_set():
    u = make_2x2()
    assert u.atom_count == 4
    assert len(u.all()) == 16
    assert u.relation_count == 16


def test_exact_cardinality_family():
    u = make_2x2()
    for k in range(5):
        assert len(u.exactly(k)) == comb(4, k)


def test_include_exclude_pair():
    u = make_2x2()
    all_relations = u.all()
    containing = all_relations.including(("a0", "b0"))
    excluding = all_relations.excluding(("a0", "b0"))
    assert len(containing) == 8
    assert len(excluding) == 8
    assert len(containing & excluding) == 0
    assert len(containing | excluding) == 16


def test_explicit_round_trip():
    u = make_2x2()
    expected = {
        frozenset(),
        frozenset({("a0", "b0")}),
        frozenset({("a0", "b1"), ("a1", "b0")}),
    }
    f = u.explicit(expected)
    assert set(f.relations()) == expected


def test_cross_universe_algebra_rejected():
    u1 = make_2x2()
    u2 = make_2x2()
    with pytest.raises(ValueError):
        _ = u1.all() | u2.all()


def test_duplicate_carrier_elements_rejected():
    with pytest.raises(ValueError):
        Carrier("bad", [1, 1])

def test_exact_count_exceeds_python_len_limit():
    u = RelationUniverse(Carrier("A", range(8)), Carrier("B", range(8)))
    assert u.all().count() == 1 << 64
    with pytest.raises(OverflowError):
        len(u.all())
