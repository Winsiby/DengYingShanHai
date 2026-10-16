#include "Puzzles/DYPuzzleEvaluatorComponent.h"

#include "Puzzles/DYPuzzleDefinition.h"

UDYPuzzleEvaluatorComponent::UDYPuzzleEvaluatorComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	ResetEvaluation();
}

FDYEvaluationResult UDYPuzzleEvaluatorComponent::Evaluate(
	const FDYPuzzleSample& Sample,
	const UDYPuzzleDefinition* Definition,
	const double DeltaSeconds)
{
	FDYEvaluationResult Result = LastResult;
	Result.bHoldStarted = false;
	Result.bHoldCanceled = false;
	Result.bJustResolved = false;

	if (!Definition || !Sample.bIsValid)
	{
		Result.bHoldCanceled = Result.State == EDYPuzzleRuntimeState::Holding;
		Result.State = EDYPuzzleRuntimeState::Searching;
		Result.Feedback = EDYPuzzleFeedbackState::InvalidSample;
		Result.HoldElapsedSeconds = 0.0;
		Result.HoldRequiredSeconds = Definition ? FMath::Max(0.0, Definition->RequiredHoldSeconds) : 0.0;
		Result.bAllRequiredConditionsValid = false;
		Result.LightPosition = FDYParameterEvaluation();
		Result.PuppetPosition = FDYParameterEvaluation();
		Result.bPuppetPoseEnabled = false;
		Result.bPuppetPoseValid = false;
		Result.CurrentPuppetPoseId = NAME_None;
		Result.RequiredPuppetPoseId = NAME_None;
		bLightPositionWasValid = false;
		bPuppetPositionWasValid = false;
		LastResult = Result;
		return LastResult;
	}

	Result.LightPosition = EvaluateParameter(
		Sample.LightPosition,
		Definition->LightPosition,
		bLightPositionWasValid);
	Result.PuppetPosition = EvaluateParameter(
		Sample.PuppetPosition,
		Definition->PuppetPosition,
		bPuppetPositionWasValid);
	Result.bPuppetPoseEnabled = !Definition->RequiredPuppetPoseId.IsNone();
	Result.CurrentPuppetPoseId = Sample.PuppetPoseId;
	Result.RequiredPuppetPoseId = Definition->RequiredPuppetPoseId;
	Result.bPuppetPoseValid = !Result.bPuppetPoseEnabled
		|| Sample.PuppetPoseId == Definition->RequiredPuppetPoseId;
	Result.HoldRequiredSeconds = FMath::Max(0.0, Definition->RequiredHoldSeconds);
	Result.bAllRequiredConditionsValid = Result.LightPosition.bIsValid
		&& Result.PuppetPosition.bIsValid
		&& Result.bPuppetPoseValid;

	double ProgressSum = 0.0;
	int32 ProgressConditionCount = 0;
	if (Definition->LightPosition.bEnabled)
	{
		ProgressSum += 1.0 - FMath::Clamp(Result.LightPosition.AbsoluteError, 0.0, 1.0);
		++ProgressConditionCount;
	}
	if (Definition->PuppetPosition.bEnabled)
	{
		ProgressSum += 1.0 - FMath::Clamp(Result.PuppetPosition.AbsoluteError, 0.0, 1.0);
		++ProgressConditionCount;
	}
	if (Result.bPuppetPoseEnabled)
	{
		ProgressSum += Result.bPuppetPoseValid ? 1.0 : 0.0;
		++ProgressConditionCount;
	}
	Result.Progress = ProgressConditionCount > 0
		? ProgressSum / static_cast<double>(ProgressConditionCount)
		: 1.0;

	if (bResolved)
	{
		Result.State = EDYPuzzleRuntimeState::Resolved;
		Result.Feedback = EDYPuzzleFeedbackState::Resolved;
		Result.ResolveCount = ResolveCount;
		LastResult = Result;
		return LastResult;
	}

	if (!Result.bAllRequiredConditionsValid)
	{
		Result.bHoldCanceled = Result.State == EDYPuzzleRuntimeState::Holding;
		Result.State = EDYPuzzleRuntimeState::Searching;
		Result.HoldElapsedSeconds = 0.0;
		const bool bLightNear = Definition->LightPosition.bEnabled
			&& Result.LightPosition.AbsoluteError <= FMath::Max(Definition->LightPosition.ExitTolerance * 2.0, 0.15);
		const bool bPuppetNear = Definition->PuppetPosition.bEnabled
			&& Result.PuppetPosition.AbsoluteError <= FMath::Max(Definition->PuppetPosition.ExitTolerance * 2.0, 0.15);
		const bool bPoseNear = Result.bPuppetPoseEnabled && Result.bPuppetPoseValid;
		Result.Feedback = bLightNear || bPuppetNear || bPoseNear
			? EDYPuzzleFeedbackState::Near
			: EDYPuzzleFeedbackState::Far;
		LastResult = Result;
		return LastResult;
	}

	Result.bHoldStarted = Result.State != EDYPuzzleRuntimeState::Holding;
	Result.State = EDYPuzzleRuntimeState::Holding;
	Result.Feedback = EDYPuzzleFeedbackState::Holding;
	Result.HoldElapsedSeconds += FMath::Max(0.0, DeltaSeconds);

	if (Result.HoldElapsedSeconds + UE_DOUBLE_SMALL_NUMBER >= Result.HoldRequiredSeconds)
	{
		bResolved = true;
		++ResolveCount;
		Result.State = EDYPuzzleRuntimeState::Resolved;
		Result.Feedback = EDYPuzzleFeedbackState::Resolved;
		Result.bJustResolved = true;
		Result.ResolveCount = ResolveCount;
	}

	LastResult = Result;
	return LastResult;
}

void UDYPuzzleEvaluatorComponent::ResetEvaluation()
{
	LastResult = FDYEvaluationResult();
	LastResult.State = EDYPuzzleRuntimeState::Searching;
	LastResult.Feedback = EDYPuzzleFeedbackState::InvalidSample;
	bLightPositionWasValid = false;
	bPuppetPositionWasValid = false;
	bResolved = false;
	ResolveCount = 0;
}

FDYParameterEvaluation UDYPuzzleEvaluatorComponent::EvaluateParameter(
	const double Current,
	const FDYTargetRange& TargetRange,
	bool& bWasValid)
{
	FDYParameterEvaluation Evaluation;
	Evaluation.bEnabled = TargetRange.bEnabled;
	Evaluation.Current = Current;
	Evaluation.Target = TargetRange.Target;
	Evaluation.EnterTolerance = FMath::Max(0.0, TargetRange.EnterTolerance);
	Evaluation.ExitTolerance = FMath::Max(Evaluation.EnterTolerance, TargetRange.ExitTolerance);
	Evaluation.AbsoluteError = FMath::Abs(Current - TargetRange.Target);

	if (!TargetRange.bEnabled)
	{
		Evaluation.bIsValid = true;
		return Evaluation;
	}

	const double ActiveTolerance = bWasValid
		? Evaluation.ExitTolerance
		: Evaluation.EnterTolerance;
	Evaluation.bIsValid = Evaluation.AbsoluteError <= ActiveTolerance + UE_DOUBLE_SMALL_NUMBER;
	bWasValid = Evaluation.bIsValid;
	return Evaluation;
}
