import pytest

from searillion.relation import Carrier
from searillion.workspace import RelationWorkspace


def make_workspace():
    a = Carrier("A", [0, 1])
    b = Carrier("B", ["x", "y"])
    c = Carrier("C", [False, True])

    ws = RelationWorkspace()
    r = ws.relation("R", a, b)
    s = ws.relation("S", b, c)
    ws.compile()
    return ws, r, s


def test_multiple_signatures_remain_live_together():
    _ws, r, s = make_workspace()

    rf = r.functions()
    sf = s.functions()

    assert rf.count() == 4
    assert sf.count() == 4

    # Creating/using S must not invalidate R: both live in one compiled universe.
    assert rf.count() == 4
    assert sf.count() == 4


def test_signature_all_is_restricted_to_its_atom_slice():
    ws, r, s = make_workspace()

    assert ws.atom_count == 8
    assert r.atom_count == 4
    assert s.atom_count == 4

    assert r.all().count() == 16
    assert s.all().count() == 16


def test_signature_exact_cardinality_ignores_other_signatures():
    _ws, r, s = make_workspace()

    assert r.exactly(1).count() == 4
    assert s.exactly(2).count() == 6


def test_explicit_round_trip_on_each_signature():
    _ws, r, s = make_workspace()

    r_expected = {
        frozenset(),
        frozenset({(0, "x")}),
        frozenset({(0, "y"), (1, "x")}),
    }
    s_expected = {
        frozenset({("x", True)}),
        frozenset({("x", False), ("y", True)}),
    }

    assert set(r.explicit(r_expected).relations()) == r_expected
    assert set(s.explicit(s_expected).relations()) == s_expected


def test_bijections_are_local_to_signature():
    _ws, r, s = make_workspace()

    assert r.bijections().count() == 2
    assert s.bijections().count() == 2


def test_workspace_is_frozen_after_compile():
    ws, _r, _s = make_workspace()

    with pytest.raises(RuntimeError, match="already compiled"):
        ws.relation("T", Carrier("X", [1]), Carrier("Y", [2]))


def test_duplicate_signature_names_rejected():
    ws = RelationWorkspace()
    a = Carrier("A", [0])
    b = Carrier("B", [1])

    ws.relation("R", a, b)
    with pytest.raises(ValueError, match="duplicate"):
        ws.relation("R", a, b)


def test_new_workspace_invalidates_old_backend_mapping():
    ws1 = RelationWorkspace()
    r1 = ws1.relation("R", Carrier("A", [0]), Carrier("B", [1]))
    ws1.compile()
    f1 = r1.all()

    ws2 = RelationWorkspace()
    ws2.relation("S", Carrier("X", [0]), Carrier("Y", [1]))
    ws2.compile()

    with pytest.raises(RuntimeError, match="inactive"):
        f1.count()


def test_joint_product_counts_cartesian_relation_choices():
    ws, r, s = make_workspace()

    rf = r.functions()
    sf = s.functions()
    joint = ws.product(rf, sf)

    assert rf.count() == 4
    assert sf.count() == 4
    assert joint.count() == 16


def test_joint_product_decodes_back_to_each_signature():
    ws, r, s = make_workspace()

    joint = ws.product(
        r.explicit([
            [(0, "x")],
            [(1, "y")],
        ]),
        s.explicit([
            [("x", True)],
            [("y", False)],
        ]),
    )

    assignments = list(joint.assignments())
    assert len(assignments) == 4
    assert all(set(item) == {"R", "S"} for item in assignments)

    r_values = {item["R"] for item in assignments}
    s_values = {item["S"] for item in assignments}

    assert r_values == {
        frozenset({(0, "x")}),
        frozenset({(1, "y")}),
    }
    assert s_values == {
        frozenset({("x", True)}),
        frozenset({("y", False)}),
    }


def test_joint_product_rejects_duplicate_signature():
    ws, r, _s = make_workspace()

    with pytest.raises(ValueError, match="disjoint"):
        ws.product(r.all(), r.exactly(1))
