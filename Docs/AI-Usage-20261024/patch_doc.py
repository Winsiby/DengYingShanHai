# -*- coding: utf-8 -*-
import pathlib, re
src = pathlib.Path(r"D:\灯影山海\Docs\AI-Usage-20261024\make_doc.py")
s = src.read_text(encoding="utf-8")

# 1) table rows must not split across pages
s = s.replace("""    for row in t.rows:
        for c_i, cell in enumerate(row.cells):
            cell.width = Cm(widths[c_i])
    return t""",
"""    for row in t.rows:
        for c_i, cell in enumerate(row.cells):
            cell.width = Cm(widths[c_i])
        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement('w:cantSplit'); trPr.append(cant)
    return t""")

# 2) headings keep with next
s = s.replace("""def heading(text):
    para(text, size=12, bold=True, cn=HEAD_CN, space_before=10, space_after=5)""",
"""def heading(text):
    p = para(text, size=12, bold=True, cn=HEAD_CN, space_before=10, space_after=5)
    p.paragraph_format.keep_with_next = True
    return p""")

# 3) bullet helper with hanging indent instead of first-line indent
s = s.replace("""heading("二、主要AI工具及使用情况")""",
"""def bullet(text, size=10.5):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.72); pf.first_line_indent = Cm(-0.42)
    pf.space_before = Pt(0); pf.space_after = Pt(3); pf.line_spacing = 1.45
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run("· " + text); set_run_font(r, size=size)
    return p

heading("二、主要AI工具及使用情况")""")

s = s.replace("""    para("· " + line, indent_chars=2, space_after=3)""", """    bullet(line)""")

# 4) footer page numbers
s = s.replace("""doc.save(str(DOC))""",
"""footer_p = sec.footer.paragraphs[0]
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
def add_field(par, instr):
    r = par.add_run(); set_run_font(r, size=9)
    fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), instr)
    inner_r = OxmlElement('w:r'); inner_t = OxmlElement('w:t'); inner_t.text = "1"
    inner_r.append(inner_t); fld.append(inner_r)
    par._p.append(fld)
r0 = footer_p.add_run("第 "); set_run_font(r0, size=9)
add_field(footer_p, "PAGE")
r1 = footer_p.add_run(" 页 / 共 "); set_run_font(r1, size=9)
add_field(footer_p, "NUMPAGES")
r2 = footer_p.add_run(" 页"); set_run_font(r2, size=9)

doc.save(str(DOC))""")

src.write_text(s, encoding="utf-8")
print("patched", len(s))
