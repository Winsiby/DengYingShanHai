"""Use the same cold FBX invariants as the full source."""
from pathlib import Path
SCRIPT=Path(__file__).resolve().parent.parent/'verify_lamp_fbx.py'
exec(compile(SCRIPT.read_text(encoding='utf-8'),str(SCRIPT),'exec'),globals())
SCRIPT=Path(__file__).resolve().parent.parent/'verify_lamp_source.py'
code=SCRIPT.read_text(encoding='utf-8').replace('DY_HeroSpotlight_Source.blend','DY_HeroSpotlight_RuntimeVariant.blend').replace("OUT/'LAMP_ORIGINAL_TEXTURE_CHECK.json'","OUT.parent/'LAMP_ORIGINAL_TEXTURE_CHECK.json'")
exec(compile(code,str(SCRIPT),'exec'),globals())
