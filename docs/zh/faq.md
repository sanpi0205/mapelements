# 常见问题

## 比例尺太长 / 太短

几乎都是 CRS 不匹配。长度是按你传入的 `crs`、在比例尺所在纬度上取测地线算出来的。
如果 `crs` 错了（例如给米制坐标轴传了经纬度），宽度会差几个数量级。

```python
# 轴是用 gdf.to_crs(CRS) 画的，就传同一个 CRS
ax.add_artist(ScaleBar(length=500, crs=CRS))
```

在 cartopy 的 `GeoAxes` 上可以省略 `crs`，会用 `ax.projection`。

## 报错 `ValueError: ScaleBar needs crs= (a projected CRS)`

你把 artist 加到了普通 `Axes` 上却没传 `crs`。要么补上，要么用
`finish(ax, crs=...)`，它会帮你传下去。

## 图上什么都没有

三种常见原因：

1. 只创建了对象，没加进轴——需要 `ax.add_artist(...)`；
2. `loc` 超出 `0..1`（位置是 axes fraction）；
3. 加完 artist 后改了坐标范围，但还没有重绘。任何 `savefig`、`draw()`
   或 notebook 渲染都会重建几何，所以只有在绘制前检查 `ax.patches` 时才会遇到。

## `save()` 抛 `NotVectorError`

检查发现了 Type 3 字体或图像对象。两种情况：

- **你的图里确实有位图层**（晕渲、卫星影像、被 `set_rasterized(True)` 的
  `contourf`）。这是合理的，传 `allow_images=True`。
- **文字被轮廓化了**。确认 `pub_style()` 在 `savefig` 之前执行，或自行设置
  `matplotlib.rcParams["pdf.fonttype"] = 42`。

## PDF 里的文字在 Illustrator 里改不了

先查字体类型：

```bash
pdffonts figs/Fig1.pdf
```

出现 `Type 3` 说明字形已变成曲线——文件是用 matplotlib 默认设置保存的。
套用 `pub_style()` 后重新导出即可。

## 中文显示成方块

matplotlib 选到了不含中文的字体。指定本机存在的字族：

```python
mapelements.pub_style({"font.sans-serif": ["Microsoft YaHei", "SimHei",
                                           "DejaVu Sans"]})
```

## 警告 `findfont: Failed to find font weight bold`

所选中文字族没有粗体。`NorthArrow(weight="normal")`（默认值）可以避免；
或安装带粗体的字族。

## 指北针看起来是歪的

这是对的。锥形投影的经线收敛，图幅边缘的真北确实偏离竖直方向。箭头计算的是真实方向，
在那里画一根笔直的箭头反而是错的。

## `fit()` 没反应

`fit()` 只在“一个 figure 只有一个 Axes”时生效。多子图请保留自己的布局，
并调用 `finish(..., fill=False)`。

## 比例尺和别的工具算出来的不一致

不同工具的假设不同。本库在比例尺所在纬度取正东方向的测地线再投影，
对投影图上的水平比例尺是精确的。别的工具若按“每像素多少米”估算，
差异就是投影的尺度因子——UTM 带内通常千分之几，大范围锥形投影会更大。

## 能和 cartopy 的 `transform=` 一起用吗

能。数据照常用 `transform=ccrs.PlateCarree()` 画；三个 artist 自己做 pyproj 计算，
不干扰 cartopy。

## 能在 Jupyter 里用吗

可以。inline 后端每次渲染都会重绘 artist，`save()` 同样可用。

## 与 `matplotlib_scalebar`、`matplotlib_map_utils` 的区别

| | `matplotlib_scalebar` | `matplotlib_map_utils` | `mapelements` |
|---|---|---|---|
| 矢量输出 | 是 | **否**，整条比例尺变成 `OffsetImage` | 是 |
| 文字可编辑 | 是 | 否 | 是 |
| 黑白分段 | 否 | 是 | 是 |
| 指北针 | 否 | 是 | 是 |
| 经纬网 | 否 | 否 | 是 |
| 额外依赖 | 有 | 有（且每次绘制渲染临时 figure） | 只需 matplotlib + pyproj |

## 怎么反馈问题

到 <https://github.com/sanpi0205/mapelements/issues> 提 issue，附最小复现：
CRS 字符串、坐标轴范围、添加 artist 的那段代码。
