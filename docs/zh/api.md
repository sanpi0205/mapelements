# API 参考

```python
import mapelements
```

## Artist 类

### `ScaleBar`

```python
ScaleBar(
    length="auto", crs=None, loc=(0.05, 0.06),
    height_frac=0.010, divisions=4, colors=("black", "white"),
    lw=0.5, fontsize=7, unit_label="km", show_mid=False,
    ref_lon=None, ref_lat=None, zorder=30,
)
```

| 参数 | 类型 | 说明 |
|---|---|---|
| `length` | `float \| "auto"` | 比例尺长度（km）；`"auto"` = 图宽 18% 取整到 1/2/5×10ⁿ |
| `crs` | PROJ 字符串、EPSG、`pyproj.CRS`、cartopy CRS | 坐标轴所用投影；默认 `ax.projection` |
| `loc` | `(fx, fy)` | 左下角位置，axes fraction |
| `height_frac` | `float` | 条高，占轴高的比例 |
| `divisions` | `int` | 分段数 |
| `colors` | 序列 | 按段循环，如 `("black", "white")` |
| `lw` | `float` | 外框线宽（pt） |
| `fontsize` | `float` | 标签字号（pt） |
| `unit_label` | `str` | 追加到最后一个标签；传 `""` 可去掉 |
| `show_mid` | `bool` | 是否标出中值（仅偶数分段） |
| `ref_lon`、`ref_lat` | `float \| None` | 测地线参考点；默认取比例尺自身位置 |
| `zorder` | `float` | 绘制顺序 |

属性 `.length`、`.loc`、`.divisions`、`.height_frac`、`.colors`、`.fontsize`、
`.unit_label`、`.show_mid`、`.crs` 均可读写。`.resolved_length` 在首次绘制后保存
解析出的数值（之前为 `None`）。

### `NorthArrow`

```python
NorthArrow(
    crs=None, loc="upper right", length_pts=14, lw=0.6,
    fontsize=8, label="N", weight="normal", lon=None, lat=None, zorder=30,
)
```

| 参数 | 类型 | 说明 |
|---|---|---|
| `crs` | CRS | 默认 `ax.projection` |
| `loc` | `str \| (fx, fy)` | `"upper right"`、`"upper left"`、`"lower right"`、`"lower left"` |
| `length_pts` | `float` | 箭头长度（pt） |
| `lw` | `float` | 线宽 |
| `fontsize` | `float` | 标签字号 |
| `label` | `str` | 通常为 `"N"` |
| `weight` | `str` | `"normal"` 或 `"bold"` |
| `lon`、`lat` | `float \| None` | 计算真北的位置 |

箭头方向取自投影的经线收敛角，由正北方向 1 km 的测地线计算。

### `Graticule`

```python
Graticule(
    crs=None, extent=None, step=5.0, color="0.55",
    lw=0.35, ls=":", npts=120, zorder=1,
)
```

| 参数 | 类型 | 说明 |
|---|---|---|
| `extent` | `(lon0, lon1, lat0, lat1)` | 必填，决定画哪些经纬线 |
| `step` | `float` | 间隔（度） |
| `color`、`lw`、`ls` | | 线型 |
| `npts` | `int` | 每条线采样点数；图幅很宽时可调大 |
| `zorder` | `float` | 压在数据下面 |

## 函数

### `scale_bar(ax, **kwargs)` · `north_arrow(ax, **kwargs)` · `graticule(ax, **kwargs)`

构造对应 artist、加到 `ax` 上并返回它。

```python
sb = mapelements.scale_bar(ax, length=500, crs=CRS)
sb.fontsize = 8          # 返回了 artist，可以继续改
```

### `finish(ax, crs=None, data=None, extent=None, graticule=5.0, scalebar="auto", north="upper right", scalebar_loc=None, pad=0.02, legend=False, fill=True, zorder=30)`

一次完成地图收尾。

| 参数 | 说明 |
|---|---|
| `crs` | 投影；默认 `ax.projection` |
| `data` | `GeoDataFrame`；按 `to_crs(crs)` 后的 `total_bounds` 定范围 |
| `extent` | 经纬度框；优先于 `data` |
| `graticule` | 间隔（度）；`None`/`False` 关闭 |
| `scalebar` | km 数值、`"auto"`，或 `None`/`False` |
| `north` | 位置别名、元组，或 `None`/`False` |
| `scalebar_loc` | axes fraction；默认放在指北针的对角 |
| `pad` | 图幅外扩比例（默认 2%） |
| `legend` | `True` 时在左上角放无边框图例 |
| `fill` | `True` 时调用 `fit()`（仅单 Axes 图） |

返回 `ax`。

### `fit(ax)`

把轴设为 `[0, 0, 1, 1]`，并按数据纵横比调整画布高度。多子图时不做任何事。返回 `ax`。

### `save(fig, stem, outdir="figs", formats=("pdf", "svg", "png"), dpi=600, allow_images=False, expect_text=None, strict=True)`

导出并对 PDF/SVG 运行 `check_vector()`。返回 `{格式: Path}`。
`strict=True` 且检查失败时抛 `NotVectorError`。

### `check_vector(path, expect_text=None, allow_images=False) -> bool`

检查已有 PDF/SVG 并打印报告；是可编辑矢量时返回 `True`。

### `pub_style(extra=None)`

套用刊物默认设置（`pdf.fonttype=42`、`svg.fonttype="none"`、基准 8 pt、轴宽 0.8 pt）。
`extra` 会合并进默认值。

### `figure(width="double", height=90, **kwargs)`

按毫米创建 `(fig, ax)`。`width` 接受 `"single"`（85 mm）、`"double"`（170 mm）或数值。

## 常量

| 名称 | 值 |
|---|---|
| `CN_ALBERS` | Albers 等积投影，标准纬线 25°N/47°N，中央经线 105°E |
| `SINGLE_COLUMN` | `85.0`（mm） |
| `DOUBLE_COLUMN` | `170.0`（mm） |
| `MM` | `1 / 25.4` |

## 工具函数

### `nice_length(km) -> float`

向上取整到最近的 1/2/5×10ⁿ：`473 → 500`、`2.2 → 5`。

### `map_width_km(ax, crs) -> float`

当前坐标轴在中心纬度处的测地线宽度（km）。

## 异常

`NotVectorError` —— `save()` 在导出结果未通过矢量检查时抛出。
