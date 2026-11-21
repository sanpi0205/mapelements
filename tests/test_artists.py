# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pytest

import mapelements
from mapelements import Graticule, NorthArrow, ScaleBar

CRS = mapelements.CN_ALBERS


@pytest.fixture(autouse=True)
def _style():
    mapelements.pub_style()
    yield
    plt.close("all")


def _fig():
    return mapelements.figure("double", 100)


def test_artists_are_vector_in_pdf(outdir):
    fig, ax = _fig()
    ax.set_xlim(-1.2e6, 1.2e6)
    ax.set_ylim(2.6e6, 4.9e6)
    ax.set_aspect("equal")
    ax.add_artist(Graticule(crs=CRS, extent=(94, 121, 26, 43), step=5))
    ax.add_artist(ScaleBar(length=500, crs=CRS))
    ax.add_artist(NorthArrow(crs=CRS))

    out = outdir / "fig.pdf"
    fig.savefig(out, format="pdf")
    raw = out.read_bytes()

    assert b"/Subtype /Image" not in raw
    assert b"/Subtype /Type3" not in raw
    # 内容流是压缩的，文字指令要解压后才能看到：交给 check_vector
    assert mapelements.check_vector(out) is True


def test_artists_are_text_in_svg(outdir):
    fig, ax = _fig()
    ax.set_xlim(-1.2e6, 1.2e6)
    ax.set_ylim(2.6e6, 4.9e6)
    ax.add_artist(ScaleBar(length=500, crs=CRS))
    ax.add_artist(NorthArrow(crs=CRS))

    out = outdir / "fig.svg"
    fig.savefig(out, format="svg")
    svg = out.read_text(encoding="utf-8")

    assert "<text" in svg
    assert "<image" not in svg


def test_copy_can_be_added_to_several_axes():
    fig, axs = plt.subplots(1, 2, figsize=(8, 3))
    sb = ScaleBar(length=500, crs=CRS)
    nw = NorthArrow(crs=CRS)
    for ax in axs:
        ax.set_xlim(-1.2e6, 1.2e6)
        ax.set_ylim(2.6e6, 4.9e6)
        ax.set_aspect("equal")
        ax.add_artist(sb.copy())
        ax.add_artist(nw.copy())

    fig.canvas.draw()

    assert len(axs[0].artists) == 2
    assert len(axs[1].artists) == 2
    assert axs[0].artists[0].resolved_length == 500
    assert axs[1].artists[0].resolved_length == 500
    assert sb.axes is None  # 原对象没有被绑定到某个 Axes


def test_auto_length_is_rounded():
    fig, ax = _fig()
    ax.set_xlim(-1.2e6, 1.2e6)
    ax.set_ylim(2.6e6, 4.9e6)
    ax.set_aspect("equal")
    sb = ScaleBar(length="auto", crs=CRS)
    ax.add_artist(sb)
    fig.canvas.draw()

    assert sb.resolved_length in {50, 100, 200, 500, 1000, 2000}


def test_missing_crs_raises():
    fig, ax = _fig()
    sb = ScaleBar(length=500)
    ax.add_artist(sb)
    with pytest.raises(ValueError):
        fig.canvas.draw()


def test_window_extent_under_constrained_layout():
    """Regression: get_window_extent must work before children have a figure."""
    import io

    fig, axs = plt.subplots(1, 2, figsize=(7, 3), constrained_layout=True)
    ax = axs[0]
    ax.set_xlim(-1.2e6, 1.2e6)
    ax.set_ylim(2.6e6, 4.9e6)
    ax.set_aspect("equal")
    sb = ScaleBar(length=500, crs=CRS)
    ax.add_artist(sb)

    buf = io.BytesIO()
    fig.savefig(buf, format="png")          # exercises the tight-bbox path

    extent = sb.get_window_extent(fig.canvas.get_renderer())
    assert extent.width > 0
    assert extent.height > 0
