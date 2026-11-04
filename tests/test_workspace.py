import pytest
from graphillion import GraphSet

from searillion.relation import Carrier
from searillion.workspace import JointFamily, RelationWorkspace


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


def test_project_joint_product_recovers_factor_family():
    ws, r, s = make_workspace()

    rf = r.functions()
    sf = s.functions()
    projected = ws.product(rf, sf).project_to(r)

    assert projected.count() == rf.count()
    assert set(projected.relations()) == set(rf.relations())


def test_projection_is_existential_and_deduplicates_correlated_choices():
    ws, r, s = make_workspace()

    r1 = r._encode_pair((0, "x"))
    r2 = r._encode_pair((1, "y"))
    s1 = s._encode_pair(("x", True))
    s2 = s._encode_pair(("y", False))

    correlated = JointFamily(
        ws,
        (r, s),
        GraphSet([
            [r1, s1],
            [r2, s1],
            [r1, s2],
        ]),
    )

    projected = correlated.project_to(s)

    assert projected.count() == 2
    assert set(projected.relations()) == {
        frozenset({("x", True)}),
        frozenset({("y", False)}),
    }


def test_projection_rejects_signature_not_in_joint_family():
    ws, r, s = make_workspace()
    t = RelationWorkspace()
    x = t.relation("T", Carrier("X", [0]), Carrier("Y", [1]))
    # Compiling t would invalidate ws, so membership is checked first.
    with pytest.raises(ValueError, match="not part"):
        ws.product(r.all(), s.all()).project_to(x)


def make_composition_workspace():
    a = Carrier("A", ["a0", "a1"])
    b = Carrier("B", ["b0", "b1"])
    c = Carrier("C", ["c0", "c1"])

    ws = RelationWorkspace()
    r = ws.relation("R", a, b)
    s = ws.relation("S", b, c)
    t = ws.relation("T", a, c)
    ws.compile()
    return ws, r, s, t


def explicit_compose(r_relation, s_relation):
    return frozenset(
        (a, c)
        for a, b1 in r_relation
        for b2, c in s_relation
        if b1 == b2
    )


def test_compose_singleton_relations():
    ws, r, s, t = make_composition_workspace()

    r_value = frozenset({
        ("a0", "b0"),
        ("a1", "b1"),
    })
    s_value = frozenset({
        ("b0", "c1"),
        ("b1", "c0"),
    })

    result = ws.compose(
        r.explicit([r_value]),
        s.explicit([s_value]),
        t,
    )

    assert result.count() == 1
    assert set(result.relations()) == {
        frozenset({
            ("a0", "c1"),
            ("a1", "c0"),
        })
    }


def test_compose_relation_families_matches_extensional_oracle():
    ws, r, s, t = make_composition_workspace()

    r_values = {
        frozenset({("a0", "b0"), ("a1", "b1")}),
        frozenset({("a0", "b1")}),
    }
    s_values = {
        frozenset({("b0", "c1"), ("b1", "c0")}),
        frozenset({("b1", "c1")}),
    }

    expected = {
        explicit_compose(r_value, s_value)
        for r_value in r_values
        for s_value in s_values
    }

    result = ws.compose(
        r.explicit(r_values),
        s.explicit(s_values),
        t,
    )

    assert result.count() == len(expected)
    assert set(result.relations()) == expected


def test_compose_multiple_middle_witnesses_produce_one_target_atom():
    a = Carrier("A", ["a"])
    b = Carrier("B", ["b0", "b1"])
    c = Carrier("C", ["c"])

    ws = RelationWorkspace()
    r = ws.relation("R", a, b)
    s = ws.relation("S", b, c)
    t = ws.relation("T", a, c)
    ws.compile()

    result = ws.compose(
        r.explicit([[("a", "b0"), ("a", "b1")]]),
        s.explicit([[("b0", "c"), ("b1", "c")]]),
        t,
    )

    assert set(result.relations()) == {
        frozenset({("a", "c")})
    }


def test_compose_no_witness_produces_empty_relation():
    ws, r, s, t = make_composition_workspace()

    result = ws.compose(
        r.explicit([[("a0", "b0")]]),
        s.explicit([[("b1", "c0")]]),
        t,
    )

    assert set(result.relations()) == {frozenset()}


def test_compose_deduplicates_equal_results_from_different_source_pairs():
    ws, r, s, t = make_composition_workspace()

    r_values = [
        [("a0", "b0")],
        [("a0", "b1")],
    ]
    s_values = [
        [("b0", "c0")],
        [("b1", "c0")],
    ]

    result = ws.compose(r.explicit(r_values), s.explicit(s_values), t)

    # Two different matching source pairs produce the same singleton T.
    assert frozenset({("a0", "c0")}) in set(result.relations())
    assert result.count() <= len(r_values) * len(s_values)


