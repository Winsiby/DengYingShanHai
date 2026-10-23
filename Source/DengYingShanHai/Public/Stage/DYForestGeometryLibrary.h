#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Stage/DYStaffPresentationTypes.h"
#include "DYForestGeometryLibrary.generated.h"

/** Authored geometry only: offsets are receiver-local +Y/+Z units, NOT UV or world cm. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYForestBranchDefinition
{
	GENERATED_BODY()

	/** First branch is the only root (-1). Other parents must precede their children. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DY|Forest Geometry")
	int32 ParentIndex = INDEX_NONE;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DY|Forest Geometry")
	FVector2D StartScreenOffset = FVector2D::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DY|Forest Geometry")
	FVector2D EndScreenOffset = FVector2D::ZeroVector;

	/** Physical diameter at the A-end source depth. No default art size is implied. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DY|Forest Geometry", meta = (Units = "cm"))
	double DiameterWorld = 0.0;

	/** Normalized presentation progress, never seconds or puzzle thresholds. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DY|Forest Geometry")
	double GrowthBegin = 0.0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DY|Forest Geometry")
	double GrowthEnd = 1.0;
};

UENUM(BlueprintType)
enum class EDYForestGeometryStatus : uint8
{
	InvalidContactGeometry,
	InvalidLayout,
	InvalidMeshBounds,
	InvalidProgress,
	OutsideScreen,
	InvalidComputedGeometry,
	Valid
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYForestBranchGeometry
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	bool bVisible = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	double Portion = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	FVector StartWorld = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	FVector EndWorld = FVector::ZeroVector;

	/** Transform of the mesh component, not its owner Actor. Undefined for hidden branches. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	FTransform MeshWorldTransform = FTransform::Identity;

	/** Conservative projection of eight local-bounds corners. NOT shadow pixels/occlusion. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	FVector2D ProjectedMin = FVector2D::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	FVector2D ProjectedMax = FVector2D::ZeroVector;
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYForestGeometrySample
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	EDYForestGeometryStatus Status = EDYForestGeometryStatus::InvalidContactGeometry;

	/** Diagnostic identity copy only; this library cannot establish that a token is current. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	FGuid ContactToken;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	FVector PhysicalRoot = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	FVector ShadowRoot = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Forest Geometry")
	TArray<FDYForestBranchGeometry> Branches;
};

/** Stateless geometry. No actors, clock, assets, mutable state, or gameplay authority. */
UCLASS()
class DENGYINGSHANHAI_API UDYForestGeometryLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintPure, Category = "DY|Forest Geometry")
	static bool IsForestLayoutValid(const TArray<FDYForestBranchDefinition>& Definition);

	/** Caller must separately authorize the current contact/token before applying any output.
	 * Finite progress clamps to [0,1]. Failure returns no partial/visible geometry.
	 * Mesh must use local Z as its growth axis; bounds must come from the actual mesh.
	 */
	UFUNCTION(BlueprintPure, Category = "DY|Forest Geometry")
	static FDYForestGeometrySample SampleForestGeometry(const FDYStaffContactPresentationSnapshot& Contact,
		const TArray<FDYForestBranchDefinition>& Definition, double NormalizedGrowth,
		const FVector& MeshLocalMin, const FVector& MeshLocalMax);
};
