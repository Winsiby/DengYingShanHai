# -*- coding: utf-8 -*-
import unreal, traceback
out=[]
try:
    out.append("hasattr KismetTextLibrary=%s" % hasattr(unreal,'KismetTextLibrary'))
    out.append("text-ish: %s" % [n for n in dir(unreal) if 'Text' in n][:15])
    cls = unreal.load_class(None, '/Script/Engine.KismetTextLibrary')
    out.append("load_class=%s" % cls)
    if cls:
        try:
            t = cls.conv_string_to_text("测试 abc")
            out.append("conv ok type=%s val=%s" % (type(t), t))
        except Exception as e:
            out.append("conv fail %s" % e)
    try:
        t2 = unreal.Text()
        out.append("Text() ok dir=%s" % [n for n in dir(t2) if not n.startswith('_')][:12])
    except Exception as e:
        out.append("Text() fail %s" % e)
    try:
        s = unreal.Text(string="abc")
        out.append("Text(string) ok=%s" % s)
    except Exception as e:
        out.append("Text(string) fail %s" % e)
    try:
        import unreal as u
        fn = getattr(u, 'KismetTextLibrary', None)
        out.append("ktext attr=%r" % (fn,))
    except Exception as e:
        out.append("attr err %s" % e)
except Exception:
    out.append(traceback.format_exc())
finally:
    print("TEXTPROBE " + " | ".join(out))
    unreal.SystemLibrary.quit_editor()
