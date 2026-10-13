from searillion.relation import Carrier, RelationUniverse


def make_2x2():
    return RelationUniverse(
        Carrier("A", ["a0", "a1"]),
        Carrier("B", ["b0", "b1"]),
    )


def explicit_forget(family, pair):
    expected = set()
    for relation in family.relations():
        expected.add(frozenset(p for p in relation if p != pair))
    return expected


def test_forget_matches_explicit_projection():
    u = make_2x2()
    f = u.explicit(
        [
            [],
            [("a0", "b0")],
            [("a0", "b0"), ("a1", "b1")],
            [("a0", "b1")],
        ]
    )
    projected = f.forget(("a0", "b0"))
    assert set(projected.relations()) == explicit_forget(f, ("a0", "b0"))


def test_forget_collapses_duplicate_images():
    u = make_2x2()
    f = u.explicit([[], [("a0", "b0")]])
    projected = f.forget(("a0", "b0"))
    assert projected.count() == 1
    assert set(projected.relations()) == {frozenset()}


def test_forget_many_matches_explicit_projection():
    u = make_2x2()
    pairs = [("a0", "b0"), ("a1", "b1")]
    f = u.all()
    projected = f.forget_many(pairs)
    expected = {
        frozenset(p for p in relation if p not in pairs)
        for relation in f.relations()
    }
    assert set(projected.relations()) == expected
    assert projected.count() == 4


def test_forget_does_not_mutate_source_family():
    u = make_2x2()
    f = u.all()
    before = f.count()
    _ = f.forget(("a0", "b0"))
    assert f.count() == before
