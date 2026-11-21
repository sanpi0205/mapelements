# -*- coding: utf-8 -*-
"""Journal defaults and millimetre-based figure sizing."""
from __future__ import annotations

import matplotlib as mpl

MM = 1 / 25.4

SINGLE_COLUMN = 85.0   # mm，单栏
DOUBLE_COLUMN = 170.0  # mm，双栏

RC = {
    # 文字保持为文字，而不是 Type3 轮廓 / <path>
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    # 字体
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Times New Roman",
                        "Microsoft YaHei", "SimHei",
                        "Noto Sans CJK SC", "DejaVu Sans"],
    "mathtext.fontset": "dejavusans",
    "mathtext.default": "regular",
    "axes.unicode_minus": False,
    # 印刷字号 / 线宽（pt）
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "legend.frameon": False,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "lines.linewidth": 1.0,
    "patch.linewidth": 0.5,
    # 尺寸控制：禁止 tight 自动裁切
    "savefig.bbox": "standard",
    "savefig.pad_inches": 0.02,
    "savefig.facecolor": "white",
    "savefig.transparent": False,
    "figure.facecolor": "white",
    "figure.dpi": 150,
    "savefig.dpi": 600,
}


def pub_style(extra: dict | None = None) -> None:
    """Apply the journal defaults; call once before creating figures."""
    rc = dict(RC)
    if extra:
        rc.update(extra)
    mpl.rcParams.update(rc)


def figure(width: float | str = DOUBLE_COLUMN, height: float = 90,
           **kwargs):
    """Create ``(fig, ax)`` with a millimetre size.

    ``width`` accepts ``"single"`` (85 mm), ``"double"`` (170 mm) or a number of
    millimetres; ``height`` is always in millimetres.
    """
    import matplotlib.pyplot as plt

    if isinstance(width, str):
        width = {"single": SINGLE_COLUMN, "double": DOUBLE_COLUMN}[width.lower()]
    fig, ax = plt.subplots(figsize=(width * MM, height * MM), **kwargs)
    return fig, ax
