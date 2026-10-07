from searillion.measurement import measure


def test_measurement_records_result():
    m = measure("answer", lambda: 42, seed=0)
    assert m.result == 42
    assert m.metadata["seed"] == 0
    assert m.wall_seconds >= 0
    assert m.cpu_seconds >= 0
