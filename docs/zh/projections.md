# 投影

比例尺和指北针只有在投影坐标系里才有意义。因此本库假设你的坐标轴是投影坐标，
并且你告诉它用的是哪个 CRS。

## 传入 CRS

每个要素都接受 `crs`：

```python
ScaleBar(length=500, crs="+proj=aea +lat_1=25 +lat_2=47 +lon_0=105 +datum=WGS84")
NorthArrow(crs=CRS)
Graticule(crs=CRS, extent=...)
```

支持的形式：

- PROJ 字符串（如上）；
- EPSG 代码或 `pyproj.CRS`：`crs="EPSG:3857"`、`crs=CRS.from_epsg(32650)`；
- cartopy CRS：`crs=ax.projection`（内部取 `proj4_init`）。

在 cartopy 的 `GeoAxes` 上可以完全省略 `crs`，因为 `ax.projection` 就是它。

## 中国：Albers

`mapelements.CN_ALBERS` 是现成的全国 Albers 等积投影：

```text
+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +datum=WGS84 +units=m
```

等积、标准纬线 25°N 与 47°N、中央经线 105°E。比例尺在标准纬线上严格成立，
这也是它最该放的位置。

```python
CRS = mapelements.CN_ALBERS
gdf.to_crs(CRS).plot(ax=ax)
mapelements.finish(ax, crs=CRS, data=gdf)
```

## 局部图：UTM

```python
utm = "+proj=utm +zone=50 +datum=WGS84 +units=m +no_defs"
gdf.to_crs(utm).plot(ax=ax)
mapelements.finish(ax, crs=utm, data=gdf)
```

UTM 带内尺度变形小于 0.1%，比例尺放在哪儿都没问题。

## cartopy

```python
import cartopy.crs as ccrs

proj = ccrs.AlbersEqualArea(central_longitude=105, standard_parallels=(25, 47))
ax = fig.add_subplot(111, projection=proj)
ax.set_extent([94, 121, 26, 43], crs=ccrs.PlateCarree())
ax.coastlines(resolution="110m", lw=0.4)

ax.add_artist(ScaleBar(length="auto", crs=ax.projection))
ax.add_artist(NorthArrow(crs=ax.projection))
```

`GeoAxes.get_xlim()` 返回的就是投影坐标，正是本库需要的，不需要任何转换。
数据照常用 `transform=ccrs.PlateCarree()` 画。

要让 cartopy 可复现（并且离线可用），把数据目录固定到项目内：

```python
import cartopy
cartopy.config["data_dir"] = "assets/cartopy"
```

## 为什么不用 Plate Carrée

中纬度区域的等经纬度图，东西向被拉长 1/cos(lat)：40°N 约 1.3 倍。在这种图上
比例尺只在一条纬线上成立，审稿人一眼能看出形变。如果确实要用经纬度轴，
本库会按比例尺所在纬度标定，但图注里应当说明——多数情况下，投影后的图更好。

## `extent` 与 `data`

`finish()` 两者都接受：

```python
finish(ax, crs=CRS, data=gdf)                 # 用重投影后数据的 total_bounds
finish(ax, crs=CRS, extent=(94, 121, 26, 43)) # 显式经纬度框
```

同时给出时 `extent` 优先。经纬度框会在 12×12 网格上采样后重投影，
所以轴范围贴合弯曲边界，而不是简单的对角点包围盒。

## 重投影建议

- 先重投影再画：`gdf.to_crs(CRS)` 比让 cartopy 在绘制时逐多边形重投影快得多。
- 细节过多的几何先简化：`gdf.simplify(0.001, preserve_topology=True)`，
  只作用于绘图副本，不改分析数据。
- 保留地理坐标用于算距离和画经纬网：本库会从你传入的投影 CRS 自动反算。
