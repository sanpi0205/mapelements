# 投稿导出

## 要求到底是什么意思

“矢量图、文字可修改”翻译成技术条件就是三条：

1. **矢量** —— 线条和填充是路径，不是像素；
2. **活文字** —— 标签是文字对象，不是轮廓，也没被烘焙进位图；
3. **不是扫描版 PDF** —— 整页背后没有一张大位图。

matplotlib 三条都能做到，前提是 PDF/SVG 后端配置正确。默认的
`pdf.fonttype = 3` 会把每个字形变成一堆曲线，编辑端根本没法改字。

## 三个关键设置

```python
mapelements.pub_style()   # 一次设好全部
```

```python
{
    "pdf.fonttype": 42,       # TrueType 子集，文字仍是文字
    "ps.fonttype": 42,
    "svg.fonttype": "none",   # 输出 <text>，不是 <path>
}
```

不用 `pub_style()` 的话，至少在保存前把这三项设上。

## `save()`

```python
paths = mapelements.save(fig, "Fig1")            # figs/Fig1.pdf/.svg/.png
paths = mapelements.save(fig, "Fig1", outdir="submission",
                         formats=("pdf", "svg"))
```

| 参数 | 含义 |
|---|---|
| `stem` | 不含扩展名的文件名，用图号 |
| `outdir` | 输出目录，不存在会自动创建 |
| `formats` | 默认 `("pdf", "svg", "png")` |
| `dpi` | 只影响 PNG 预览 |
| `allow_images` | 允许位图对象（仅影像底图时用） |
| `expect_text` | 期望在 PDF 中出现、用于比对的文字（仅 ASCII） |
| `strict` | 检查不通过时抛 `NotVectorError`（默认 `True`） |

PDF 元数据会清掉 `CreationDate`、`ModDate`，所以同一张图重复导出字节一致——
需要证明“提交文件与修回稿一致”时很有用。

## `check_vector()`

```python
ok = mapelements.check_vector("figs/Fig1.pdf")
```

检查项：

| 检查 | 通过条件 |
|---|---|
| 字体类型 | 无 `Type 3`；`TrueType` / `Type0` / `CIDFontType2` 都可以 |
| 文字指令 | 内容流里至少有一个 `Tj`/`TJ` |
| 位图对象 | `/Subtype /Image` 数量为 0 |
| SVG | 有 `<text>`，无 `<image>` |

`save()` 会自动调用它，失败即抛 `NotVectorError`，不合规的图不会进投稿系统。

CI 里可以这样用：

```bash
python -c "import mapelements,sys; sys.exit(0 if mapelements.check_vector('figs/Fig1.pdf') else 1)"
```

## 手工核验（Poppler）

装了 `poppler-utils` 的话：

```bash
pdffonts figs/Fig1.pdf        # 应为 TrueType/Type0；出现 "Type 3" 即失败
pdftotext figs/Fig1.pdf -     # 能抽出你的标签文字
pdfimages -list figs/Fig1.pdf # 应为空
```

## 交付 AI / EMF / Word / PPT

| 目标 | 做法 |
|---|---|
| **PDF（可编辑）** | 直接交 `Fig1.pdf`，最稳 |
| **AI** | Illustrator 打开 `Fig1.pdf` → 另存为 `.ai`，保留“创建 PDF 兼容文件” |
| **AI，中文改字** | 改用 `Fig1.svg` 打开；Unicode 文本比 CID 编码的 PDF 更可靠 |
| **EMF** | `inkscape Fig1.svg --export-type=emf -o Fig1.emf`，或用 LibreOffice Draw |
| **Word** | 插入 EMF；或插入 SVG 后“转换为形状” |
| **PPT** | 插入 SVG（Office 365）后“转换为形状”，或粘贴 EMF |

转成 EMF 后务必验证：插入 Word → 右键“编辑图片” → 取消组合。如果标签变成文本框，
说明文字保住了可编辑性。很多转换器会悄悄把文字变成路径。

提交前不要用 `cairosvg`、`svglib` 转 matplotlib 的 SVG：两者都会把文字拍成路径。

## 文件命名

- 按图号命名：`Fig1.pdf`、`Fig2.pdf`、`Fig1a.pdf`。
- 用 ASCII 文件名。投稿系统对中文名的处理经常出问题；确需对应，在投稿信里附一张
  `Fig1 = 图1` 的对照表。
- 各格式保持同一 stem：`Fig1.pdf`、`Fig1.svg`、`Fig1.png`。

## 交稿前检查清单

- [ ] 所有图都经 `mapelements.save()` 导出，无 `Type 3` 字体。
- [ ] `pdfimages -list` 为空（或只有已声明的影像底图）。
- [ ] 字体为 Arial / Helvetica / 标准中文字族。
- [ ] 尺寸与正文预留位置一致（85 mm 或 170 mm 宽）。
- [ ] 标签、单位、图例、子图字母与 Word 稿完全一致。
- [ ] 比例尺是整数值，参考纬度合理。
- [ ] 指北针指向真北（检查图幅边缘的偏角）。
- [ ] 没有用 `bbox_inches="tight"`，没有 `transparent=True`。
- [ ] 文件名与正文中的图号对应。
