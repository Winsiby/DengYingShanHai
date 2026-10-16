#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Puzzles/DYPuzzleTypes.h"
#include "DYPuzzleEvaluatorComponent.generated.h"

class UDYPuzzleDefinition;

UCLASS(ClassGroup = (DY), meta = (BlueprintSpawnableComponent))
class DENGYINGSHANHAI_API UDYPuzzleEvaluatorComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UDYPuzzleEvaluatorComponent();

	UFUNCTION(BlueprintCallable, Category = "DY|Puzzle")
	FDYEvaluationResult Evaluate(const FDYPuzzleSample& Sample, const UDYPuzzleDefinition* Definition, double DeltaSeconds);

	UFUNCTION(BlueprintCallable, Category = "DY|Puzzle")
	void ResetEvaluation();

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle")
	FDYEvaluationResult GetLastResult() const { return LastResult; }

private:
	static FDYParameterEvaluation EvaluateParameter(
		double Current,
		const FDYTargetRange& TargetRange,
		bool& bWasValid);

	FDYEvaluationResult LastResult;
	bool bLightPositionWasValid = false;
	bool bPuppetPositionWasValid = false;
	bool bResolved = false;
	int32 ResolveCount = 0;
};
