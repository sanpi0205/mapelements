# mapelements

**Vector map elements for matplotlib — scale bars, north arrows and graticules
that stay editable in PDF and SVG.**

`mapelements` adds the three cartographic elements that matplotlib does not ship
with, and it adds them as real `matplotlib.artist.Artist` objects made of
`Patch`, `Line2D` and `Text`. Nothing is rasterised: no `OffsetImage`, no
temporary figure rendering. A figure exported to PDF or SVG keeps paths as paths
and labels as text, so an editor can still change "500 km" in Illustrator.

This is the documentation index. Choose a language:

- [English](en/index.md)
- [中文](zh/index.md)

## At a glance

```python
import mapelements

mapelements.pub_style()                        # journal defaults
fig, ax = mapelements.figure("double", 110)    # 170 mm wide, mm-based
gdf.to_crs(mapelements.CN_ALBERS).plot(ax=ax, column="value")

mapelements.finish(ax, crs=mapelements.CN_ALBERS, data=gdf)
mapelements.save(fig, "Fig1")                  # figs/Fig1.pdf + .svg + .png
```

## Documentation layout

| Path | Content |
|---|---|
| `docs/en/` | English manual |
| `docs/zh/` | 中文手册 |
| `mkdocs.en.yml` / `mkdocs.zh.yml` | static-site configs for each language |

Preview locally:

```bash
pip install mkdocs
mkdocs serve -f mkdocs.en.yml    # English, http://127.0.0.1:8000
mkdocs serve -f mkdocs.zh.yml    # 中文
```
