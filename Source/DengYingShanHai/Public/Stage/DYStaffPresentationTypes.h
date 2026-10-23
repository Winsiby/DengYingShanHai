#pragma once

#include "CoreMinimal.h"
#include "Interaction/DYControlTypes.h"
#include "Stage/DYStaffProjectionLibrary.h"
#include "DYStaffPresentationTypes.generated.h"

/** Authored line on a planar receiver, not the physical backstage floor. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYNarrativeGroundLineSnapshot
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	bool bIsValid = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FVector WorldAnchor = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	double ScreenLocalZ = 0.0;
};

/** Captured only on a live Resolve event; never reconstructed from later animation. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYStageResolvedPresentationSnapshot
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	bool bHasSnapshot = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FGuid Token;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FName PuzzleId = NAME_None;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FDYControlSnapshot Light;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FDYControlSnapshot Puppet;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FDYStaffProjectionCapture Projection;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FDYNarrativeGroundLineSnapshot GroundLine;
};

/** One accepted cosmetic contact, with the actual current A-end geometry. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYStaffContactPresentationSnapshot
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	bool bHasContact = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FGuid Token;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FName PuzzleId = NAME_None;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FDYStaffProjectionCapture Projection;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Presentation")
	FVector ContactWorldPosition = FVector::ZeroVector;
};
