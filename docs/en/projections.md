# Projections

Scale bars and north arrows only mean something on a projected map. The whole
library therefore assumes that your axes are in projected coordinates and that
you tell it which CRS that is.

## Pass a CRS

Every element accepts `crs`:

```python
ScaleBar(length=500, crs="+proj=aea +lat_1=25 +lat_2=47 +lon_0=105 +datum=WGS84")
NorthArrow(crs=CRS)
Graticule(crs=CRS, extent=...)
```

Accepted forms:

- a PROJ string, as above;
- an EPSG code or `pyproj.CRS`: `crs="EPSG:3857"`, `crs=CRS.from_epsg(32650)`;
- a cartopy CRS: `crs=ax.projection` (the `proj4_init` string is used).

On a cartopy `GeoAxes` you can omit `crs` entirely, because `ax.projection`
provides it.

## China: Albers

`mapelements.CN_ALBERS` is a ready-made Albers Equal Area for national maps:

```text
+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +datum=WGS84 +units=m
```

Equal-area, standard parallels 25°N and 47°N, central meridian 105°E. Scale is
true along the standard parallels, which is exactly where a scale bar should be
placed.

```python
CRS = mapelements.CN_ALBERS
gdf.to_crs(CRS).plot(ax=ax)
mapelements.finish(ax, crs=CRS, data=gdf)
```

## Local maps: UTM

```python
utm = "+proj=utm +zone=50 +datum=WGS84 +units=m +no_defs"
gdf.to_crs(utm).plot(ax=ax)
mapelements.finish(ax, crs=utm, data=gdf)
```

Scale distortion is below 0.1 % within a UTM zone, so any bar position is fine.

## Cartopy

```python
import cartopy.crs as ccrs

proj = ccrs.AlbersEqualArea(central_longitude=105, standard_parallels=(25, 47))
ax = fig.add_subplot(111, projection=proj)
ax.set_extent([94, 121, 26, 43], crs=ccrs.PlateCarree())
ax.coastlines(resolution="110m", lw=0.4)

ax.add_artist(ScaleBar(length="auto", crs=ax.projection))
ax.add_artist(NorthArrow(crs=ax.projection))
```

`GeoAxes.get_xlim()` returns projection coordinates, which is exactly what the
artists expect — no conversion is needed. Plot your data with
`transform=ccrs.PlateCarree()` as usual.

To make cartopy reproducible (and work offline), pin its data directory:

```python
import cartopy
cartopy.config["data_dir"] = "assets/cartopy"
```

## Why not Plate Carrée

A plate carrée map of a mid-latitude region stretches east–west by 1/cos(lat):
about 1.3× at 40°N. A scale bar drawn on it is only valid along one parallel,
and reviewers notice the distortion. If you must use lon/lat axes, the bar is
calibrated at its own latitude and you should say so in the caption — but a
projected map is almost always the better choice.

## Extent versus data

`finish()` accepts either:

```python
finish(ax, crs=CRS, data=gdf)                 # from total_bounds of the reprojected data
finish(ax, crs=CRS, extent=(94, 121, 26, 43)) # explicit lon/lat box
```

`extent` wins when both are given. The lon/lat box is sampled on a 12 × 12 grid
and reprojected, so the resulting axis limits follow the curved boundary instead
of a naive corner-to-corner box.

## Reprojection tips

- Reproject once, then plot: `gdf.to_crs(CRS)` is cheaper than letting cartopy
  reproject every polygon at draw time.
- Simplify very detailed geometries before plotting:
  `gdf.simplify(0.001, preserve_topology=True)` — this affects the drawing copy,
  not your analysis data.
- Keep the geographic CRS around for computing distances and for the graticule;
  `mapelements` handles that internally from the projected CRS you pass.
