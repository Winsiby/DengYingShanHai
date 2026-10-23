#pragma once

#include "CoreMinimal.h"
#include "DYControlExitRecorder.generated.h"

/**
 * Automation-only recorder for OnControlStateChanged broadcasts.
 * Lives in the test tree so the stale-actor exit contract can be observed from
 * automation without adding any product-facing API or state.
 */
UCLASS()
class UDYControlExitRecorder : public UObject
{
	GENERATED_BODY()

public:
	/** Total number of OnControlStateChanged broadcasts observed. */
	int32 Count = 0;

	/** Broadcasts whose actor argument was null (stale-session exits). */
	int32 NullActorCount = 0;

	/** Broadcasts with bIsControlling=true (control entries). */
	int32 EnterCount = 0;

	/** Broadcasts with bIsControlling=false (control exits). */
	int32 ExitCount = 0;

	UFUNCTION()
	void HandleControlStateChanged(AActor* ControlledActor, bool bIsControlling)
	{
		++Count;
		if (ControlledActor == nullptr)
		{
			++NullActorCount;
		}
		if (bIsControlling)
		{
			++EnterCount;
		}
		else
		{
			++ExitCount;
		}
	}
};
