#pragma once

#include "CoreMinimal.h"
#include "DYPuzzleTypes.generated.h"

UENUM(BlueprintType)
enum class EDYPuzzleRuntimeState : uint8
{
	Inactive,
	Searching,
	Holding,
	Resolved
};

UENUM(BlueprintType)
enum class EDYPuzzleFeedbackState : uint8
{
	InvalidSample,
	Far,
	Near,
	InsideTarget,
	Holding,
	Resolved
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYTargetRange
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle")
	bool bEnabled = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	double Target = 0.5;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	double EnterTolerance = 0.05;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	double ExitTolerance = 0.08;
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYPuzzleSample
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	bool bIsValid = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	double LightPosition = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	double PuppetPosition = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	FName PuppetPoseId = NAME_None;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle", meta = (Units = "s"))
	double SampleTimeSeconds = 0.0;
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYParameterEvaluation
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	bool bEnabled = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	bool bIsValid = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	double Current = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	double Target = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	double AbsoluteError = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	double EnterTolerance = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	double ExitTolerance = 0.0;
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYEvaluationResult
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	EDYPuzzleRuntimeState State = EDYPuzzleRuntimeState::Inactive;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	EDYPuzzleFeedbackState Feedback = EDYPuzzleFeedbackState::InvalidSample;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	FDYParameterEvaluation LightPosition;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	FDYParameterEvaluation PuppetPosition;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	bool bPuppetPoseEnabled = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	bool bPuppetPoseValid = true;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	FName CurrentPuppetPoseId = NAME_None;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	FName RequiredPuppetPoseId = NAME_None;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	double Progress = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle", meta = (Units = "s"))
	double HoldElapsedSeconds = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle", meta = (Units = "s"))
	double HoldRequiredSeconds = 0.0;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	bool bAllRequiredConditionsValid = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	bool bHoldStarted = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	bool bHoldCanceled = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	bool bJustResolved = false;

	UPROPERTY(BlueprintReadOnly, Category = "DY|Puzzle")
	int32 ResolveCount = 0;
};
