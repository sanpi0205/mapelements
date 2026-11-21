# -*- coding: utf-8 -*-
"""Vector map elements implemented as matplotlib Artist subclasses.

Use them like any other artist::

    from mapelements import ScaleBar, NorthArrow, Graticule

    ax.add_artist(ScaleBar(length=500, crs=CRS))
    ax.add_artist(NorthArrow(crs=CRS, loc="upper right"))
    ax.add_artist(Graticule(crs=CRS, extent=(94, 121, 26, 43), step=5))

Or build one object and copy it onto several panels::

    sb = ScaleBar(length=500, crs=CRS)
    ax1.add_artist(sb.copy())
    ax2.add_artist(sb.copy())

Every child artist is a Patch, LineCollection or Text. Geometry is rebuilt at
draw time from the current axis limits and figure size, so the elements stay
correct after zooming, resizing or re-layout, and they remain vector in PDF/SVG.
"""
from __future__ import annotations

import math

import numpy as np
from matplotlib.artist import Artist
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyArrow, Rectangle
from matplotlib.text import Text
from matplotlib.transforms import Bbox

from .geom import (
    GEOD,
    NORTH_LOCS,
    as_pyproj,
    data_per_pt,
    frac_per_pt,
    map_width_km,
    nice_length,
    transformers,
)


# ------------------------------------------------------------------ 基类
class _VectorArtist(Artist):
    """Base class for composite vector artists.

    ``draw()`` rebuilds the child primitives and renders them one by one. No
    offsetbox and no rasterisation is involved.
    """

    def __init__(self, zorder=30):
        super().__init__()
        self.set_zorder(zorder)
        self.set_clip_on(False)
        self._kids = []

    # 子类实现：向 self._kids 追加 Patch / LineCollection / Text
    def _build(self, renderer):  # pragma: no cover - 抽象
        raise NotImplementedError

    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible():
            return
        self._kids = []
        self._build(renderer)
        for kid in self._kids:
            kid.set_figure(self.figure)
            kid.draw(renderer)

    def get_window_extent(self, renderer=None):
        if self.figure is None:
            return Bbox.null()
        if renderer is None:
            try:
                renderer = self.figure.canvas.get_renderer()
            except Exception:
                return Bbox.null()
        self._kids = []
        self._build(renderer)
        if not self._kids:
            return Bbox.null()
        for kid in self._kids:
            kid.set_figure(self.figure)
        return Bbox.union([k.get_window_extent(renderer) for k in self._kids])

    def copy(self):
        """Return a copy that can be added to another Axes."""
        return type(self)(**dict(self._params))


def _prop(name):
    """Build a read/write property backed by ``self._params``."""
    def getter(self):
        return self._params[name]

    def setter(self, value):
        self._params[name] = value

    return property(getter, setter)


