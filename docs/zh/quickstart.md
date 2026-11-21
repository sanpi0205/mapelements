# 快速开始

大约二十行，从投影后的研究区到可直接投稿的 PDF。

## 1. 套用刊物版式

```python
import mapelements

mapelements.pub_style()
```

`pub_style()` 设定的是“能出图”和“编辑能改图”之间的差别：

```python
{
    "pdf.fonttype": 42,      # TrueType，文字仍是文字（3 = Type3 轮廓）
    "ps.fonttype": 42,
    "svg.fonttype": "none",  # 输出 <text>，不是 <path>
    "font.size": 8,
    ...
}
```

可以按需覆盖：

```python
mapelements.pub_style({"font.sans-serif": ["Arial", "DejaVu Sans"]})
```

## 2. 用毫米建图

```python
fig, ax = mapelements.figure("double", 110)   # 170 mm × 110 mm
```

`"single"` 是 85 mm，`"double"` 是 170 mm，对应常见单栏/双栏。期刊版心不同就直接传毫米数。

## 3. 在投影坐标系里画数据

```python
import geopandas as gpd
from pyproj import Transformer

CRS = mapelements.CN_ALBERS           # Albers，标准纬线 25°N/47°N，中央经线 105°E
fwd = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)

gdf.to_crs(CRS).plot(ax=ax, column="value", cmap="YlGnBu",
                     edgecolor="0.3", linewidth=0.4)
```

中纬度区域图不要用未投影的等经纬度（Plate Carrée）：东西向会被拉长，比例尺也失去意义。

## 4. 一行加上地图要素

```python
mapelements.finish(ax, crs=CRS, data=gdf)
```

它按数据范围设图幅（外扩 2%），画 5° 经纬网、自动取整的比例尺（图宽的 18%，取 1/2/5×10ⁿ）、
右上角指北针，同时去掉坐标框并让地图铺满画布。

想手动指定范围，就把 `data` 换成经纬度框：

```python
mapelements.finish(ax, crs=CRS, extent=(94, 121, 26, 43))
```

## 5. 导出并自检

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

如果 PDF 里出现 Type 3 字体或位图对象，`save()` 会抛 `NotVectorError`，
不合规的图不会悄悄流出去。

## 完整脚本

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

## 下一步

- [地图要素](elements.md) —— 三个 artist 的全部参数。
- [投影](projections.md) —— Albers、UTM、cartopy。
- [投稿导出](export.md) —— 交稿前的检查清单。
