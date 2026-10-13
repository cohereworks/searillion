from math import factorial

from searillion.relation import Carrier, RelationUniverse


def universe(n_left: int, n_right: int):
    return RelationUniverse(
        Carrier("A", range(n_left)),
        Carrier("B", range(n_right)),
    )


def test_function_family_count():
    u = universe(3, 2)
    assert u.functions().count() == 2 ** 3


def test_function_family_members_are_total_single_valued():
    u = universe(2, 3)
    for relation in u.functions().relations():
        assert len(relation) == 2
        for a in u.left.elements:
            matches = [pair for pair in relation if pair[0] == a]
            assert len(matches) == 1


def test_bijection_family_count():
    u = universe(4, 4)
    assert u.bijections().count() == factorial(4)


def test_bijection_members_are_one_to_one_and_onto():
    u = universe(3, 3)
    for relation in u.bijections().relations():
        assert {a for a, _ in relation} == set(u.left.elements)
        assert {b for _, b in relation} == set(u.right.elements)
        assert len(relation) == 3


def test_bijections_empty_for_unequal_carriers():
    assert universe(2, 3).bijections().count() == 0
