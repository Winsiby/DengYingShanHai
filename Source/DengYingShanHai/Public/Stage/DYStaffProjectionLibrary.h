#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Interaction/DYStaffGeometryTypes.h"
#include "DYStaffProjectionLibrary.generated.h"

class ADYLightRigActor;
class ADYPuppetActor;
class UStaticMeshComponent;

UENUM(BlueprintType)
enum class EDYStaffProjectionStatus : uint8
{
	InvalidGeometry,
	ParallelRay,
	ScreenNotBeyondSource,
	OutsideScreen,
	OnScreen
};

/** Central-ray geometry only. OnScreen is NOT a puzzle success or a visibility test. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYStaffProjectionPoint
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	EDYStaffProjectionStatus Status = EDYStaffProjectionStatus::InvalidGeometry;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FVector WorldPosition = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FVector ScreenLocalPosition = FVector::ZeroVector;

	/** U increases along local +Y, V along local +Z (not texture-coordinate V). */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FVector2D ScreenUV = FVector2D::ZeroVector;

	/** Source is t=1 on the ray from the actual emitter. A receiver must have t>1. */
	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	double RayParameter = 0.0;
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYStaffProjectionCapture
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	bool bHasGeometry = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FVector EmitterWorld = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FDYStaffGeometrySnapshot Staff;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FTransform ScreenTransform = FTransform::Identity;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FVector ScreenLocalMin = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FVector ScreenLocalMax = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FDYStaffProjectionPoint EndA;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Projection")
	FDYStaffProjectionPoint EndB;
};

/** Planar cube-screen adapter for the Dev fixture; no Director/Evaluator dependency. */
UCLASS()
class DENGYINGSHANHAI_API UDYStaffProjectionLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintPure, Category = "DY|Projection")
	static FDYStaffProjectionPoint ProjectPointToScreen(const FVector& EmitterWorld,
		const FVector& SourceWorld, const FTransform& ScreenTransform,
		const FVector& LocalMin, const FVector& LocalMax);

	UFUNCTION(BlueprintPure, Category = "DY|Projection")
	static FDYStaffProjectionCapture CaptureStaffProjection(const ADYLightRigActor* Light,
		const ADYPuppetActor* Puppet, const UStaticMeshComponent* Screen);
};
