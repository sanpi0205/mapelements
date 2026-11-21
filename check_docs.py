# -*- coding: utf-8 -*-
"""文档自检：Markdown 可解析、内部链接可达、锚点存在、Python 代码块语法正确。"""
import ast
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
EXTS = ["admonition", "attr_list", "def_list", "tables", "fenced_code", "toc"]

LINK_RE = re.compile(r"(?<!\!)\[([^\]]+)\]\(([^)\s]+)\)")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
CODE_RE = re.compile(r"```python\n(.*?)```", re.S)


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text).strip("-")


def anchors(path: Path) -> set:
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            out.add(slug(m.group(2)))
    return out


def main() -> int:
    pages = sorted(DOCS.rglob("*.md"))
    errors = []

    for page in pages:
        text = page.read_text(encoding="utf-8")
        try:
            markdown.markdown(text, extensions=EXTS)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{page}: markdown 解析失败: {exc}")

        for _, target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            file_part, _, anchor = target.partition("#")
            if file_part:
                dest = (page.parent / file_part).resolve()
                if not dest.exists():
                    errors.append(f"{page.name}: 链接目标不存在 -> {target}")
                    continue
            else:
                dest = page
            if anchor and anchor not in anchors(dest):
                errors.append(f"{page.name}: 锚点不存在 -> {target}")

        for _, target in IMG_RE.findall(text):
            if target.startswith(("http://", "https://")):
                continue
            dest = (page.parent / target).resolve()
            if not dest.exists():
                errors.append(f"{page.name}: 图片不存在 -> {target}")

        for i, block in enumerate(CODE_RE.findall(text), 1):
            if "..." in block or "…" in block:
                continue
            try:
                ast.parse(block)
            except SyntaxError as exc:
                errors.append(f"{page.name}: 第 {i} 个 python 代码块语法错误: {exc}")

    print(f"检查 {len(pages)} 个页面")
    if errors:
        print("\n".join(errors))
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
