# -*- coding: utf-8 -*-
"""pytest 公共设置：强制无界面后端、把 src 加入路径、提供工作区内的输出目录。"""
import shutil
import sys
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def outdir():
    """项目内的临时输出目录（避免依赖系统 temp，便于受限环境运行）。"""
    path = ROOT / "tests" / "_out"
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)
