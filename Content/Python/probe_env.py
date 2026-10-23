import os, unreal
open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/env-probe.txt","w",encoding="utf8").write(os.environ.get("DY_SCRIPT","NONE"))
unreal.SystemLibrary.quit_editor()
