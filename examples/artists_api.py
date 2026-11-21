# -*- coding: utf-8 -*-
"""
artists_api.py — Artist 方式：add_artist / copy / cartopy

运行：python examples/artists_api.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import mapelements
from mapelements import Graticule, NorthArrow, ScaleBar

OUT = Path(__file__).parent / "out"
CRS = mapelements.CN_ALBERS
mapelements.pub_style({"font.sans-serif": ["SimHei", "Arial"]})


# ---- 1) 普通 Axes：三个 artist 直接加 -------------------------------------
fig, ax = mapelements.figure("double", 100)
ax.set_xlim(-1.2e6, 1.2e6)
ax.set_ylim(2.6e6, 4.9e6)
ax.set_aspect("equal")
ax.set_axis_off()
ax.add_artist(Graticule(crs=CRS, extent=(94, 121, 26, 43), step=5))
ax.add_artist(ScaleBar(length=500, crs=CRS))
ax.add_artist(NorthArrow(crs=CRS))
mapelements.save(fig, "artist_api", outdir=OUT)


# ---- 2) 一个对象复制到多个子图 -------------------------------------------
fig2, axs = plt.subplots(1, 2, figsize=(8, 3.8))
sb = ScaleBar(length=500, crs=CRS, loc=(0.06, 0.08))
nw = NorthArrow(crs=CRS)
for i, a in enumerate(axs):
    a.set_xlim(-1.2e6, 1.2e6)
    a.set_ylim(2.6e6, 4.9e6)
    a.set_aspect("equal")
    a.set_axis_off()
    a.text(0, 4.6e6, f"panel {i + 1}", fontsize=8, ha="center")
    a.add_artist(sb.copy())
    a.add_artist(nw.copy())
mapelements.save(fig2, "artist_copy", outdir=OUT, formats=("pdf",))


# ---- 3) cartopy GeoAxes ---------------------------------------------------
import cartopy.crs as ccrs

proj = ccrs.AlbersEqualArea(central_longitude=105, standard_parallels=(25, 47))
fig3 = plt.figure(figsize=(6.7, 4.4))
ax3 = fig3.add_subplot(111, projection=proj)
ax3.set_extent([94, 121, 26, 43], crs=ccrs.PlateCarree())
ax3.coastlines(resolution="110m", lw=0.4)
ax3.add_artist(ScaleBar(length="auto", crs=ax3.projection, loc=(0.05, 0.07)))
ax3.add_artist(NorthArrow(crs=ax3.projection))
mapelements.save(fig3, "cartopy_map", outdir=OUT, formats=("pdf",))
