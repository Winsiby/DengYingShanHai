#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Stage/DYStaffPresentationTypes.h"
#include "DYStaffContactLibrary.generated.h"

/** Stateless presentation geometry; no World, Director, evaluator or rendering reads. */
UCLASS()
class DENGYINGSHANHAI_API UDYStaffContactLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintPure, Category = "DY|Staff Presentation")
	static FDYNarrativeGroundLineSnapshot CaptureNarrativeGroundLine(
		const FDYStaffProjectionCapture& Projection, const FVector& WorldAnchor);

	/** A = local -Z. Numerical round-trip epsilon only, not a puzzle tolerance. */
	UFUNCTION(BlueprintPure, Category = "DY|Staff Presentation")
	static bool IsStaffAOnNarrativeGround(const FDYStaffProjectionCapture& Projection,
		const FDYNarrativeGroundLineSnapshot& GroundLine);
};
