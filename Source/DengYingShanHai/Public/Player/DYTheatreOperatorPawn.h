#pragma once

#include "CoreMinimal.h"
#include "Player/DYStageOperatorPawn.h"
#include "DYTheatreOperatorPawn.generated.h"

class UDYFootstepAudioComponent;

/** Opt-in Dev carrier. All movement, inputs, camera and reset remain inherited unchanged. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYTheatreOperatorPawn : public ADYStageOperatorPawn
{
	GENERATED_BODY()
public:
	ADYTheatreOperatorPawn();
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="DY|Audio") TObjectPtr<UDYFootstepAudioComponent> FootstepAudio;
};
