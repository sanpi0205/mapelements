# Quickstart

A complete map figure in about twenty lines, from a projected study area to a
journal-ready PDF.

## 1. Set the journal style

```python
import mapelements

mapelements.pub_style()
```

`pub_style()` sets the settings that make the difference between "a plot" and
"artwork an editor can edit":

```python
{
    "pdf.fonttype": 42,      # TrueType, text stays text (3 = Type 3 outlines)
    "ps.fonttype": 42,
    "svg.fonttype": "none",  # <text>, not <path>
    "font.size": 8,
    ...
}
```

You can override anything:

```python
mapelements.pub_style({"font.sans-serif": ["Arial", "DejaVu Sans"]})
```

## 2. Create a figure in millimetres

```python
fig, ax = mapelements.figure("double", 110)   # 170 mm × 110 mm
```

`"single"` is 85 mm, `"double"` is 170 mm — the usual column widths. Pass a
number of millimetres if your journal differs.

## 3. Plot your data in a projected CRS

```python
import geopandas as gpd
from pyproj import Transformer

CRS = mapelements.CN_ALBERS           # Albers, 25°N/47°N, central meridian 105°E
fwd = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)

gdf.to_crs(CRS).plot(ax=ax, column="value", cmap="YlGnBu",
                     edgecolor="0.3", linewidth=0.4)
```

Never draw a mid-latitude region in an unprojected (Plate Carrée) CRS: shapes
are stretched east–west and a scale bar would be meaningless.

## 4. Add the map furniture in one call

```python
mapelements.finish(ax, crs=CRS, data=gdf)
```

This sets the extent from the data, pads it by 2 %, draws a 5° graticule, a
rounded scale bar (18 % of the map width, snapped to 1/2/5 × 10ⁿ), and a north
arrow in the upper right. It also removes the axis frame and makes the map fill
the canvas.

Prefer explicit extents? Pass lon/lat bounds instead of `data`:

```python
mapelements.finish(ax, crs=CRS, extent=(94, 121, 26, 43))
```

## 5. Export and verify

```python
mapelements.save(fig, "Fig1")
```

```
[saved] figs/Fig1.pdf (17.9 KB)
[saved] figs/Fig1.svg (36.5 KB)
[saved] figs/Fig1.png (420.7 KB)

=== Fig1.pdf ===
font subtypes: {'CIDFontType2': 1, 'Type0': 1}
text operators Tj/TJ: 10
image XObjects: 0
result: PASS
```

`save()` raises `NotVectorError` if the PDF contains Type 3 fonts or image
objects, so a bad export cannot slip through unnoticed.

## Complete script

```python
import matplotlib
matplotlib.use("Agg")
import geopandas as gpd
import mapelements

CRS = mapelements.CN_ALBERS
mapelements.pub_style()

fig, ax = mapelements.figure("double", 110)
gdf.to_crs(CRS).plot(ax=ax, column="value", cmap="YlGnBu",
                     edgecolor="0.3", linewidth=0.4)

mapelements.finish(ax, crs=CRS, data=gdf, scalebar=500, north="upper right")
mapelements.save(fig, "Fig1")
```

## Next

- [Map elements](elements.md) — every option of the three artists.
- [Projections](projections.md) — Albers, UTM, cartopy.
- [Exporting for a journal](export.md) — the checklist before you submit.
