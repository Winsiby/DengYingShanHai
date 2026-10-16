# Wide-blade 6x source candidate

Independent snapshot of build_canopy.py; only the four blade halfwidths change from 3/2.7 cm to 18/16.2 cm. Wood, petioles, axes, positions, thickness and UV rules stay unchanged; original bounds must remain +/-34,+/-28,+/-50cm. No automatic recentering or normalization is permitted to pass this gate. Original builder/source remain untouched.

One combined mesh: the original closed tapered stem plus four closed wooden petioles and four closed wide leaf solids. Wood0 is slot 0, Leaf1 is slot 1. All nine topological shells are intentionally intersecting, not boolean-unioned; SOURCE.json records point-inside proof at each stem/stalk and stalk/blade connection, per-shell winding/volume and full vertex/face/UV/material data.

Original procedural stylized leaf geometry with Codex assistance; no download, paid asset, image/3D generation service or third-party mesh/texture. Not a botanical peach-tree reconstruction, historical original or traditional-school authenticity claim. Neutral rough preview materials are not final UE art. The two PNGs are actual Cycles CPU renders of the FBX source geometry, not hand-drawn compositions.

Centimeters, mesh-local Z [-50,+50], centered XY bounds and real wood root/tip at (0,0,-50)/(0,0,50). FBX forward -Y/up Z, unit scale applied; the project native axis mapping must still be independently checked. Export contains only one mesh, one UV0, two materials, no textures, bones, animations, wind or collision helpers.

This tool does not alter the 15-branch layout or run UE. Overall branch diameter is normalized from the whole mesh bounds, and early growth scales Z only: flattened leaves/width popping, root continuity, conservative projection bounds, material slot retention, native source correspondence, actual same-light shadows and final visuals remain unaccepted. Preserve all prior source/BP/map assets.
