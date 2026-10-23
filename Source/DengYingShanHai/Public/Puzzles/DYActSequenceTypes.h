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

/** One campaign chapter: a title plus the act steps it plays through the same Director machine. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYChapterEntry
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Campaign")
	FText ChapterTitle;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Campaign")
	FText ChapterSubtitle;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Campaign")
	TArray<FDYActSequenceEntry> Steps;
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

	/** Campaign chapter (four-act run); INDEX_NONE when the map authors a single chapter. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Act Sequence")
	int32 ChapterIndex = INDEX_NONE;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Act Sequence")
	int32 ChapterCount = 0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Act Sequence")
	FText ChapterTitle;
};
