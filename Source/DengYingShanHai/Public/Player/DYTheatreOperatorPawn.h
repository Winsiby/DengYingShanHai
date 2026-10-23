#pragma once

#include "CoreMinimal.h"
#include "Player/DYStageOperatorPawn.h"
#include "DYTheatreOperatorPawn.generated.h"

class UDYFootstepAudioComponent;

/** Formal third-person operator carrier with the supplied reenactor visual. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYTheatreOperatorPawn : public ADYStageOperatorPawn
{
	GENERATED_BODY()
public:
	ADYTheatreOperatorPawn();

	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="DY|Audio") TObjectPtr<UDYFootstepAudioComponent> FootstepAudio;
};
