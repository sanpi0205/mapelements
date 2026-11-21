# -*- coding: utf-8 -*-
"""mapelements — journal-quality vector map elements for matplotlib.

Scale bars, north arrows and graticules implemented as matplotlib ``Artist``
subclasses. Add them with ``ax.add_artist(...)`` like any other artist; they are
built from ``Patch`` / ``Line2D`` / ``Text`` only, so PDF/SVG exports keep
editable paths and live text.

Three ways to use the package::

    # 1) artist style
    from mapelements import ScaleBar, NorthArrow, Graticule
    ax.add_artist(ScaleBar(length=500, crs=CRS))
    ax.add_artist(NorthArrow(crs=CRS, loc="upper right"))

    # 2) function style
    import mapelements
    mapelements.scale_bar(ax, length=500, crs=CRS)

    # 3) one call for the whole map furniture
    mapelements.finish(ax, crs=CRS, data=gdf)
    mapelements.save(fig, "Fig1")
"""
from importlib.metadata import PackageNotFoundError, version

from .api import finish, fit
from .artists import Graticule, NorthArrow, ScaleBar, graticule, north_arrow, scale_bar
from .export import NotVectorError, check_vector, save
from .geom import CN_ALBERS, map_width_km, nice_length
from .style import DOUBLE_COLUMN, MM, SINGLE_COLUMN, figure, pub_style

try:
    __version__ = version("mapelements")
except PackageNotFoundError:  # 直接从源码目录运行，且尚未安装
    __version__ = "0.0.0+unknown"

__all__ = [
    # artist 类
    "ScaleBar", "NorthArrow", "Graticule",
    # 函数封装
    "scale_bar", "north_arrow", "graticule",
    # 收尾与导出
    "finish", "fit", "save", "check_vector", "NotVectorError",
    # 版式
    "pub_style", "figure", "MM", "SINGLE_COLUMN", "DOUBLE_COLUMN",
    # 常量 / 工具
    "CN_ALBERS", "nice_length", "map_width_km",
    "__version__",
]
