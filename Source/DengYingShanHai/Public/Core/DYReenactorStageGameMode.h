#pragma once

#include "CoreMinimal.h"
#include "Core/DYStageGameMode.h"
#include "DYReenactorStageGameMode.generated.h"

/** Dev-only composition; inherited controller, HUD and stage registration are unchanged. */
UCLASS()
class DENGYINGSHANHAI_API ADYReenactorStageGameMode : public ADYStageGameMode
{
	GENERATED_BODY()

public:
	ADYReenactorStageGameMode();
};
