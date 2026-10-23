# -*- coding: utf-8 -*-
import pathlib
src = pathlib.Path(r"D:\灯影山海\Docs\AI-Usage-20261024\make_doc.py")
s = src.read_text(encoding="utf-8")

s = s.replace("""def heading(text):
    p = para(text, size=12, bold=True, cn=HEAD_CN, space_before=10, space_after=5)
    p.paragraph_format.keep_with_next = True
    return p""",
"""def heading(text, new_page=False):
    p = para(text, size=12, bold=True, cn=HEAD_CN, space_before=10, space_after=5)
    p.paragraph_format.keep_with_next = True
    if new_page:
        p.paragraph_format.page_break_before = True
    return p""")

s = s.replace("""heading("三、代表性AI使用过程")
para("（一）三具影偶：从平面概念图到可投影的实体皮影", size=10.5, bold=True, space_before=4, space_after=3)""",
"""heading("三、代表性AI使用过程", new_page=True)
sub1 = para("（一）三具影偶：从平面概念图到可投影的实体皮影", size=10.5, bold=True, space_before=4, space_after=3)
sub1.paragraph_format.keep_with_next = True""")

s = s.replace("""para("（二）四幕换偶与烛龙昼夜：AI 草案经人工实测纠正", size=10.5, bold=True, space_before=8, space_after=3)""",
"""sub2 = para("（二）四幕换偶与烛龙昼夜：AI 草案经人工实测纠正", size=10.5, bold=True, space_before=8, space_after=3)
sub2.paragraph_format.page_break_before = True
sub2.paragraph_format.keep_with_next = True""")

src.write_text(s, encoding="utf-8")
print("ok")
