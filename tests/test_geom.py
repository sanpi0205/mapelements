# -*- coding: utf-8 -*-
import pytest

from mapelements.geom import CN_ALBERS, nice_length, project_extent, transformers


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(473, 500), (120, 200), (0.4, 0.5), (1, 1), (9000, 10000), (2.2, 5)],
)
def test_nice_length(raw, expected):
    assert nice_length(raw) == expected


def test_project_extent_is_symmetric_about_central_meridian():
    x0, x1, y0, y1 = project_extent(CN_ALBERS, (95, 115, 30, 40))
    assert x0 == pytest.approx(-x1, rel=1e-6)
    assert y0 < y1


def test_transformers_roundtrip():
    fwd, inv = transformers(CN_ALBERS)
    x, y = fwd.transform(105.0, 35.0)
    lon, lat = inv.transform(x, y)
    assert (lon, lat) == pytest.approx((105.0, 35.0), abs=1e-9)
