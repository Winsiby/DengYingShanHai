import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8-sig")
p.write_text(s, encoding="utf-8-sig")
print("bom ok", p.stat().st_size)
