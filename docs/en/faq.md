# FAQ

## The scale bar is too long / too short

Almost always a CRS mismatch. The bar length is computed from a geodesic at its
own latitude, using the `crs` you pass. If `crs` is wrong (for example degrees
passed to an axes that is actually in metres), the width is off by orders of
magnitude.

```python
# axes plotted with gdf.to_crs(CRS) -> pass the same CRS
ax.add_artist(ScaleBar(length=500, crs=CRS))
```

On a cartopy `GeoAxes` you can omit `crs`; `ax.projection` is used.

## `ValueError: ScaleBar needs crs= (a projected CRS)`

You put the artist on a plain `Axes` and did not pass `crs`. Either pass it, or
use `finish(ax, crs=...)`, which forwards it.

## Nothing appears on the figure

Three usual causes:

1. the artist was never added — `ax.add_artist(...)`, not just
   `ScaleBar(...)`;
2. `loc` is outside `0..1` (positions are axes fractions);
3. the axes limits were changed after the artist was added **and** the figure
   was never redrawn. Any `savefig`, `draw()` or notebook render rebuilds the
   geometry, so this only bites when you inspect `ax.patches` before drawing.

## `NotVectorError` from `save()`

The check found Type 3 fonts or image objects. Two cases:

- **Your own figure contains a raster layer** (hillshade, satellite image,
  rasterised `contourf`). That is legitimate: pass `allow_images=True`.
- **Text was outlined.** Make sure `pub_style()` ran before `savefig`, or set
  `matplotlib.rcParams["pdf.fonttype"] = 42` yourself.

## The PDF text cannot be edited in Illustrator

Check the font type first:

```bash
pdffonts figs/Fig1.pdf
```

`Type 3` means the glyphs are curves — the figure was saved with the default
matplotlib setting. Re-export after `pub_style()`.

## Chinese characters show as boxes

matplotlib picked a font without CJK coverage. Set one that exists on your
machine:

```python
mapelements.pub_style({"font.sans-serif": ["Microsoft YaHei", "SimHei",
                                           "DejaVu Sans"]})
```

## `findfont: Failed to find font weight bold`

The selected CJK family has no bold face. `NorthArrow(weight="normal")` (the
default) avoids it; or install a family that ships bold.

## The north arrow looks tilted

That is correct. On a conic projection the meridians converge, so true north
leans away from vertical near the map edges. The arrow computes the real
direction; a perfectly vertical arrow would be wrong there.

## `fit()` did nothing

`fit()` only acts when the figure has exactly one axes. For multi-panel layouts
keep your own geometry and call `finish(..., fill=False)`.

## The scale bar disagrees with a bar from another tool

Different tools assume different things. `mapelements` measures a geodesic step
due east at the bar's latitude and projects it, which is exact for a horizontal
bar on a projected map. If another tool assumed a fixed "metres per pixel", the
two will differ by the projection's scale factor — a few tenths of a percent
inside a UTM zone, more on a wide conic map.

## Does it work with cartopy's `transform=`?

Yes. Plot your data with `transform=ccrs.PlateCarree()` as usual; the three
artists do their own pyproj maths and do not interfere with cartopy.

## Can I use it in Jupyter?

Yes. With the inline backend the artists draw on every render. `save()` works
there too.

## Difference from `matplotlib_scalebar` and `matplotlib_map_utils`

| | `matplotlib_scalebar` | `matplotlib_map_utils` | `mapelements` |
|---|---|---|---|
| Vector output | yes | **no** — the whole bar becomes an `OffsetImage` | yes |
| Editable text | yes | no | yes |
| Alternating blocks | no | yes | yes |
| North arrow | no | yes | yes |
| Graticule | no | no | yes |
| Extra dependency | yes | yes (+ temporary figure rendering) | matplotlib + pyproj only |

## How do I report a bug?

Open an issue at <https://github.com/sanpi0205/mapelements/issues> with a minimal
reproduction: the CRS string, the axis limits, and the code that adds the
artist.
