#pragma once

#include "CoreMinimal.h"
#include "Interaction/DYControlTypes.h"
#include "Puzzles/DYPuzzleTypes.h"
#include "DYResolvedPuzzleSnapshot.generated.h"

/**
 * Value-only gameplay evidence captured once at Resolve. The Director owns its
 * lifetime; readers receive a copy. Staff-component transforms and curtain
 * contact/projection belong to the presentation layer, not this success rule.
 */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYResolvedPuzzleSnapshot
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle|Resolved Snapshot")
	bool bIsResolved = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle|Resolved Snapshot")
	FName PuzzleId = NAME_None;

	/** Opaque activation identity; reset/restart/another Director cannot reuse it. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle|Resolved Snapshot")
	FGuid Token;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle|Resolved Snapshot")
	FDYEvaluationResult Evaluation;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle|Resolved Snapshot")
	FDYControlSnapshot Light;

	/** A missing optional puppet does not invalidate an already-resolved puzzle. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle|Resolved Snapshot")
	FDYControlSnapshot Puppet;
};
