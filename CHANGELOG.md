# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

> 从 0.1.1 起，变更记录改由
> [GitHub Releases](https://github.com/sanpi0205/mapelements/releases) 自动生成。
> 本文件只保留 0.1.0 的历史记录。

## [0.1.0] - 2026-11-21

### Added

- `ScaleBar`, `NorthArrow`, `Graticule` as `matplotlib.artist.Artist` subclasses:
  they can be added with `ax.add_artist()`, removed, re-used via `.copy()`, and
  are rebuilt at draw time so they follow changes to limits and figure size.
- `scale_bar()`, `north_arrow()`, `graticule()` function wrappers.
- `finish()` one-call helper (extent + graticule + scale bar + north arrow).
- `fit()` to remove subplot margins on single-panel map figures.
- `pub_style()` with journal defaults (`pdf.fonttype=42`, `svg.fonttype="none"`,
  7–8 pt type) and `figure()` sized in millimetres.
- `save()` with vector self-checks (`NotVectorError` on failure) and
  `check_vector()` for arbitrary PDF/SVG files.
- `CN_ALBERS` constant (Albers Equal Area, standard parallels 25°N/47°N).
- Scale bars are computed from a geodesic east–west chord at the bar's own
  latitude, so projection scale factors are accounted for automatically.
- North arrows are rotated by the projection's meridian convergence.
- Bilingual documentation under `docs/en/` and `docs/zh/` (installation,
  quickstart, map elements, projections, layout, export, API, cookbook, FAQ),
  with `mkdocs.en.yml` / `mkdocs.zh.yml` site configs and `check_docs.py`
  for link/anchor checking.
- Static documentation site (English at `/en/`, Chinese at `/zh/`, bilingual
  landing page) published to GitHub Pages by `.github/workflows/docs.yml`.
- `docs/make_figures.py`, which renders the six figures embedded in the manual.

### Fixed

- `ScaleBar.get_window_extent()` raised `AttributeError` when the figure used
  `constrained_layout` (the child artists had no figure attached yet).

[0.1.0]: https://github.com/sanpi0205/mapelements/releases/tag/v0.1.0