def test_compose_requires_same_middle_ambient_carrier():
    a = Carrier("A", [0, 1])
    b1 = Carrier("B", [0, 1])
    b2 = Carrier("B", [0, 1])
    c = Carrier("C", [0, 1])

    ws = RelationWorkspace()
    r = ws.relation("R", a, b1)
    s = ws.relation("S", b2, c)
    t = ws.relation("T", a, c)
    ws.compile()

    with pytest.raises(ValueError, match="middle carriers"):
        ws.compose(r.all(), s.all(), t)


def test_compose_requires_target_with_exact_ambient_endpoints():
    a = Carrier("A", [0])
    a_copy = Carrier("A", [0])
    b = Carrier("B", [0])
    c = Carrier("C", [0])

    ws = RelationWorkspace()
    r = ws.relation("R", a, b)
    s = ws.relation("S", b, c)
    wrong_t = ws.relation("T", a_copy, c)
    ws.compile()

    with pytest.raises(ValueError, match="target signature"):
        ws.compose(r.all(), s.all(), wrong_t)


def test_explicit_atom_order_preserves_workspace_semantics():
    a = Carrier("A", [0, 1])
    b = Carrier("B", ["x", "y"])
    c = Carrier("C", [False, True])

    ws = RelationWorkspace()
    r = ws.relation("R", a, b)
    s = ws.relation("S", b, c)

    order = [
        (s, pair) for pair in reversed(s._pairs)
    ] + [
        (r, pair) for pair in reversed(r._pairs)
    ]
    ws.compile(atom_order=order)

    assert r.functions().count() == 4
    assert s.functions().count() == 4
    assert ws.product(r.functions(), s.functions()).count() == 16


def test_explicit_atom_order_rejects_missing_atoms():
    ws = RelationWorkspace()
    r = ws.relation("R", Carrier("A", [0, 1]), Carrier("B", [0, 1]))

    with pytest.raises(ValueError, match="every workspace atom"):
        ws.compile(atom_order=[(r, r._pairs[0])])


def test_explicit_atom_order_rejects_duplicate_atoms():
    ws = RelationWorkspace()
    r = ws.relation("R", Carrier("A", [0]), Carrier("B", [0]))

    with pytest.raises(ValueError, match="duplicate"):
        ws.compile(atom_order=[(r, r._pairs[0]), (r, r._pairs[0])])


def test_explicit_atom_order_rejects_foreign_signature():
    a = Carrier("A", [0])
    b = Carrier("B", [0])

    ws1 = RelationWorkspace()
    r1 = ws1.relation("R", a, b)

    ws2 = RelationWorkspace()
    r2 = ws2.relation("R2", a, b)

    with pytest.raises(ValueError, match="outside this workspace"):
        ws1.compile(atom_order=[(r2, r2._pairs[0])])


def test_graft_composition_matches_filter_composition_and_oracle():
    ws, r, s, t = make_composition_workspace()

    r_values = {
        frozenset({("a0", "b0"), ("a1", "b1")}),
        frozenset({("a0", "b1")}),
    }
    s_values = {
        frozenset({("b0", "c1"), ("b1", "c0")}),
        frozenset({("b1", "c1")}),
    }

    expected = {
        explicit_compose(r_value, s_value)
        for r_value in r_values
        for s_value in s_values
    }

    rf = r.explicit(r_values)
    sf = s.explicit(s_values)

    filtered = ws._composition_joint(rf, sf, t).project_to(t)
    grafted = ws._composition_joint_graft(rf, sf, t).project_to(t)

    assert set(filtered.relations()) == expected
    assert set(grafted.relations()) == expected
    assert set(grafted.relations()) == set(filtered.relations())


def test_graft_composition_handles_multiple_witnesses_and_no_witnesses():
    a = Carrier("A", ["a"])
    b = Carrier("B", ["b0", "b1"])
    c = Carrier("C", ["c0", "c1"])

    ws = RelationWorkspace()
    r = ws.relation("R", a, b)
    s = ws.relation("S", b, c)
    t = ws.relation("T", a, c)
    ws.compile()

    rf = r.explicit([
        [("a", "b0"), ("a", "b1")],
    ])
    sf = s.explicit([
        [("b0", "c0"), ("b1", "c0")],
    ])

    result = ws._composition_joint_graft(rf, sf, t).project_to(t)

    assert set(result.relations()) == {
        frozenset({("a", "c0")})
    }


