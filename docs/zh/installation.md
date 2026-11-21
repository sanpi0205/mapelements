# 安装

## 环境要求

| 依赖 | 版本 | 用途 |
|---|---|---|
| Python | ≥ 3.9 | 全部功能 |
| matplotlib | ≥ 3.6 | 全部功能 |
| numpy | ≥ 1.22 | 全部功能 |
| pyproj | ≥ 3.4 | 投影、测地线长度 |
| geopandas | ≥ 0.13 | 可选，处理矢量数据 |
| cartopy | ≥ 0.22 | 可选，`GeoAxes` 地图 |

`pyproj` 是硬依赖：比例尺和指北针都基于真实测地线计算，而不是按像素估算。

## 安装

```bash
pip install mapelements
```

连同可选的 GIS 依赖：

```bash
pip install "mapelements[geo,cartopy]"
```

| extras | 包含 |
|---|---|
| `geo` | geopandas |
| `cartopy` | cartopy |
| `test` | pytest |
| `dev` | geo + cartopy + pytest + build + twine |

## 验证安装

```python
import mapelements
print(mapelements.__version__)

fig, ax = mapelements.figure("double", 90)
mapelements.finish(ax, crs=mapelements.CN_ALBERS, extent=(94, 121, 26, 43))
fig.savefig("check.pdf")
print(mapelements.check_vector("check.pdf"))
```

最后一行应输出 `True` 和一份报告：字体为 `CIDFontType2`/`TrueType`、
文字指令数大于 0、位图对象为 0。

## 开发安装

```bash
git clone https://github.com/sanpi0205/mapelements
cd mapelements
pip install -e ".[dev]"
pytest
```

测试使用 Agg 后端，只往仓库内部写文件，可在无图形界面、无网络的环境下运行。

## 安装排错

- **`ModuleNotFoundError: pyproj`** —— 装二进制 wheel：
  `pip install "pyproj>=3.4"`；conda 用户可 `conda install -c conda-forge pyproj`。
- **Linux 上 cartopy 编译失败** —— 优先用 conda-forge 或 manylinux wheel。
- **与旧的 `mapkit` 包冲突？** —— 那是另一个项目，导入名不同（`mapelements`），
  不会冲突。
