# Installation

## Requirements

| Dependency | Version | Needed for |
|---|---|---|
| Python | ≥ 3.9 | everything |
| matplotlib | ≥ 3.6 | everything |
| numpy | ≥ 1.22 | everything |
| pyproj | ≥ 3.4 | projections, geodesic lengths |
| geopandas | ≥ 0.13 | optional, convenient data handling |
| cartopy | ≥ 0.22 | optional, `GeoAxes` maps |

`pyproj` is a hard requirement because the scale bar and the north arrow are
computed from real geodesy, not from pixel guesses.

## Install

```bash
pip install mapelements
```

With the optional geo stack:

```bash
pip install "mapelements[geo,cartopy]"
```

Extras:

| Extra | Pulls in |
|---|---|
| `geo` | geopandas |
| `cartopy` | cartopy |
| `test` | pytest |
| `dev` | geo + cartopy + pytest + build + twine |

## Verify the install

```python
import mapelements
print(mapelements.__version__)

fig, ax = mapelements.figure("double", 90)
mapelements.finish(ax, crs=mapelements.CN_ALBERS, extent=(94, 121, 26, 43))
fig.savefig("check.pdf")
print(mapelements.check_vector("check.pdf"))
```

The last line must print `True` together with a short report: fonts
`CIDFontType2`/`TrueType`, a non-zero number of text operators, zero image
objects.

## Development install

```bash
git clone https://github.com/sanpi0205/mapelements
cd mapelements
pip install -e ".[dev]"
pytest
```

The test suite uses the Agg backend and writes only inside the repository, so it
runs headless and offline.

## Troubleshooting the install

- **`ModuleNotFoundError: pyproj`** — install a binary wheel:
  `pip install "pyproj>=3.4"`. On conda: `conda install -c conda-forge pyproj`.
- **cartopy build errors on Linux** — prefer
  `conda install -c conda-forge cartopy` or a manylinux wheel.
- **conflict with an old `mapkit` package** — unrelated project, different
  import name (`mapelements`), no conflict.
