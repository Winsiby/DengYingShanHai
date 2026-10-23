# -*- coding: utf-8 -*-
import pathlib
src = pathlib.Path(r"D:\灯影山海\Docs\AI-Usage-20261024\make_doc.py")
s = src.read_text(encoding="utf-8")

old = """        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement('w:cantSplit'); trPr.append(cant)
    return t"""
new = """        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement('w:cantSplit'); trPr.append(cant)
        if r_i == 0:
            trPr.append(OxmlElement('w:tblHeader'))
    # keep the whole table on one page when it fits: all but the last row keep with next
    for r_i, row in enumerate(t.rows[:-1]):
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.keep_with_next = True
    return t"""
assert old in s
s = s.replace(old, new)

s = s.replace("""    pf.space_before = Pt(0); pf.space_after = Pt(3); pf.line_spacing = 1.45""",
              """    pf.space_before = Pt(0); pf.space_after = Pt(2); pf.line_spacing = 1.4""")
s = s.replace("""    r = p.add_run("· " + text); set_run_font(r, size=size)""",
              """    r = p.add_run("·  " + text); set_run_font(r, size=size)""")
src.write_text(s, encoding="utf-8")
print("patched")
