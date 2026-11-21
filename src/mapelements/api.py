# -*- coding: utf-8 -*-
"""One-call helpers: finish() for the map furniture, fit() for the layout."""
from __future__ import annotations

from .artists import Graticule, NorthArrow, ScaleBar
from .geom import as_pyproj, extent_from_axes, project_extent


def fit(ax):
    """Make a single-panel map fill the canvas.

    Removes the subplot margins and adjusts the figure height to the data aspect
    ratio. It only acts when the figure contains exactly one Axes; multi-panel
    figures are left untouched. Call it after setting the limits and aspect, and
    before adding the map elements.
    """
    fig = ax.figure
    if len(fig.axes) != 1:
        return ax
    ax.set_position([0, 0, 1, 1])
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    w_in = fig.get_size_inches()[0]
    fig.set_size_inches(w_in, w_in * (y1 - y0) / (x1 - x0))
    return ax


def finish(ax, crs=None, data=None, extent=None,
           graticule=5.0, scalebar="auto", north="upper right",
           scalebar_loc=None, pad=0.02, legend=False, fill=True, zorder=30):
    """Add the map furniture in one call.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        A plain projected Axes or a cartopy GeoAxes.
    crs : CRS-like, optional
        Projection; defaults to ``ax.projection``.
    data : geopandas.GeoDataFrame, optional
        Used to derive the extent from ``total_bounds`` after ``to_crs(crs)``.
    extent : (lon0, lon1, lat0, lat1), optional
        Explicit geographic box; takes precedence over ``data``.
    graticule : float or None
        Spacing in degrees; ``None`` or ``False`` disables the graticule.
    scalebar : float, "auto" or None
        Bar length in km; ``"auto"`` rounds to a 1/2/5 x 10^n value.
    north : str, tuple or None
        Position alias ("upper right", ...), axes-fraction tuple, or disabled.
    scalebar_loc : tuple, optional
        Bar position; defaults to the corner opposite the north arrow.
    pad : float
        Fractional padding around the extent (default 2 %).
    legend : bool
        Place a borderless legend in the upper-left corner.
    fill : bool
        Call :func:`fit` for single-panel figures (ignored otherwise).

    Returns
    -------
    matplotlib.axes.Axes
        The same axes, for chaining.
    """
    if crs is None:
        crs = getattr(ax, "projection", None)
    if crs is None:
        raise ValueError("finish() needs crs=: pass the projected CRS explicitly for plain Axes")
    crs = as_pyproj(crs)

    # 1) 范围
    if extent is not None:
        x0, x1, y0, y1 = project_extent(crs, extent)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
    elif data is not None:
        b = data.to_crs(crs).total_bounds
        ax.set_xlim(b[0], b[2])
        ax.set_ylim(b[1], b[3])

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_xlim(x0 - pad * (x1 - x0), x1 + pad * (x1 - x0))
    ax.set_ylim(y0 - pad * (y1 - y0), y1 + pad * (y1 - y0))
    ax.set_aspect("equal")
    ax.set_axis_off()

    # 1.5) 单幅地图铺满画布（多子图时自动跳过）
    if fill:
        fit(ax)

    # 2) 经纬网范围
    if extent is None:
        extent = extent_from_axes(ax, crs)
    if graticule:
        ax.add_artist(Graticule(crs=crs, extent=extent, step=graticule))

    # 3) 比例尺（默认放在指北针的斜对角）
    if scalebar_loc is None:
        up = isinstance(north, str) and north.startswith("upper")
        scalebar_loc = (0.05, 0.06) if up else (0.05, 0.90)
    if scalebar:
        ax.add_artist(ScaleBar(length=scalebar, crs=crs,
                               loc=scalebar_loc, zorder=zorder))

    # 4) 指北针
    if north:
        ax.add_artist(NorthArrow(crs=crs, loc=north, zorder=zorder))

    # 5) 图例
    if legend:
        ax.legend(loc="upper left", bbox_to_anchor=(0.012, 0.988),
                  fontsize=6.5, frameon=False, borderaxespad=0.2,
                  handlelength=1.2, borderpad=0.3, labelspacing=0.35)

    return ax
