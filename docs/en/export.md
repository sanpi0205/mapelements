# Exporting for a journal

## What the requirement actually means

"Vector artwork with editable text" is three conditions:

1. **Vector** — lines and fills are paths, not pixels;
2. **Live text** — labels are text objects, not outlines and not baked into a
   bitmap;
3. **Not a scanned PDF** — no page-sized raster behind the whole figure.

matplotlib can satisfy all three, but only if the PDF/SVG backend is configured
correctly. The default `pdf.fonttype = 3` turns every glyph into a set of curves
an editor cannot retype.

## The three settings

```python
mapelements.pub_style()   # sets all of them
```

```python
{
    "pdf.fonttype": 42,       # TrueType subset, text stays text
    "ps.fonttype": 42,
    "svg.fonttype": "none",   # emits <text>, not <path>
}
```

If you do not use `pub_style()`, set at least these three before saving.

## `save()`

```python
paths = mapelements.save(fig, "Fig1")            # figs/Fig1.pdf/.svg/.png
paths = mapelements.save(fig, "Fig1", outdir="submission",
                         formats=("pdf", "svg"))
```

| Argument | Meaning |
|---|---|
| `stem` | file name without extension; use the figure number |
| `outdir` | output directory, created if missing |
| `formats` | defaults to `("pdf", "svg", "png")` |
| `dpi` | resolution of the PNG preview only |
| `allow_images` | permit raster objects (only for imagery basemaps) |
| `expect_text` | substrings that should appear in the PDF (ASCII only) |
| `strict` | raise `NotVectorError` when the check fails (default `True`) |

PDF metadata is scrubbed (`CreationDate`, `ModDate` removed) so that exporting
the same figure twice yields identical bytes — handy when you need to prove that
the submitted file matches the revised one.

## `check_vector()`

```python
ok = mapelements.check_vector("figs/Fig1.pdf")
```

It reports and enforces:

| Check | Pass condition |
|---|---|
| Font types | no `Type 3`; `TrueType` / `Type0` / `CIDFontType2` are fine |
| Text operators | at least one `Tj`/`TJ` in the content streams |
| Raster objects | zero `/Subtype /Image` |
| SVG | has `<text>`, no `<image>` |

`save()` calls it automatically and raises `NotVectorError` on failure, so a
bad figure cannot reach the submission system unnoticed.

A CI-style one-liner:

```bash
python -c "import mapelements,sys; sys.exit(0 if mapelements.check_vector('figs/Fig1.pdf') else 1)"
```

## Manual verification (Poppler)

If you have `poppler-utils`:

```bash
pdffonts figs/Fig1.pdf        # expect TrueType/Type0; "Type 3" means failure
pdftotext figs/Fig1.pdf -     # should print your labels
pdfimages -list figs/Fig1.pdf # should be empty
```

## Delivering AI / EMF / Word / PPT

| Target | How |
|---|---|
| **PDF (editable)** | submit `Fig1.pdf` directly — the safest option |
| **AI** | open `Fig1.pdf` in Illustrator → *Save As* → `.ai`; keep "Create PDF Compatible File" |
| **AI, CJK editing** | open `Fig1.svg` instead; Unicode text survives better than CID-encoded PDF |
| **EMF** | `inkscape Fig1.svg --export-type=emf -o Fig1.emf`, or LibreOffice Draw |
| **Word** | insert the EMF; or insert the SVG and use *Convert to Shape* |
| **PPT** | insert SVG (Office 365) and *Convert to Shape*, or paste the EMF |

After converting to EMF, always verify: insert into Word, right-click → *Edit
Picture* → ungroup. If the labels become text boxes, the conversion kept them
editable. Many converters quietly outline text.

Never place a matplotlib SVG through `cairosvg` or `svglib` before submitting:
both flatten text to paths.

## File naming

- Name by figure number: `Fig1.pdf`, `Fig2.pdf`, `Fig1a.pdf`.
- Use ASCII names. Submission systems mangle Chinese filenames surprisingly
  often; keep a mapping table (`Fig1 = 图1`) in the cover letter if needed.
- Keep the stem identical across formats: `Fig1.pdf`, `Fig1.svg`, `Fig1.png`.

## Pre-submission checklist

- [ ] Every figure exported through `mapelements.save()` — no `Type 3` fonts.
- [ ] `pdfimages -list` empty (or a declared imagery basemap only).
- [ ] Fonts are Arial / Helvetica / a standard CJK family.
- [ ] Size matches the manuscript slot (85 mm or 170 mm wide).
- [ ] Labels, units, legend, panel letters identical to the Word manuscript.
- [ ] Scale bar length is a round number and its latitude is meaningful.
- [ ] North arrow points to true north (check the tilt at map edges).
- [ ] No `bbox_inches="tight"`, no `transparent=True` in the saved version.
- [ ] File names match the figure numbers used in the text.
