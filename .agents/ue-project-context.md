# Unreal project context

- Project: `DengYingShanHai`
- Engine: Unreal Engine 5.8.3 installed at `C:\Program Files\Epic Games\UE_5.8`
- Build entry: `C:\UEProjects\DengYingShanHai` (junction to the current repository)
- Runtime module: `DengYingShanHai`
- API macro: `DENGYINGSHANHAI_API`
- Core classes: `ADYStageGameMode`, `ADYStagePlayerController`, `ADYStageOperatorPawn`
- Input: Enhanced Input; mapping contexts owned by the local `ADYStagePlayerController`; Pawn binds semantic actions.
- Networking: none in the phase-one demo.
- GAS: not enabled.
- Runtime plugin dependency: Enhanced Input only.
- Editor-only asset generation and validation: retain the built-in Python Script Plugin with `TargetAllowList: ["Editor"]`; it is required by `Scripts/Create-Phase1Assets.py` and `Scripts/Verify-Phase1Assets.py` but must not become a Game runtime dependency.
- Dev-only mapping for phase-one validation: WASD move, mouse look, `R` operator reset. These are not accepted final gameplay bindings.
- Phase-one reset means operator-transform reset only; it does not decide the whole-experience reset strategy.
