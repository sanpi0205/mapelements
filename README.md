# mapelements

[![PyPI](https://img.shields.io/pypi/v/mapelements.svg)](https://pypi.org/project/mapelements/)
[![Python](https://img.shields.io/pypi/pyversions/mapelements.svg)](https://pypi.org/project/mapelements/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/zhangbo/mapelements/actions/workflows/ci.yml/badge.svg)](https://github.com/zhangbo/mapelements/actions/workflows/ci.yml)

**矢量**地图要素，专为期刊插图：比例尺、指北针、经纬网。

全部用 matplotlib 的 `Patch` / `Line2D` / `Text` 绘制，不产生任何位图。
导出 PDF/SVG 后线条仍是路径、文字仍是文字，在 Illustrator 里可以直接改。
配合 `pdf.fonttype = 42`（`pub_style()` 会自动设置），满足"图中文字可修改"
的投稿要求。

## 文档

| 语言 | 内容 |
|---|---|
| [English](docs/en/index.md) | installation, quickstart, elements, projections, layout, export, API, cookbook, FAQ |
| [中文](docs/zh/index.md) | 安装、快速开始、地图要素、投影、版式、投稿导出、API、实用配方、常见问题 |

本地预览：

```bash
pip install -e ".[docs]"
mkdocs serve -f mkdocs.en.yml     # http://127.0.0.1:8000
mkdocs serve -f mkdocs.zh.yml
```

在线站点（推送 `main` 后由 `.github/workflows/docs.yml` 自动发布）：
<https://zhangbo.github.io/mapelements/>

文档自检（链接、锚点、图片、代码块语法）：

```bash
python check_docs.py
```

文档里的插图由 [`docs/make_figures.py`](docs/make_figures.py) 生成：

```bash
python docs/make_figures.py
```

## 安装

```bash
pip install mapelements

# 需要 geopandas / cartopy 时
pip install "mapelements[geo,cartopy]"
```

## 快速开始

```python
import matplotlib.pyplot as plt
import mapelements

mapelements.pub_style()                       # 刊物版式：Type42、7-8 pt
fig, ax = mapelements.figure("double", 110)   # 170 mm 宽

gdf.to_crs(mapelements.CN_ALBERS).plot(ax=ax, column="value", cmap="YlGnBu")

mapelements.finish(ax, crs=mapelements.CN_ALBERS, data=gdf)
mapelements.save(fig, "Fig1")                  # figs/Fig1.pdf + .svg + .png
```

## 三种用法

**Artist 方式**（和 matplotlib 原生写法一致，可 `remove()`、可 `copy()`）

```python
from mapelements import ScaleBar, NorthArrow, Graticule

ax.add_artist(Graticule(crs=CRS, extent=(94, 121, 26, 43), step=5))
ax.add_artist(ScaleBar(length=500, crs=CRS, loc=(0.05, 0.06)))
ax.add_artist(NorthArrow(crs=CRS, loc="upper right"))
```

**函数方式**

```python
mapelements.scale_bar(ax, length=500, crs=CRS)
mapelements.north_arrow(ax, crs=CRS)
```

**一站式**

```python
mapelements.finish(ax, crs=CRS, data=gdf, scalebar="auto", north="upper right")
```

## 多子图复用

```python
sb = ScaleBar(length=500, crs=CRS)
nw = NorthArrow(crs=CRS)
for ax in axs.flat:
    ax.add_artist(sb.copy())     # 每个 Axes 需要一份副本
    ax.add_artist(nw.copy())
```

## 为什么不用现成的包

| | `matplotlib_scalebar` | `matplotlib_map_utils` | **mapelements** |
|---|---|---|---|
| 矢量 | 是 | **否**（整条渲染成位图） | 是 |
| 文字可编辑 | 是 | 否 | 是 |
| 黑白分段 | 否 | 是 | 是 |
| 指北针 / 经纬网 | 否 | 是 / 否 | 是 |
| 依赖 | 额外一个包 | 额外一个包 + 临时 figure 渲染 | 只要 matplotlib + pyproj |

## API

| 对象 | 说明 |
|---|---|
| `ScaleBar(length="auto", crs=None, loc=(0.05, 0.06), divisions=4, colors=("black", "white"), height_frac=0.010, fontsize=7, unit_label="km", show_mid=False, ref_lon=None, ref_lat=None)` | 黑白分段比例尺；`"auto"` 按图幅取 1/2/5×10ⁿ |
| `NorthArrow(crs=None, loc="upper right", length_pts=14, label="N", weight="normal")` | 真北指北针（按经线收敛定向） |
| `Graticule(crs=None, extent=(lon0, lon1, lat0, lat1), step=5, color="0.55", lw=0.35, ls=":")` | 经纬网 |
| `scale_bar(ax, **kw)` / `north_arrow(ax, **kw)` / `graticule(ax, **kw)` | 构造并添加，返回 artist |
| `finish(ax, crs, data=None, extent=None, graticule=5, scalebar="auto", north="upper right", fill=True, legend=False)` | 一站式收尾 |
| `fit(ax)` | 单幅地图铺满画布（多子图自动跳过） |
| `save(fig, "Fig1", outdir="figs", formats=("pdf", "svg", "png"))` | 导出并自检，不通过抛 `NotVectorError` |
| `check_vector(path)` | 检查已有 PDF/SVG 是否可编辑矢量 |
| `pub_style(extra=None)` / `figure(width, height_mm)` | 刊物版式 / 按 mm 建图 |

常量：`CN_ALBERS`（Albers 25/47，中央经线 105°E）、`MM`、`SINGLE_COLUMN`、`DOUBLE_COLUMN`。

## 设计要点

- **绘制时才计算几何**：`draw()` 中按当前 `xlim`、轴尺寸构建子图元，改了范围或
  画布大小后自动重排，不需要重新添加；先 `add_artist` 再 `set_xlim` 也可以。
- **比例尺精度**：按参考纬度处正东方向的测地线长度换算，自动吸收投影尺度因子。
- **指北针精度**：按投影的经线收敛角旋转，锥形投影边缘不会指偏。
- **cartopy 兼容**：`crs=ax.projection` 即可（内部取 `proj4_init` 交给 pyproj）。
- **不栅格化**：没有 `OffsetImage`、没有临时 figure 渲染。

## 开发

```bash
git clone https://github.com/zhangbo/mapelements
cd mapelements
pip install -e ".[dev]"
pytest
```

## 许可证

MIT，见 [LICENSE](LICENSE)。
