# API reference

```python
import mapelements
```

## Artists

### `ScaleBar`

```python
ScaleBar(
    length="auto", crs=None, loc=(0.05, 0.06),
    height_frac=0.010, divisions=4, colors=("black", "white"),
    lw=0.5, fontsize=7, unit_label="km", show_mid=False,
    ref_lon=None, ref_lat=None, zorder=30,
)
```

| Parameter | Type | Description |
|---|---|---|
| `length` | `float \| "auto"` | bar length in km; `"auto"` = 18 % of the map width snapped to 1/2/5 × 10ⁿ |
| `crs` | PROJ string, EPSG, `pyproj.CRS`, cartopy CRS | projection of the axes; defaults to `ax.projection` |
| `loc` | `(fx, fy)` | lower-left corner in axes fraction |
| `height_frac` | `float` | bar height as a fraction of the axes height |
| `divisions` | `int` | number of blocks |
| `colors` | sequence | cycled over the blocks, e.g. `("black", "white")` |
| `lw` | `float` | outline width in points |
| `fontsize` | `float` | label size in points |
| `unit_label` | `str` | appended to the last label; `""` to omit |
| `show_mid` | `bool` | also label the midpoint (even `divisions` only) |
| `ref_lon`, `ref_lat` | `float \| None` | latitude at which the geodesic is evaluated; defaults to the bar position |
| `zorder` | `float` | drawing order |

Attributes: `.length`, `.loc`, `.divisions`, `.height_frac`, `.colors`,
`.fontsize`, `.unit_label`, `.show_mid`, `.crs` are read/write properties.
`.resolved_length` holds the numeric length after the first draw (`None` before).

### `NorthArrow`

```python
NorthArrow(
    crs=None, loc="upper right", length_pts=14, lw=0.6,
    fontsize=8, label="N", weight="normal", lon=None, lat=None, zorder=30,
)
```

| Parameter | Type | Description |
|---|---|---|
| `crs` | CRS | defaults to `ax.projection` |
| `loc` | `str \| (fx, fy)` | `"upper right"`, `"upper left"`, `"lower right"`, `"lower left"` |
| `length_pts` | `float` | arrow length in points |
| `lw` | `float` | outline width |
| `fontsize` | `float` | label size |
| `label` | `str` | usually `"N"` |
| `weight` | `str` | `"normal"` or `"bold"` |
| `lon`, `lat` | `float \| None` | point where true north is evaluated |

The arrow direction is the projection's meridian convergence, computed from a
1 km geodesic step due north.

### `Graticule`

```python
Graticule(
    crs=None, extent=None, step=5.0, color="0.55",
    lw=0.35, ls=":", npts=120, zorder=1,
)
```

| Parameter | Type | Description |
|---|---|---|
| `extent` | `(lon0, lon1, lat0, lat1)` | required; which meridians/parallels to draw |
| `step` | `float` | spacing in degrees |
| `color`, `lw`, `ls` | | line style |
| `npts` | `int` | samples per line; raise for very wide maps |
| `zorder` | `float` | keep below the data |

## Functions

### `scale_bar(ax, **kwargs)` · `north_arrow(ax, **kwargs)` · `graticule(ax, **kwargs)`

Construct the corresponding artist, add it to `ax`, and return it.

```python
sb = mapelements.scale_bar(ax, length=500, crs=CRS)
sb.fontsize = 8          # the artist is returned, so you can tweak it
```

### `finish(ax, crs=None, data=None, extent=None, graticule=5.0, scalebar="auto", north="upper right", scalebar_loc=None, pad=0.02, legend=False, fill=True, zorder=30)`

One-call map furniture.

| Parameter | Description |
|---|---|
| `crs` | projection; defaults to `ax.projection` |
| `data` | `GeoDataFrame`; extent taken from `total_bounds` after `to_crs(crs)` |
| `extent` | lon/lat box; overrides `data` |
| `graticule` | spacing in degrees; `None`/`False` disables |
| `scalebar` | km, `"auto"`, or `None`/`False` |
| `north` | alias, tuple, or `None`/`False` |
| `scalebar_loc` | axes fraction; defaults to the corner opposite the north arrow |
| `pad` | fractional padding around the extent (default 2 %) |
| `legend` | `True` to place a borderless legend upper-left |
| `fill` | `True` to call `fit()` (single-axes figures only) |

Returns `ax`.

### `fit(ax)`

Set the axes to `[0, 0, 1, 1]` and adjust the figure height to the data aspect
ratio. No-op when the figure has more than one axes. Returns `ax`.

### `save(fig, stem, outdir="figs", formats=("pdf", "svg", "png"), dpi=600, allow_images=False, expect_text=None, strict=True)`

Write the figure and run `check_vector()` on the PDF/SVG. Returns
`{format: Path}`. Raises `NotVectorError` when `strict=True` and the check
fails.

### `check_vector(path, expect_text=None, allow_images=False) -> bool`

Inspect a PDF or SVG and print a report. Returns `True` when the file is
editable vector artwork.

### `pub_style(extra=None)`

Apply the journal defaults (`pdf.fonttype=42`, `svg.fonttype="none"`, 8 pt base
size, 0.8 pt axes). `extra` is merged into the defaults.

### `figure(width="double", height=90, **kwargs)`

Create `(fig, ax)` with a millimetre size. `width` accepts `"single"` (85 mm),
`"double"` (170 mm) or a number.

## Constants

| Name | Value |
|---|---|
| `CN_ALBERS` | Albers Equal Area, standard parallels 25°N/47°N, central meridian 105°E |
| `SINGLE_COLUMN` | `85.0` (mm) |
| `DOUBLE_COLUMN` | `170.0` (mm) |
| `MM` | `1 / 25.4` |

## Utilities

### `nice_length(km) -> float`

Round up to the next 1/2/5 × 10ⁿ value: `473 → 500`, `2.2 → 5`.

### `map_width_km(ax, crs) -> float`

Geodesic width of the current axis at its central latitude, in km.

## Exceptions

`NotVectorError` — raised by `save()` when the exported PDF/SVG fails the vector
checks.
