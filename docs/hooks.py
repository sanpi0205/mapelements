"""MkDocs hook: copy the shared image assets into each built site.

The English and Chinese manuals live in ``docs/en`` and ``docs/zh`` but share
``docs/assets``.  MkDocs only copies files below ``docs_dir``, so the images
would otherwise be missing from the generated site.
"""
import shutil
from pathlib import Path


def on_post_build(config, **kwargs):
    docs_dir = Path(config.docs_dir)
    site_dir = Path(config.site_dir)
    assets = docs_dir.parent / "assets"
    if not assets.is_dir():
        return
    for dest in (site_dir / "assets", site_dir.parent / "assets"):
        shutil.copytree(assets, dest, dirs_exist_ok=True)
