try:
    from nest2D import Point
except ImportError as e:
    raise ImportError("Could not import Point from nest2D. Ensure that the nest2D library is correctly installed.") from e

def test_point():
    p = Point(-5000000, 8954050)
    print(p)
    assert repr(p) == 'Point(-5000000, 8954050)'
    assert Point.__doc__ == '2D Point'
    assert p.x == -5000000
    assert p.y == 8954050

