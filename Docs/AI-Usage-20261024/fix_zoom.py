# -*- coding: utf-8 -*-
import zipfile, shutil, pathlib, re
p = pathlib.Path(r"D:\灯影山海\Docs\AI-Usage-20261024\灯影山海_人工智能工具使用情况说明.docx")
tmp = p.with_suffix(".tmp.docx")
with zipfile.ZipFile(p) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/settings.xml":
            s = data.decode("utf-8")
            s2 = re.sub(r'<w:zoom(?![^>]*w:percent)([^>]*)/>', r'<w:zoom w:percent="100"\1/>', s)
            if s2 == s and "<w:zoom" not in s:
                s2 = s.replace("</w:settings>", '<w:zoom w:percent="100"/></w:settings>')
            data = s2.encode("utf-8")
        zout.writestr(item, data)
shutil.move(str(tmp), str(p))
print("fixed zoom")
