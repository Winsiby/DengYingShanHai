#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Puzzles/DYPuzzleTypes.h"
#include "DYPuzzleDefinition.generated.h"

UCLASS(BlueprintType)
class DENGYINGSHANHAI_API UDYPuzzleDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle")
	FName PuzzleId = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle")
	FDYTargetRange LightPosition;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle")
	FDYTargetRange PuppetPosition;

	/** NAME_None disables the discrete pose requirement. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle")
	FName RequiredPuppetPoseId = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle", meta = (ClampMin = "0.0", Units = "s"))
	double RequiredHoldSeconds = 1.0;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle", meta = (MultiLine = "true"))
	FText DebugNotes;
};
