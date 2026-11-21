# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

import mapelements

CRS = mapelements.CN_ALBERS


def test_save_writes_pdf_svg_png(outdir):
    fig, ax = mapelements.figure("double", 100)
    mapelements.finish(ax, crs=CRS, extent=(94, 121, 26, 43))

    paths = mapelements.save(fig, "Fig1", outdir=outdir)

    assert set(paths) == {"pdf", "svg", "png"}
    for path in paths.values():
        assert path.exists() and path.stat().st_size > 0
    plt.close(fig)


def test_check_vector_accepts_generated_pdf(outdir):
    fig, ax = mapelements.figure("double", 100)
    ax.plot([0, 1], [0, 1])
    out = outdir / "ok.pdf"
    fig.savefig(out, format="pdf")
    plt.close(fig)

    assert mapelements.check_vector(out) is True
