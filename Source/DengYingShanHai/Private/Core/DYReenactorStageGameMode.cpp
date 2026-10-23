#include "Core/DYReenactorStageGameMode.h"

#include "Player/DYReenactorOperatorPawn.h"

ADYReenactorStageGameMode::ADYReenactorStageGameMode()
{
	DefaultPawnClass = ADYReenactorOperatorPawn::StaticClass();
	HUDClass = nullptr;
}