# ------------------------------------------------------------------ 比例尺
class ScaleBar(_VectorArtist):
    """Segmented scale bar with alternating black and white blocks.

    Parameters
    ----------
    length : float or "auto"
        Bar length in kilometres; ``"auto"`` takes 18 % of the map width and snaps
        it to a 1/2/5 x 10^n value.
    crs : CRS-like, optional
        Projection of the axes; falls back to ``ax.projection`` (cartopy).
    loc : (float, float)
        Lower-left corner of the bar in axes fraction.
    """

    length = _prop("length")
    loc = _prop("loc")
    divisions = _prop("divisions")
    height_frac = _prop("height_frac")
    colors = _prop("colors")
    fontsize = _prop("fontsize")
    unit_label = _prop("unit_label")
    show_mid = _prop("show_mid")
    crs = _prop("crs")

    def __init__(self, length="auto", crs=None, loc=(0.05, 0.06),
                 height_frac=0.010, divisions=4, colors=("black", "white"),
                 lw=0.5, fontsize=7, unit_label="km", show_mid=False,
                 ref_lon=None, ref_lat=None, zorder=30):
        super().__init__(zorder)
        self._params = dict(
            length=length, crs=crs, loc=loc, height_frac=height_frac,
            divisions=divisions, colors=tuple(colors), lw=lw,
            fontsize=fontsize, unit_label=unit_label, show_mid=show_mid,
            ref_lon=ref_lon, ref_lat=ref_lat, zorder=zorder,
        )
        self.resolved_length = None

    def _build(self, renderer):
        ax = self.axes
        p = self._params
        crs = p["crs"] or getattr(ax, "projection", None)
        if crs is None:
            raise ValueError("ScaleBar needs crs= (a projected CRS)")
        crs = as_pyproj(crs)

        length = p["length"]
        if length == "auto":
            length = nice_length(0.18 * map_width_km(ax, crs))
        self.resolved_length = float(length)

        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        span_x, span_y = x1 - x0, y1 - y0
        fwd, inv = transformers(crs)

        loc = p["loc"]
        ref_lon, ref_lat = p["ref_lon"], p["ref_lat"]
        if ref_lon is None or ref_lat is None:
            ref_lon, ref_lat = inv.transform(x0 + loc[0] * span_x,
                                             y0 + loc[1] * span_y)

        # 参考纬度处正东 1 km 的测地线，投影后取水平分量
        lon2, lat2, _ = GEOD.fwd(ref_lon, ref_lat, 90.0, self.resolved_length * 1000.0)
        xa, _ = fwd.transform(ref_lon, ref_lat)
        xb, _ = fwd.transform(lon2, lat2)
        width_frac = abs(xb - xa) / span_x

        _, fy_pt = frac_per_pt(ax)
        seg = width_frac / p["divisions"]
        h = p["height_frac"]
        z = self.get_zorder()

        for i in range(p["divisions"]):
            self._kids.append(Rectangle(
                (loc[0] + i * seg, loc[1]), seg, h,
                transform=ax.transAxes,
                facecolor=p["colors"][i % 2], edgecolor="black",
                linewidth=p["lw"], zorder=z))
        self._kids.append(Rectangle(
            (loc[0], loc[1]), width_frac, h, transform=ax.transAxes,
            facecolor="none", edgecolor="black", linewidth=p["lw"], zorder=z + 1))

        from matplotlib.lines import Line2D
        for i in (0, p["divisions"]):
            xx = loc[0] + i * seg
            self._kids.append(Line2D(
                [xx, xx], [loc[1], loc[1] - 2.5 * fy_pt],
                transform=ax.transAxes, color="black", linewidth=p["lw"],
                zorder=z + 1, solid_capstyle="butt"))

        marks = [(0, "0"), (p["divisions"], f"{self.resolved_length:g}")]
        if p["show_mid"] and p["divisions"] % 2 == 0:
            marks.insert(1, (p["divisions"] // 2,
                             f"{self.resolved_length / 2:g}"))
        if p["unit_label"]:
            i, txt = marks[-1]
            marks[-1] = (i, f"{txt} {p['unit_label']}")
        for i, txt in marks:
            self._kids.append(Text(
                loc[0] + i * seg, loc[1] - 3.5 * fy_pt, txt,
                transform=ax.transAxes, ha="center" if i else "left",
                va="top", fontsize=p["fontsize"], zorder=z + 1))


