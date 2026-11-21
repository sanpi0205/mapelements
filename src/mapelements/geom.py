# -*- coding: utf-8 -*-
"""Projection and geodesy helpers. No drawing code lives here."""
from __future__ import annotations

import math

import numpy as np
from pyproj import Geod, Transformer

GEOD = Geod(ellps="WGS84")

# 中国常用 Albers：标准纬线 25°N / 47°N，中央经线 105°E
CN_ALBERS = ("+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 "
             "+lon_0=105 +datum=WGS84 +units=m +no_defs")

# 指北针位置别名 -> axes fraction
NORTH_LOCS = {
    "upper right": (0.93, 0.86),
    "upper left": (0.07, 0.86),
    "lower right": (0.93, 0.10),
    "lower left": (0.07, 0.10),
}


def as_pyproj(crs):
    """Accept a PROJ string, a pyproj CRS or a cartopy CRS."""
    return crs.proj4_init if hasattr(crs, "proj4_init") else crs


def transformers(crs):
    crs = as_pyproj(crs)
    fwd = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    inv = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    return fwd, inv


def axes_size_inch(ax):
    fig = ax.figure
    pos = ax.get_position()
    return (fig.get_size_inches()[0] * pos.width,
            fig.get_size_inches()[1] * pos.height)


def frac_per_pt(ax):
    """Axes fraction occupied by one point (x and y separately)."""
    w, h = axes_size_inch(ax)
    return 1.0 / (w * 72.0), 1.0 / (h * 72.0)


def data_per_pt(ax):
    """Data units per point; requires ``set_aspect('equal')``."""
    x0, x1 = ax.get_xlim()
    w, _ = axes_size_inch(ax)
    return (x1 - x0) / (w * 72.0)


def nice_length(km):
    """Round up to the next 1/2/5 x 10^n value (473 -> 500)."""
    if km <= 0:
        return 1.0
    exp = math.floor(math.log10(km))
    base = km / 10 ** exp
    for cand in (1, 2, 5, 10):
        if base <= cand + 1e-9:
            v = cand * 10 ** exp
            return int(v) if v >= 1 else round(v, 6)
    return km


def map_width_km(ax, crs):
    """Geodesic width of the current axis at its central latitude, in km."""
    _, inv = transformers(crs)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    lon_a, lat_a = inv.transform(x0, (y0 + y1) / 2)
    lon_b, lat_b = inv.transform(x1, (y0 + y1) / 2)
    _, _, d = GEOD.inv(lon_a, lat_a, lon_b, lat_b)
    return d / 1000.0


def project_extent(crs, extent, n=12):
    """Geographic extent -> projected bounds, sampled on an n x n grid."""
    fwd, _ = transformers(crs)
    lon0, lon1, lat0, lat1 = extent
    lo, la = np.meshgrid(np.linspace(lon0, lon1, n), np.linspace(lat0, lat1, n))
    x, y = fwd.transform(lo.ravel(), la.ravel())
    return float(np.min(x)), float(np.max(x)), float(np.min(y)), float(np.max(y))


def extent_from_axes(ax, crs):
    """Approximate geographic extent of the current projected limits."""
    _, inv = transformers(crs)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    lons, lats = [], []
    for x in (x0, x1):
        for y in (y0, y1):
            lon, lat = inv.transform(x, y)
            lons.append(lon)
            lats.append(lat)
    return (min(lons), max(lons), min(lats), max(lats))
