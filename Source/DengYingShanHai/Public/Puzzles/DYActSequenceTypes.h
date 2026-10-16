#pragma once

#include "CoreMinimal.h"
#include "DYActSequenceTypes.generated.h"

class UDYPuzzleDefinition;

/** Experience progression is distinct from Evaluator Searching/Holding/Resolved. */
UENUM(BlueprintType)
enum class EDYActSequencePhase : uint8
{
	Inactive,
	Playing,
	AwaitingTransition,
	AwaitingFinale,
	Complete
};

/** Explicit authored order. Targets remain exclusively in the referenced Definition. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYActSequenceEntry
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Act Sequence")
	TObjectPtr<UDYPuzzleDefinition> Definition;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Act Sequence")
	FText ActTitle;
};

/** Passive public display snapshot: no answer, tolerance, progress or control reference. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYActSequenceSnapshot
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Act Sequence")
	bool bSequenceEnabled = false;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Act Sequence")
	int32 ActIndex = INDEX_NONE;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Act Sequence")
	int32 ActCount = 0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Act Sequence")
	FText ActTitle;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Act Sequence")
	EDYActSequencePhase Phase = EDYActSequencePhase::Inactive;
};
