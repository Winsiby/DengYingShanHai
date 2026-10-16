#pragma once

#include "CoreMinimal.h"
#include "DYStaffGeometryTypes.generated.h"

/** Value evidence from the actual Staff mesh. A/B are local -Z/+Z, not a chosen finale tip. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYStaffGeometrySnapshot
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff")
	bool bIsValid = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff")
	FTransform ComponentTransform = FTransform::Identity;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff")
	FVector LocalMin = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff")
	FVector LocalMax = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff")
	FVector EndAWorld = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Staff")
	FVector EndBWorld = FVector::ZeroVector;
};
