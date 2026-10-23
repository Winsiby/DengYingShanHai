#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Stage/DYStaffPresentationTypes.h"
#include "DYStaffDropLibrary.generated.h"

UENUM(BlueprintType)
enum class EDYStaffDropStatus : uint8
{
	InvalidSnapshot,
	InvalidGeometry,
	InvalidGroundLine,
	NotAboveGround,
	InvalidProgress,
	Valid
};

/** Value-only animation sample. Valid geometry is NOT current-token authorization or contact. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYStaffDropSample
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Drop")
	EDYStaffDropStatus Status = EDYStaffDropStatus::InvalidSnapshot;

	/** Copied identity only. The caller must still check the live Presentation/Director. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Drop")
	FGuid Token;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Drop")
	FName PuzzleId = NAME_None;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Drop")
	double NormalizedProgress = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Drop")
	FTransform StaffWorldTransform = FTransform::Identity;

	/** Full displacement from the captured pose; no absolute world-Z or receiver position preset. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Drop")
	FVector FullTranslationWorld = FVector::ZeroVector;

	/** Shadow goal on the receiver, NOT the physical position of the Staff component. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Drop")
	FVector ShadowTargetWorld = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff Drop")
	FDYStaffProjectionCapture Projection;
};

/** Stateless Resolve-to-ground math. No World, Actor writes, timer, seconds, token issue or CDO state. */
UCLASS()
class DENGYINGSHANHAI_API UDYStaffDropLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Uses the actual captured A (mesh-local -Z), preserving receiver-local X/Y,
	 * Staff rotation/scale and ray depth. Finite progress is clamped to [0,1].
	 * Recomputes cached geometry; cannot validate a live token, move Staff, authorize
	 * contact/forest, restore owner-relative translation, or finish the experience.
	 */
	UFUNCTION(BlueprintPure, Category = "DY|Staff Drop")
	static FDYStaffDropSample SampleStaffDrop(
		const FDYStageResolvedPresentationSnapshot& Resolved, double NormalizedProgress);
};