# ------------------------------------------------------------------ 指北针
class NorthArrow(_VectorArtist):
    """True-north arrow.

    The direction comes from the projection's meridian convergence, so the arrow
    leans correctly near the edges of a conic map. ``loc`` accepts a position alias
    ("upper right", "lower left", ...) or an ``(fx, fy)`` tuple in axes fraction.
    """

    loc = _prop("loc")
    length_pts = _prop("length_pts")
    label = _prop("label")
    crs = _prop("crs")

    def __init__(self, crs=None, loc="upper right", length_pts=14, lw=0.6,
                 fontsize=8, label="N", weight="normal", lon=None, lat=None,
                 zorder=30):
        super().__init__(zorder)
        self._params = dict(
            crs=crs, loc=loc, length_pts=length_pts, lw=lw,
            fontsize=fontsize, label=label, weight=weight,
            lon=lon, lat=lat, zorder=zorder,
        )

    def _build(self, renderer):
        ax = self.axes
        p = self._params
        crs = p["crs"] or getattr(ax, "projection", None)
        if crs is None:
            raise ValueError("NorthArrow needs crs= (a projected CRS)")
        crs = as_pyproj(crs)

        loc = p["loc"]
        fx, fy = NORTH_LOCS[loc] if isinstance(loc, str) else loc

        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        fwd, inv = transformers(crs)

        ax_x = x0 + fx * (x1 - x0)
        ax_y = y0 + fy * (y1 - y0)
        lon, lat = p["lon"], p["lat"]
        if lon is None or lat is None:
            lon, lat = inv.transform(ax_x, ax_y)

        lon2, lat2, _ = GEOD.fwd(lon, lat, 0.0, 1000.0)
        xa, ya = fwd.transform(lon, lat)
        xb, yb = fwd.transform(lon2, lat2)
        theta = math.atan2(xb - xa, yb - ya)

        L = p["length_pts"] * data_per_pt(ax)
        dx, dy = L * math.sin(theta), L * math.cos(theta)
        z = self.get_zorder()

        self._kids.append(FancyArrow(
            ax_x, ax_y, dx, dy,
            width=0.09 * L, head_width=0.40 * L, head_length=0.36 * L,
            length_includes_head=True, facecolor="black", edgecolor="black",
            linewidth=p["lw"], transform=ax.transData, zorder=z))
        self._kids.append(Text(
            ax_x + dx * 1.22, ax_y + dy * 1.22, p["label"],
            transform=ax.transData, ha="center", va="center",
            fontsize=p["fontsize"], fontweight=p["weight"], zorder=z + 1))


# ------------------------------------------------------------------ 经纬网
class Graticule(_VectorArtist):
    """Latitude/longitude graticule drawn as a single LineCollection.

    ``extent = (lon0, lon1, lat0, lat1)`` selects which meridians and parallels are
    drawn; the lines are sampled in lon/lat and reprojected into the map CRS.
    """

    step = _prop("step")
    color = _prop("color")
    extent = _prop("extent")

    def __init__(self, crs=None, extent=None, step=5.0, color="0.55",
                 lw=0.35, ls=":", npts=120, zorder=1):
        super().__init__(zorder)
        self._params = dict(
            crs=crs, extent=extent, step=step, color=color, lw=lw, ls=ls,
            npts=npts, zorder=zorder,
        )

    def _build(self, renderer):
        ax = self.axes
        p = self._params
        crs = p["crs"] or getattr(ax, "projection", None)
        if crs is None:
            raise ValueError("Graticule needs crs= (a projected CRS)")
        if p["extent"] is None:
            raise ValueError("Graticule 需要 extent=(lon0, lon1, lat0, lat1)")
        fwd, _ = transformers(crs)

        lon_min, lon_max, lat_min, lat_max = p["extent"]
        step, npts = p["step"], p["npts"]
        segs = []
        for lon in np.arange(np.ceil(lon_min / step) * step,
                             lon_max + 1e-6, step):
            la = np.linspace(lat_min, lat_max, npts)
            x, y = fwd.transform(np.full_like(la, lon), la)
            segs.append(np.column_stack([x, y]))
        for lat in np.arange(np.ceil(lat_min / step) * step,
                             lat_max + 1e-6, step):
            lo = np.linspace(lon_min, lon_max, npts)
            x, y = fwd.transform(lo, np.full_like(lo, lat))
            segs.append(np.column_stack([x, y]))

        self._kids.append(LineCollection(
            segs, colors=p["color"], linewidths=p["lw"],
            linestyles=p["ls"], transform=ax.transData,
            zorder=self.get_zorder()))


# ------------------------------------------------------------------ 函数封装
def scale_bar(ax, **kwargs):
    """Create a scale bar, add it to ``ax`` and return the artist."""
    artist = ScaleBar(**kwargs)
    ax.add_artist(artist)
    return artist


def north_arrow(ax, **kwargs):
    """Create a north arrow, add it to ``ax`` and return the artist."""
    artist = NorthArrow(**kwargs)
    ax.add_artist(artist)
    return artist


def graticule(ax, **kwargs):
    """Create a graticule, add it to ``ax`` and return the artist."""
    artist = Graticule(**kwargs)
    ax.add_artist(artist)
    return artist
