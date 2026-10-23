# -*- coding: utf-8 -*-
import pathlib, subprocess, sys
base = pathlib.Path(r"D:\灯影山海\Docs\AI-Usage-20261024")
pdf = base / "灯影山海_人工智能工具使用情况说明.pdf"
# Render via PyMuPDF if available, else pdftoppm
try:
    import fitz
    doc = fitz.open(str(pdf))
    print("PAGES", doc.page_count)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=110)
        out = base / f"page{i+1}.png"
        pix.save(str(out))
        print("PNG", out.name, out.stat().st_size, pix.width, pix.height)
except ImportError:
    print("NO_FITZ")