def test_row_elimination_preserves_shared_s_and_cross_row_r_correlations():
    ws, r, s, t = make_composition_workspace()

    # R's rows are correlated: they must choose the same middle element.
    # S is shared by both target rows, so treating rows independently would
    # create impossible S/T pairs even if the final target count happened
    # to match.
    r_values = {
        frozenset({("a0", "b0"), ("a1", "b0")}),
        frozenset({("a0", "b1"), ("a1", "b1")}),
    }
    s_values = {
        frozenset({("b0", "c0"), ("b1", "c1")}),
        frozenset({("b0", "c1"), ("b1", "c0")}),
    }
    expected = {
        (s_value, explicit_compose(r_value, s_value))
        for r_value in r_values
        for s_value in s_values
    }

    joint = ws._composition_joint_graft_rows(
        r.explicit(r_values), s.explicit(s_values), t
    )
    actual = {
        (assignment["S"], assignment["T"])
        for assignment in joint.assignments()
    }

    assert joint.signatures == (s, t)
    assert actual == expected
    assert set(joint.project_to(t).relations()) == {t_value for _, t_value in expected}


def test_row_elimination_matches_filter_on_rectangular_families():
    a = Carrier("A", [0, 1])
    b = Carrier("B", [0, 1, 2])
    c = Carrier("C", [0, 1])
    ws = RelationWorkspace()
    r = ws.relation("R", a, b)
    s = ws.relation("S", b, c)
    t = ws.relation("T", a, c)
    ws.compile()

    r_values = [[], [(0, 0), (1, 1)], [(0, 1), (0, 2), (1, 0)]]
    s_values = [[], [(0, 1), (1, 1)], [(1, 0), (2, 1)]]
    expected = {
        explicit_compose(frozenset(rv), frozenset(sv))
        for rv in r_values
        for sv in s_values
    }
    rf, sf = r.explicit(r_values), s.explicit(s_values)

    row_result = ws._composition_joint_graft_rows(rf, sf, t).project_to(t)
    filter_result = ws._composition_joint(rf, sf, t).project_to(t)
    assert set(row_result.relations()) == expected
    assert set(filter_result.relations()) == expected


def test_row_elimination_empty_source_family_yields_empty_target_family():
    ws, r, s, t = make_composition_workspace()
    result = ws._composition_joint_graft_rows(r.empty_family(), s.all(), t)
    assert result.project_to(t).count() == 0


def test_row_elimination_total_functions_equal_independent_target_constructor():
    carrier_a = Carrier("A", range(3))
    carrier_b = Carrier("B", range(3))
    carrier_c = Carrier("C", range(3))
    ws = RelationWorkspace()
    r = ws.relation("R", carrier_a, carrier_b)
    s = ws.relation("S", carrier_b, carrier_c)
    t = ws.relation("T", carrier_a, carrier_c)
    ws.compile()

    result = ws._composition_joint_graft_rows(r.functions(), s.functions(), t)
    assert result.project_to(t)._graphset == t.functions()._graphset


def test_public_compose_selects_row_elimination_not_legacy_graft(monkeypatch):
    ws, r, s, t = make_composition_workspace()

    def legacy_called(*_args, **_kwargs):
        raise AssertionError("legacy delayed-elimination composer was selected")

    monkeypatch.setattr(ws, "_composition_joint_graft", legacy_called)
    assert ws.compose(r.functions(), s.functions(), t)._graphset == t.functions()._graphset


@pytest.mark.parametrize("n", [2, 3])
def test_compose_bijection_families_equals_independent_bijections(n):
    a, b, c = (Carrier(name, range(n)) for name in ("A", "B", "C"))
    ws = RelationWorkspace()
    r, s, t = (ws.relation(name, left, right) for name, left, right in (
        ("R", a, b), ("S", b, c), ("T", a, c)
    ))
    ws.compile()

    assert ws.compose(r.bijections(), s.bijections(), t)._graphset == t.bijections()._graphset


@pytest.mark.parametrize("n", [2, 3])
def test_compose_single_edge_relations_is_empty_or_single_edge(n):
    a, b, c = (Carrier(name, range(n)) for name in ("A", "B", "C"))
    ws = RelationWorkspace()
    r, s, t = (ws.relation(name, left, right) for name, left, right in (
        ("R", a, b), ("S", b, c), ("T", a, c)
    ))
    ws.compile()

    expected = t.exactly(1) | t.explicit([[]])
    assert ws.compose(r.exactly(1), s.exactly(1), t)._graphset == expected._graphset


def test_compose_unrestricted_small_families_is_unrestricted():
    ws, r, s, t = make_composition_workspace()
    assert ws.compose(r.all(), s.all(), t)._graphset == t.all()._graphset
