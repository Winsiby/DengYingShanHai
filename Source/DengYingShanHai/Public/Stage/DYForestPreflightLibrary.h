#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Stage/DYForestGeometryLibrary.h"
#include "DYForestPreflightLibrary.generated.h"

UENUM(BlueprintType)
enum class EDYForestPreflightStatus : uint8
{
	InvalidGeometry,
	InvalidSilhouette,
	OutsideScreen,
	ProtectedOverlap,
	Valid
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYForestPreflightResult
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Preflight")
	EDYForestPreflightStatus Status = EDYForestPreflightStatus::InvalidGeometry;

	/** Available only for Valid. Token copying is diagnostic, never authorization. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Preflight")
	FDYForestGeometrySample FinalGeometry;
};

/** Value-only counterpart of the Dev candidate's conservative silhouette preflight. */
UCLASS()
class DENGYINGSHANHAI_API UDYForestPreflightLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Checks full growth against the actual torso/head local-bounds corners.
	 * Padding is a caller-authored fraction of receiver-local Y/Z extents.
	 * Protected space spans combined Y bounds and extends upward from the lowest Z.
	 * No World, Actor writes, assets, time, puzzle truth, or token authorization.
	 * Failures contain no usable FinalGeometry, including partial branch output.
	 */
	UFUNCTION(BlueprintPure, Category = "DY|Forest Preflight")
	static FDYForestPreflightResult CheckForestSilhouette(
		const FDYStaffContactPresentationSnapshot& Contact,
		const TArray<FDYForestBranchDefinition>& BranchDefinitions,
		const FVector& MeshMin, const FVector& MeshMax,
		const FVector& TorsoMin, const FVector& TorsoMax, const FTransform& TorsoTransform,
		const FVector& HeadMin, const FVector& HeadMax, const FTransform& HeadTransform,
		double PaddingFraction);
};
