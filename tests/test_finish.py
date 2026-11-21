# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pytest

import mapelements

CRS = mapelements.CN_ALBERS


@pytest.fixture(autouse=True)
def _style():
    mapelements.pub_style()
    yield
    plt.close("all")


def test_finish_adds_three_artists():
    fig, ax = mapelements.figure("double", 100)
    mapelements.finish(ax, crs=CRS, extent=(94, 121, 26, 43))
    assert len(ax.artists) == 3
    x0, x1 = ax.get_xlim()
    assert x1 > x0


def test_finish_can_disable_elements():
    fig, ax = mapelements.figure("double", 100)
    mapelements.finish(ax, crs=CRS, extent=(94, 121, 26, 43),
                       graticule=None, scalebar=None, north=None)
    assert len(ax.artists) == 0


def test_finish_fills_single_axes():
    fig, ax = mapelements.figure("double", 100)
    mapelements.finish(ax, crs=CRS, extent=(94, 121, 26, 43))
    pos = ax.get_position()
    assert pos.x0 == pytest.approx(0, abs=1e-6)
    assert pos.y0 == pytest.approx(0, abs=1e-6)
    assert pos.x1 == pytest.approx(1, abs=1e-6)
    assert pos.y1 == pytest.approx(1, abs=1e-6)


def test_fit_skips_multipanel():
    fig, axs = plt.subplots(1, 2, figsize=(8, 3))
    before = fig.get_size_inches().copy()
    mapelements.fit(axs[0])
    assert (fig.get_size_inches() == before).all()
