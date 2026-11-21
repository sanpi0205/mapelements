# -*- coding: utf-8 -*-
"""Generate the figures used in the documentation.

Run from the repository root::

    python docs/make_figures.py

The output lands in ``docs/assets/``. All figures are rasterised previews; the
documentation embeds them, but the package itself only produces vector output.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer

import mapelements
from mapelements import Graticule, NorthArrow, ScaleBar

ASSETS = Path(__file__).parent / "assets"
CRS = mapelements.CN_ALBERS
FWD = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)

mapelements.pub_style({"font.sans-serif": ["DejaVu Sans", "Arial"]})


def save(fig, name, dpi=160):
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / name
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    print(f"[figure] {path} ({path.stat().st_size / 1024:.0f} KB)")


def outline(lons, lats):
    x, y = FWD.transform(lons, lats)
    return np.asarray(x, float), np.asarray(y, float)


def extent_xy(extent, n=40):
    lon0, lon1, lat0, lat1 = extent
    lo, la = np.meshgrid(np.linspace(lon0, lon1, n), np.linspace(lat0, lat1, n))
    x, y = FWD.transform(lo.ravel(), la.ravel())
    return np.min(x), np.max(x), np.min(y), np.max(y)


def blank_map(extent, width=160, height=95):
    fig, ax = mapelements.figure(width, height)
    x0, x1, y0, y1 = extent_xy(extent)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.set_axis_off()
    return fig, ax


# --------------------------------------------------------------- 1. scale bars
def figure_scalebars():
    fig, ax = blank_map((94, 121, 26, 43), width=125, height=105)
    ax.add_artist(Graticule(crs=CRS, extent=(94, 121, 26, 43), step=5,
                            color="0.85", lw=0.3))

    variants = [
        ((0.10, 0.78), dict(length=500, divisions=4),
         "divisions=4, colors=('black', 'white')"),
        ((0.10, 0.52), dict(length=300, divisions=3, lw=0.8, fontsize=8),
         "divisions=3, lw=0.8, fontsize=8"),
        ((0.10, 0.26), dict(length=400, divisions=4,
                            colors=("0.2", "white")),
         "colors=('0.2', 'white'), length=400"),
    ]
    for loc, kwargs, caption in variants:
        ax.add_artist(ScaleBar(crs=CRS, loc=loc, **kwargs))
        ax.text(loc[0], loc[1] + 0.075, caption, fontsize=6.5,
                color="0.35", va="bottom", transform=ax.transAxes)

    save(fig, "elements-scalebar.png")


# -------------------------------------------------------------- 2. north arrow
def figure_northarrows():
    extent = (75, 135, 25, 45)
    fig, ax = blank_map(extent, width=165, height=88)
    ax.add_artist(Graticule(crs=CRS, extent=extent, step=10,
                            color="0.8", lw=0.3))

    for fx in (0.12, 0.5, 0.88):
        ax.add_line(plt.Line2D([fx, fx], [0.05, 0.95],
                               transform=ax.transAxes,
                               color="0.6", lw=0.4, ls="--"))
        ax.add_artist(NorthArrow(crs=CRS, loc=(fx, 0.55), length_pts=20,
                                 fontsize=9))

    ax.text(0.5, 0.96, "arrows follow the meridian convergence",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=7.5, color="0.3")
    save(fig, "elements-northarrow.png")


# ---------------------------------------------------------------- 3. graticule
def figure_graticule():
    fig, ax = blank_map((94, 121, 26, 43))
    ax.add_artist(Graticule(crs=CRS, extent=(94, 121, 26, 43), step=5))
    x, y = outline([96, 104, 108, 102, 95, 96], [40, 42, 38, 35, 36, 40])
    ax.fill(x, y, facecolor="#cfe3f3", edgecolor="0.3", lw=0.5, zorder=3)
    save(fig, "elements-graticule.png")


# ------------------------------------------------------------- 4. two panels
def figure_panels():
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.4), constrained_layout=True)
    sb = ScaleBar(length=400, crs=CRS, loc=(0.06, 0.08))
    nw = NorthArrow(crs=CRS, loc="upper right", length_pts=12)

    for ax, extent, title in zip(
        axs,
        [(75, 105, 26, 45), (105, 135, 26, 45)],
        ["western sheet", "eastern sheet"],
    ):
        x0, x1, y0, y1 = extent_xy(extent)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.set_aspect("equal")
        ax.set_axis_off()
        ax.add_artist(Graticule(crs=CRS, extent=extent, step=5,
                                color="0.8", lw=0.3))
        ax.add_artist(sb.copy())
        ax.add_artist(nw.copy())
        ax.text(0.5, 0.96, title, transform=ax.transAxes, ha="center",
                fontsize=7.5)

    save(fig, "layout-panels.png")


# --------------------------------------------------------------- 5. cartopy
def figure_cartopy():
    import cartopy.crs as ccrs

    proj = ccrs.AlbersEqualArea(central_longitude=105,
                                standard_parallels=(25, 47))
    fig = plt.figure(figsize=(6.6, 4.2))
    ax = fig.add_subplot(111, projection=proj)
    ax.set_extent([94, 121, 26, 43], crs=ccrs.PlateCarree())
    ax.coastlines(resolution="110m", lw=0.4)
    ax.add_artist(Graticule(crs=ax.projection, extent=(94, 121, 26, 43), step=5,
                            color="0.75", lw=0.3))
    ax.add_artist(ScaleBar(length="auto", crs=ax.projection, loc=(0.05, 0.06)))
    ax.add_artist(NorthArrow(crs=ax.projection))
    save(fig, "cookbook-cartopy.png", dpi=150)


if __name__ == "__main__":
    figure_scalebars()
    figure_northarrows()
    figure_graticule()
    figure_panels()
    figure_cartopy()
