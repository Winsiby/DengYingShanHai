#pragma once

#include "CoreMinimal.h"
#include "DYControlTypes.generated.h"

class APawn;

UENUM(BlueprintType)
enum class EDYControlChannel : uint8
{
	PrimaryAxis,
	SecondaryAxis,
	Confirm,
	Cancel
};

UENUM(BlueprintType)
enum class EDYControlPhase : uint8
{
	Started,
	Ongoing,
	Completed,
	Canceled
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYControlIntent
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Interaction")
	EDYControlChannel Channel = EDYControlChannel::PrimaryAxis;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Interaction")
	FVector2D Value = FVector2D::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Interaction", meta = (Units = "s"))
	double DeltaSeconds = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Interaction")
	EDYControlPhase Phase = EDYControlPhase::Ongoing;
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYControlContext
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Interaction")
	TObjectPtr<APawn> InstigatorPawn = nullptr;
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYControlSnapshot
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Interaction")
	bool bIsValid = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Interaction")
	double PrimaryNormalized = 0.0;

	/** Optional authored state for controls such as the shadow puppet. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Interaction")
	FName PoseId = NAME_None;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Interaction")
	FTransform WorldTransform = FTransform::Identity;
};
