# -*- coding: utf-8 -*-
"""
demo_map.py — 一站式用法：范围 + 经纬网 + 比例尺 + 指北针

运行：python examples/demo_map.py
产出：examples/out/Fig1.pdf / .svg / .png
"""
from pathlib import Path

import numpy as np
from matplotlib.patches import Patch
from pyproj import Transformer

import mapelements

OUT = Path(__file__).parent / "out"
CRS = mapelements.CN_ALBERS

mapelements.pub_style({"font.sans-serif": ["SimHei", "Microsoft YaHei",
                                           "Arial", "DejaVu Sans"]})
fwd = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)


def proj(lons, lats):
    x, y = fwd.transform(lons, lats)
    return np.asarray(x, float), np.asarray(y, float)


regions = [
    ([(96, 40), (104, 42), (108, 38), (102, 35), (95, 36)], "#cfe3f3", "研究区 A"),
    ([(108, 38), (116, 42), (120, 37), (114, 33), (107, 34)], "#f6d9c9", "研究区 B"),
    ([(102, 35), (108, 38), (114, 33), (110, 28), (103, 29)], "#dfeed6", "研究区 C"),
]
cities = [(105.0, 38.5, "银川"), (112.0, 36.0, "太原"), (108.5, 31.0, "重庆")]
extent = (94, 121, 26, 43)

fig, ax = mapelements.figure("double", 112)

for ring, color, _ in regions:
    x, y = proj([p[0] for p in ring], [p[1] for p in ring])
    ax.fill(x, y, facecolor=color, edgecolor="0.25", linewidth=0.5, zorder=3)

for lon, lat, name in cities:
    x, y = proj([lon], [lat])
    ax.plot(x, y, marker="o", ms=3, mfc="white", mec="black", mew=0.6, zorder=5)
    ax.text(x[0], y[0], " " + name, fontsize=6.5, va="bottom", zorder=6)

mapelements.finish(ax, crs=CRS, extent=extent, graticule=5,
                   scalebar=500, north="upper right")

handles = [Patch(facecolor=c, edgecolor="0.25", lw=0.5, label=n)
           for _, c, n in regions]
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.012, 0.988),
          fontsize=6.5, frameon=False, borderaxespad=0.2,
          handlelength=1.2, borderpad=0.3, labelspacing=0.35)

mapelements.save(fig, "Fig1", outdir=OUT)
