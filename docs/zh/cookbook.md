# 实用配方

短小、可直接运行的例子。都假设：

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mapelements

CRS = mapelements.CN_ALBERS
mapelements.pub_style()
```

## 1. 从 GeoDataFrame 出省级地图

```python
fig, ax = mapelements.figure("double", 110)
gdf.to_crs(CRS).plot(ax=ax, column="value", cmap="YlGnBu",
                     edgecolor="0.3", linewidth=0.4,
                     legend=True,
                     legend_kwds={"shrink": 0.45, "pad": 0.02})
mapelements.finish(ax, crs=CRS, data=gdf, scalebar=500)
mapelements.save(fig, "Fig1")
```

自动色标挤占图面时，改成 `legend=False`，在 `save()` 前自己加
`fig.colorbar(..., ax=ax, fraction=0.03, pad=0.02)`。

## 2. cartopy + 海岸线

```python
import cartopy.crs as ccrs

proj = ccrs.AlbersEqualArea(central_longitude=105, standard_parallels=(25, 47))
fig = plt.figure(figsize=(6.7, 4.4))
ax = fig.add_subplot(111, projection=proj)
ax.set_extent([94, 121, 26, 43], crs=ccrs.PlateCarree())
ax.coastlines(resolution="110m", lw=0.4)

ax.add_artist(mapelements.ScaleBar(length="auto", crs=ax.projection,
                                   loc=(0.05, 0.07)))
ax.add_artist(mapelements.NorthArrow(crs=ax.projection))
mapelements.save(fig, "Fig2", outdir="figs")
```

![cartopy 海岸线地图](../assets/cookbook-cartopy.png)

## 3. 位图底图 + 矢量要素

```python
ax.imshow(hillshade, extent=[x0, x1, y0, y1], cmap="gray", zorder=0)
gdf.to_crs(CRS).plot(ax=ax, facecolor="none", edgecolor="C3", lw=0.5)
mapelements.finish(ax, crs=CRS, data=gdf)
mapelements.save(fig, "Fig3", allow_images=True)   # 唯一一张位图就是底图
```

图注里注明底图（“90 m 晕渲”），其余要素保持矢量。

## 4. 填色等值线不生成 40 MB 的 PDF

```python
cf = ax.contourf(lon, lat, field, levels=20, transform=ccrs.PlateCarree())
cf.set_rasterized(True)     # 只栅格化这一层
mapelements.finish(ax, crs=ax.projection, extent=(94, 121, 26, 43))
mapelements.save(fig, "Fig4", allow_images=True)
```

文字、海岸线、经纬网、比例尺、指北针仍是矢量。

## 5. 两个子图，一套配置

```python
fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.2), constrained_layout=True)
sb = mapelements.ScaleBar(length=500, crs=CRS, loc=(0.06, 0.08))
nw = mapelements.NorthArrow(crs=CRS)

for ax, ext in zip(axs, [(94, 108, 26, 43), (108, 121, 26, 43)]):
    gdf.to_crs(CRS).plot(ax=ax, column="value")
    mapelements.finish(ax, crs=CRS, extent=ext, fill=False,
                       graticule=5, scalebar=None, north=None)
    ax.add_artist(sb.copy())
    ax.add_artist(nw.copy())

mapelements.save(fig, "Fig5", formats=("pdf",))
```

## 6. 添加后再改样式

```python
sb = mapelements.scale_bar(ax, length=500, crs=CRS)
sb.colors = ("0.15", "white")
sb.fontsize = 6.5
sb.loc = (0.55, 0.06)
fig.canvas.draw()          # 几何在每次 draw 时重建
```

## 7. 按版面挪位置

```python
mapelements.ScaleBar(length=500, crs=CRS, loc=(0.62, 0.05))
mapelements.NorthArrow(crs=CRS, loc=(0.90, 0.60))
```

位置是 axes fraction：`(0, 0)` 左下、`(1, 1)` 右上。

## 8. 中文标签

```python
mapelements.pub_style({"font.sans-serif": ["Microsoft YaHei", "SimHei",
                                           "Arial", "DejaVu Sans"]})
ax.set_xlabel("经度 (°E)")
ax.set_ylabel("纬度 (°N)")
```

投稿前在 Illustrator 里确认：CID 编码的中文文本可编辑，但依赖编辑端有对应字体。
详见[投稿导出](export.md#交付-ai-emf-word-ppt)。

## 9. 打包提交

```python
for i, fig in enumerate(figures, start=1):
    mapelements.save(fig, f"Fig{i}", outdir="submission",
                     formats=("pdf", "png"))
```

每个图号一份 PDF，加一张 PNG 供审稿系统预览；SVG 需要时再生成。
