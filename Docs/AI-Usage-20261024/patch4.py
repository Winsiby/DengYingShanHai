# -*- coding: utf-8 -*-
import pathlib
src = pathlib.Path(r"D:\灯影山海\Docs\AI-Usage-20261024\make_doc.py")
s = src.read_text(encoding="utf-8")
s = s.replace("sec.top_margin = Cm(2.4); sec.bottom_margin = Cm(2.4)",
              "sec.top_margin = Cm(2.2); sec.bottom_margin = Cm(2.15)")
s = s.replace("para(\"填表日期：2026 年 10 月 24 日\", align=\"right\", space_before=10)",
              "para(\"填表日期：2026 年 10 月 24 日\", align=\"right\", space_before=8)")
s = s.replace("""    p = para(text, size=12, bold=True, cn=HEAD_CN, space_before=10, space_after=5)""",
              """    p = para(text, size=12, bold=True, cn=HEAD_CN, space_before=8, space_after=5)""")
src.write_text(s, encoding="utf-8")
print("ok")
