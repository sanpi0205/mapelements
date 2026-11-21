# -*- coding: utf-8 -*-
"""Export helpers: save() writes the artwork, check_vector() audits it."""
from __future__ import annotations

import re
import zlib
from collections import Counter
from pathlib import Path


class NotVectorError(RuntimeError):
    """Raised when the exported artwork is not editable vector graphics."""


def _pdf_streams(raw: bytes):
    for m in re.finditer(rb"stream\r?\n", raw):
        start = m.end()
        end = raw.find(b"endstream", start)
        if end == -1:
            continue
        try:
            yield zlib.decompress(raw[start:end])
        except zlib.error:
            continue


def check_vector(path, expect_text=None, allow_images=False) -> bool:
    """
    Inspect a PDF/SVG for editable vector content and print a report.

    PDF passes when there is no Type 3 font, at least one Tj/TJ operator and
    no image XObject (unless ``allow_images``).
    SVG passes when it contains <text> and no <image>.
    """
    path = Path(path)
    raw = path.read_bytes()
    ok = True
    print(f"\n=== {path.name} ===")

    if path.suffix.lower() == ".pdf":
        fonts = [f.decode() for f in re.findall(
            rb"/Subtype\s*/(Type3|TrueType|Type1|Type0|CIDFontType0|"
            rb"CIDFontType2|OpenType|MMType1)", raw)]
        cnt = Counter(fonts)
        print("font subtypes:", dict(cnt) or "none")
        if cnt.get("Type3"):
            ok = False
            print("  x Type 3 font: glyphs are outlines, text is not editable"
                  " (set pdf.fonttype=42)")

        text_ops, samples = 0, []
        for s in _pdf_streams(raw):
            text_ops += s.count(b"Tj") + s.count(b"TJ")
            for m in re.finditer(rb"\(([^()\\]{1,80})\)\s*Tj", s):
                samples.append(m.group(1).decode("latin-1", "ignore"))
        print("text operators Tj/TJ:", text_ops)
        if text_ops == 0:
            ok = False
            print("  x no text operators: the page is a bitmap or fully outlined")

        n_img = len(re.findall(rb"/Subtype\s*/Image", raw))
        print("image XObjects:", n_img)
        if n_img and not allow_images:
            ok = False
            print(
                "  x image object found "
                "(pass allow_images=True for imagery basemaps)"
            )

        if expect_text:
            joined = "".join(samples)
            missing = [t for t in expect_text if t not in joined]
            if missing:
                print("  ! not found in literal strings:", missing,
                      "(CJK text is CID-encoded and cannot be matched literally; "
                      "double-click the text in Illustrator to verify)")

    elif path.suffix.lower() == ".svg":
        svg = raw.decode("utf-8", "ignore")
        n_text = len(re.findall(r"<text[\s>]", svg))
        n_path = len(re.findall(r"<path[\s>]", svg))
        n_img = len(re.findall(r"<image[\s>]", svg))
        print(f"<text>: {n_text}   <path>: {n_path}   <image>: {n_img}")
        if n_text == 0:
            ok = False
            print(
                "  x no <text>: text was converted to paths "
                "(set svg.fonttype='none')"
            )
        if n_img and not allow_images:
            ok = False
            print("  x contains a raster <image>")
    else:
        print("  not a PDF/SVG file, check manually")
        return True

    print("result:", "PASS" if ok else "FAIL")
    return ok


def save(fig, stem, outdir="figs", formats=("pdf", "svg", "png"),
         dpi=600, allow_images=False, expect_text=None, strict=True):
    """Write the figure and audit the result.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
    stem : str
        File name without extension; use the figure number.
    outdir : str or pathlib.Path
        Output directory, created if missing.
    formats : tuple of str
        Formats to write; defaults to ``("pdf", "svg", "png")``.
    dpi : int
        Resolution of the PNG preview only.
    allow_images : bool
        Permit raster objects, e.g. an imagery basemap.
    expect_text : list of str, optional
        Substrings that should appear in the PDF (ASCII only).
    strict : bool
        Raise :class:`NotVectorError` when the audit fails (default ``True``).

    Returns
    -------
    dict
        Mapping ``{format: pathlib.Path}``.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    pdf_meta = {"Creator": "mapelements", "Producer": "matplotlib",
                "CreationDate": None, "ModDate": None}

    paths = {}
    for fmt in formats:
        fmt = fmt.lower().lstrip(".")
        p = outdir / f"{stem}.{fmt}"
        kw = {}
        if fmt == "pdf":
            kw["metadata"] = pdf_meta
        elif fmt == "svg":
            kw["metadata"] = {"Creator": "mapelements", "Date": None}
        elif fmt == "png":
            kw["dpi"] = dpi
        fig.savefig(p, format=fmt, **kw)
        paths[fmt] = p
        print(f"[saved] {p} ({p.stat().st_size / 1024:.1f} KB)")

    if "pdf" in paths:
        ok = check_vector(paths["pdf"], expect_text=expect_text,
                          allow_images=allow_images)
        if not ok and strict:
            raise NotVectorError(
                f"{paths['pdf']} failed the vector check; fix the figure or "
                f"pass strict=False to only warn.")
    if "svg" in paths:
        check_vector(paths["svg"], allow_images=allow_images)

    return paths
