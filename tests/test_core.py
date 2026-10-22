import pytest
from core import parse_coordinate, parse_point, bearing_text, calculate, make_svg, Point

def test_compact_and_dms():
    assert parse_coordinate('N423101', True) == pytest.approx(42 + 31/60 + 1/3600)
    assert parse_coordinate('E0721448', False) == pytest.approx(72 + 14/60 + 48/3600)
    assert parse_coordinate('S423101', True) < 0
    assert parse_coordinate('42° 31 01', True) == pytest.approx(parse_coordinate('N423101', True))

@pytest.mark.parametrize('coordinate,latitude', [('N429999', True), ('N916000', True), ('E1810000', False), ('N423160', True), ('E0721460', False)])
def test_invalid_ranges(coordinate, latitude):
    with pytest.raises(ValueError):
        parse_coordinate(coordinate, latitude)

def test_bearing_wrap():
    assert bearing_text(359.8, False) == 'A000'
    assert bearing_text(359.999, True) == 'A000.00'
    assert bearing_text(5.27, True) == 'A005.27'

def test_true_bearing_and_insert():
    result = calculate('N423101 E0721448', '(Т.1) N423101 E0721448', magnetic=False)
    assert 'S0,0км A000' in result.text
    assert len(result.points) == 1

def test_invalid_line_warning():
    result = calculate('N423101 E0721448', 'N429999 E0721448\nN423101 E0721448', magnetic=False, clean_list=True)
    assert len(result.warnings) == 1
    assert len(result.points) == 1

def test_svg_escapes_labels():
    assert '&lt;script&gt;' in make_svg((42,72), [Point(42,72,'<script>')])


def test_svg_boundary_focus_excludes_distant_airport():
    pts = [Point(42.5, 72.2, "T1"), Point(42.6, 72.4, "T2"), Point(42.4, 72.5, "T3")]
    far_airport = (40.0, 70.8)
    all_objects = make_svg(far_airport, pts)
    boundary_only = make_svg(far_airport, pts, focus_boundary=True)
    assert "КТА" in all_objects
    assert "КТА" not in boundary_only
    assert 'T1' in boundary_only and 'T3' in boundary_only
    assert all_objects != boundary_only


def test_svg_boundary_focus_keeps_airport_if_inside():
    pts = [Point(42.5, 72.2, "T1"), Point(42.6, 72.4, "T2"), Point(42.4, 72.5, "T3")]
    assert "КТА" in make_svg((42.5, 72.35), pts, focus_boundary=True)
