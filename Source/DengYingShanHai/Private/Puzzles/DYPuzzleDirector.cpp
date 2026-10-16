#include "Puzzles/DYPuzzleDirector.h"

#include "DengYingShanHai.h"
#include "DrawDebugHelpers.h"
#include "Engine/Engine.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Puzzles/DYPuzzleDefinition.h"
#include "Puzzles/DYPuzzleEvaluatorComponent.h"
#include "TimerManager.h"
#include "Stage/DYStagePresentation.h"

namespace DYPuzzleDebug
{
	constexpr uint64 MessageKey = 0x44594D31;

	const TCHAR* StateToString(const EDYPuzzleRuntimeState State)
	{
		switch (State)
		{
		case EDYPuzzleRuntimeState::Inactive: return TEXT("Inactive");
		case EDYPuzzleRuntimeState::Searching: return TEXT("Searching");
		case EDYPuzzleRuntimeState::Holding: return TEXT("Holding");
		case EDYPuzzleRuntimeState::Resolved: return TEXT("Resolved");
		default: return TEXT("Unknown");
		}
	}
}

ADYPuzzleDirector::ADYPuzzleDirector()
{
	PrimaryActorTick.bCanEverTick = false;
	Evaluator = CreateDefaultSubobject<UDYPuzzleEvaluatorComponent>(TEXT("PuzzleEvaluator"));
}

void ADYPuzzleDirector::BeginPlay()
{
	Super::BeginPlay();
	bShowDevelopmentDebug = bShowDevelopmentDebug || FParse::Param(FCommandLine::Get(), TEXT("DYDebug"));
	if (LightRig)
	{
		LightRig->OnResetRequested.AddUniqueDynamic(this, &ADYPuzzleDirector::HandleControlResetRequested);
	}
	if (PuppetActor)
	{
		PuppetActor->OnResetRequested.AddUniqueDynamic(this, &ADYPuzzleDirector::HandleControlResetRequested);
	}
	if (bAutoStartOnBeginPlay || !IsActSequenceEnabled())
	{
		StartCurrentPuzzle();
	}
	else
	{
		// Title means genuinely inactive, not a running puzzle behind an overlay.
		if (LightRig) { IDYControllable::Execute_SetControlEnabled(LightRig, false); }
		if (PuppetActor) { IDYControllable::Execute_SetControlEnabled(PuppetActor, false); }
	}
}

bool ADYPuzzleDirector::CanStartManualSequence(const ADYStagePresentation* Requester) const
{
	return !bEndingPlay && IsValid(this) && HasActorBegunPlay() && !bAcceptingManualStart
		&& !bAutoStartOnBeginPlay && IsActSequenceEnabled() && ValidateActSequence()
		&& CurrentActIndex == INDEX_NONE && SequencePhase == EDYActSequencePhase::Inactive
		&& IsValid(Requester) && Requester->GetWorld() == GetWorld()
		&& SequencePresentation.Get() == Requester && AreSequenceActorsReady();
}

bool ADYPuzzleDirector::StartManualSequence(ADYStagePresentation* Requester)
{
	if (!CanStartManualSequence(Requester)) { return false; }
	TGuardValue<bool> StartGuard(bAcceptingManualStart, true);
	StartCurrentPuzzle();
	return !bEndingPlay && IsValid(this) && ActivationToken.IsValid()
		&& SequencePresentation.Get() == Requester && CurrentActIndex == 0
		&& SequencePhase != EDYActSequencePhase::Inactive;
}

void ADYPuzzleDirector::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	bEndingPlay = true; // A teardown observer cannot start or resolve a new activation.
	InvalidateResolvedSnapshot();
	SequencePresentation.Reset();
	if (UWorld* World = GetWorld()) { World->GetTimerManager().ClearTimer(SequenceActivationTimerHandle); }
	bSequenceActivationDeferred = false;
	StopEvaluation();
	if (LightRig)
	{
		LightRig->OnResetRequested.RemoveDynamic(this, &ADYPuzzleDirector::HandleControlResetRequested);
	}
	if (PuppetActor)
	{
		PuppetActor->OnResetRequested.RemoveDynamic(this, &ADYPuzzleDirector::HandleControlResetRequested);
	}
#if !UE_BUILD_SHIPPING
	if (GEngine)
	{
		GEngine->RemoveOnScreenDebugMessage(DYPuzzleDebug::MessageKey);
	}
#endif
	Super::EndPlay(EndPlayReason);
}

void ADYPuzzleDirector::StartCurrentPuzzle()
{
	if (bEndingPlay || !IsValid(this)) { return; }
	if (!bAutoStartOnBeginPlay && IsActSequenceEnabled()
		&& CurrentActIndex == INDEX_NONE && !bAcceptingManualStart) { return; }
	if (IsActSequenceEnabled() && !AreSequenceActorsReady())
	{
		// Sequence entry moves both actors. Wait for their own BeginPlay rail setup;
		// authored Actor order must not cause a second .15 offset/shifted rail centre.
		if (!bSequenceActivationDeferred && GetWorld())
		{
			bSequenceActivationDeferred = true;
			SequenceActivationTimerHandle = GetWorld()->GetTimerManager().SetTimerForNextTick(
				FTimerDelegate::CreateWeakLambda(this, [this]()
				{
					bSequenceActivationDeferred = false;
					if (bEndingPlay || !IsValid(this)) { return; }
					if (!AreSequenceActorsReady())
					{
						UE_LOG(LogDengYingShanHai, Error, TEXT("Three-act Director dependencies did not finish BeginPlay; activation remains inactive."));
						return; // One deferred attempt, not a world polling loop.
					}
					StartCurrentPuzzle();
				}));
		}
		return;
	}
	if (bSequenceActivationDeferred)
	{
		if (UWorld* World = GetWorld()) { World->GetTimerManager().ClearTimer(SequenceActivationTimerHandle); }
		bSequenceActivationDeferred = false; // An explicit ready start supersedes the pending first start.
	}
	const uint64 Operation = InvalidateResolvedSnapshot();
	if (bEndingPlay || !IsValid(this) || Operation != InvalidationSerial) { return; }
	StopEvaluation();
	Evaluator->ResetEvaluation();
	LastEvaluationTimeSeconds = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	if (IsActSequenceEnabled())
	{
		if (!ValidateActSequence())
		{
			UE_LOG(LogDengYingShanHai, Error, TEXT("Director %s requires three explicit, distinct act definitions and titles."), *GetNameSafe(this));
			return;
		}
		if (CurrentActIndex == INDEX_NONE) { CurrentActIndex = 0; }
		if (!ActSequence.IsValidIndex(CurrentActIndex)) { return; }
		PuzzleDefinition = ActSequence[CurrentActIndex].Definition;
	}

	if (!LightRig || !PuzzleDefinition || (CurrentPuzzleRequiresPuppet() && !PuppetActor))
	{
		UE_LOG(
			LogDengYingShanHai,
			Error,
			TEXT("Puzzle Director %s is missing an explicit required reference (LightRig, PuzzleDefinition, or PuppetActor)."),
			*GetNameSafe(this));
		return;
	}

	ActivationToken = FGuid::NewGuid();
	const FGuid StartedToken = ActivationToken;
	if (IsActSequenceEnabled())
	{
		// Approved Dev entry baseline. Reset existing components; never rewrite targets.
		if (LightRig->GetLightControlComponent()) { LightRig->GetLightControlComponent()->ResetToInitialValue(); }
		if (bEndingPlay || Operation != InvalidationSerial || ActivationToken != StartedToken) { return; }
		if (PuppetActor && PuppetActor->GetPuppetControlComponent()) { PuppetActor->GetPuppetControlComponent()->ResetToInitialValue(); }
		if (bEndingPlay || Operation != InvalidationSerial || ActivationToken != StartedToken) { return; }
		SetSequencePhase(EDYActSequencePhase::Playing);
		if (bEndingPlay || Operation != InvalidationSerial || ActivationToken != StartedToken) { return; }
	}
	IDYControllable::Execute_SetControlEnabled(LightRig, true);
	if (bEndingPlay || ActivationToken != StartedToken) { return; }
	if (PuppetActor)
	{
		IDYControllable::Execute_SetControlEnabled(PuppetActor, CurrentPuzzleRequiresPuppet());
		if (bEndingPlay || ActivationToken != StartedToken) { return; }
	}
	LightRig->ApplyResolvedDevFeedback(false);
	{
		TGuardValue<FGuid> NotificationScope(PuzzleNotificationToken, StartedToken);
		OnPuzzleActivated.Broadcast(PuzzleDefinition->PuzzleId);
	}
	if (bEndingPlay || ActivationToken != StartedToken
		|| (IsActSequenceEnabled() && SequencePhase != EDYActSequencePhase::Playing))
	{
		return; // A listener restarted the puzzle; do not schedule the old activation.
	}
	ScheduleEvaluation();
	EvaluatePuzzleNow();
}

void ADYPuzzleDirector::ResetCurrentPuzzle()
{
	if (bEndingPlay || !IsValid(this)) { return; }
	if (IsActSequenceEnabled())
	{
		// Start resets both entry values in sequence mode, without rewinding the act index.
		StartCurrentPuzzle();
		return;
	}
	// Invalidate before control-reset events can run an old presentation callback.
	const uint64 Operation = InvalidateResolvedSnapshot();
	if (bEndingPlay || !IsValid(this) || Operation != InvalidationSerial) { return; }
	if (LightRig && LightRig->GetLightControlComponent())
	{
		LightRig->GetLightControlComponent()->ResetToInitialValue();
		if (bEndingPlay || !IsValid(this) || Operation != InvalidationSerial) { return; }
	}
	if (PuppetActor && PuppetActor->GetPuppetControlComponent())
	{
		PuppetActor->GetPuppetControlComponent()->ResetToInitialValue();
		if (bEndingPlay || !IsValid(this) || Operation != InvalidationSerial) { return; }
	}
	StartCurrentPuzzle();
	UE_LOG(LogDengYingShanHai, Display, TEXT("Puzzle %s reset to its authored Dev baseline."), *GetCurrentPuzzleId().ToString());
}

void ADYPuzzleDirector::EvaluatePuzzleNow()
{
	UWorld* World = GetWorld();
	if (bEndingPlay || !IsValid(this) || !World || !LightRig || !PuzzleDefinition || !LightRig->GetLightControlComponent()
		|| (IsActSequenceEnabled() && SequencePhase != EDYActSequencePhase::Playing)
		|| (CurrentPuzzleRequiresPuppet() && (!PuppetActor || !PuppetActor->GetPuppetControlComponent())))
	{
		return;
	}

	const FGuid EvaluationToken = ActivationToken;
	TGuardValue<FGuid> NotificationScope(PuzzleNotificationToken, EvaluationToken);
	const double NowSeconds = World->GetTimeSeconds();
	// Never award an artificial first sample. Holding time is accumulated from
	// actual world time, so changing 10/15/20 Hz affects responsiveness only.
	const double DeltaSeconds = FMath::Max(0.0, NowSeconds - LastEvaluationTimeSeconds);
	LastEvaluationTimeSeconds = NowSeconds;

	FDYPuzzleSample Sample;
	Sample.bIsValid = true;
	Sample.LightPosition = LightRig->GetLightControlComponent()->GetNormalizedValue();
	if (CurrentPuzzleRequiresPuppet())
	{
		Sample.PuppetPosition = PuppetActor->GetPuppetControlComponent()->GetNormalizedValue();
		Sample.PuppetPoseId = PuppetActor->GetPoseId();
	}
	Sample.SampleTimeSeconds = NowSeconds;

	const FDYEvaluationResult Result = Evaluator->Evaluate(Sample, PuzzleDefinition, DeltaSeconds);
	OnEvaluationUpdated.Broadcast(Result);
	if (ActivationToken != EvaluationToken)
	{
		return;
	}
	if (Result.bHoldStarted)
	{
		OnHoldStarted.Broadcast(PuzzleDefinition->PuzzleId);
		if (ActivationToken != EvaluationToken) { return; }
	}
	if (Result.bHoldCanceled)
	{
		OnHoldCanceled.Broadcast(PuzzleDefinition->PuzzleId);
		if (ActivationToken != EvaluationToken) { return; }
	}
	if (Result.bJustResolved)
	{
		IDYControllable::Execute_SetControlEnabled(LightRig, false);
		if (bEndingPlay || ActivationToken != EvaluationToken) { return; }
		if (PuppetActor)
		{
			IDYControllable::Execute_SetControlEnabled(PuppetActor, false);
			if (bEndingPlay || ActivationToken != EvaluationToken) { return; }
		}
		LightRig->ApplyResolvedDevFeedback(true);
		CaptureResolvedSnapshot(Result);
		if (ActivationToken != EvaluationToken) { return; }
		// Stop before notifying: a listener may activate a new puzzle/timer.
		StopEvaluation();
		// The whole notification stack must retain this act and snapshot. Presentation
		// callbacks cannot advance synchronously even with a valid resolved identity.
		TGuardValue<bool> ResolveGuard(bBroadcastingResolve, true);
		if (IsActSequenceEnabled())
		{
			SetSequencePhase(IsFinalSequenceAct() ? EDYActSequencePhase::AwaitingFinale : EDYActSequencePhase::AwaitingTransition);
			if (bEndingPlay || ActivationToken != EvaluationToken) { return; }
		}
		OnPuzzleResolved.Broadcast(PuzzleDefinition->PuzzleId, Result);
		if (ActivationToken != EvaluationToken) { return; }
		UE_LOG(LogDengYingShanHai, Display, TEXT("Puzzle %s resolved exactly once."), *PuzzleDefinition->PuzzleId.ToString());
	}

	UpdateDevelopmentDebug(Result);
}

FDYEvaluationResult ADYPuzzleDirector::GetLastEvaluation() const
{
	return Evaluator->GetLastResult();
}

FDYResolvedPuzzleSnapshot ADYPuzzleDirector::GetResolvedPuzzleSnapshot() const
{
	return IsResolvedTokenCurrent(ResolvedSnapshot.Token)
		? ResolvedSnapshot : FDYResolvedPuzzleSnapshot();
}

bool ADYPuzzleDirector::IsResolvedTokenCurrent(const FGuid& Token) const
{
	return !bEndingPlay && IsValid(this) && Token.IsValid()
		&& Token == ActivationToken
		&& ResolvedSnapshot.bIsResolved
		&& Token == ResolvedSnapshot.Token
		&& ResolvedSnapshot.PuzzleId == GetCurrentPuzzleId()
		&& Evaluator && Evaluator->GetLastResult().State == EDYPuzzleRuntimeState::Resolved;
}

uint64 ADYPuzzleDirector::InvalidateResolvedSnapshot()
{
	const FGuid PreviousToken = ResolvedSnapshot.Token;
	const uint64 Operation = ++InvalidationSerial;
	SequencePhase = EDYActSequencePhase::Inactive; // Revoke callback permission before listeners.
	ActivationToken.Invalidate();
	ResolvedSnapshot = FDYResolvedPuzzleSnapshot();
	if (PreviousToken.IsValid()) { ResolvedSnapshotInvalidated.Broadcast(PreviousToken); }
	return Operation; // Listener reentry increments the serial; callers then abandon old work.
}

void ADYPuzzleDirector::CaptureResolvedSnapshot(const FDYEvaluationResult& Result)
{
	if (!Result.bJustResolved || !ActivationToken.IsValid() || ResolvedSnapshot.bIsResolved)
	{
		return;
	}
	FDYResolvedPuzzleSnapshot Captured;
	Captured.bIsResolved = true;
	Captured.PuzzleId = GetCurrentPuzzleId();
	Captured.Token = ActivationToken;
	Captured.Evaluation = Result;
	if (IsValid(LightRig))
	{
		Captured.Light = IDYControllable::Execute_GetControlSnapshot(LightRig);
	}
	if (IsValid(PuppetActor))
	{
		Captured.Puppet = IDYControllable::Execute_GetControlSnapshot(PuppetActor);
	}
	if (Captured.Token == ActivationToken)
	{
		ResolvedSnapshot = Captured;
	}
}

void ADYPuzzleDirector::ScheduleEvaluation()
{
	if (UWorld* World = GetWorld())
	{
		const double Interval = 1.0 / FMath::Max(EvaluationFrequencyHz, 1.0);
		World->GetTimerManager().SetTimer(
			EvaluationTimerHandle,
			this,
			&ADYPuzzleDirector::EvaluatePuzzleNow,
			Interval,
			true);
	}
}

void ADYPuzzleDirector::StopEvaluation()
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(EvaluationTimerHandle);
	}
}

void ADYPuzzleDirector::UpdateDevelopmentDebug(const FDYEvaluationResult& Result)
{
#if !UE_BUILD_SHIPPING
	if (!bShowDevelopmentDebug || !GEngine || !PuzzleDefinition)
	{
		return;
	}

	const double NowSeconds = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	if (!Result.bJustResolved
		&& NowSeconds - LastDevelopmentDebugTimeSeconds < DevelopmentDebugRefreshIntervalSeconds)
	{
		return;
	}
	LastDevelopmentDebugTimeSeconds = NowSeconds;

	const FString Message = FString::Printf(
		TEXT("DY DEV | E: control/exit | A/D: selected object axis | R: reset puzzle\n")
		TEXT("Puzzle=%s State=%s ResolveCount=%d\n")
		TEXT("Light Current=%.3f Target=%.3f Enter=%.3f Exit=%.3f Valid=%s\n")
		TEXT("Puppet Current=%.3f Target=%.3f Pose=%s/%s Valid=%s\n")
		TEXT("Progress=%.2f Holding=%.2f/%.2f Hz=%.0f (accepted baseline)"),
		*PuzzleDefinition->PuzzleId.ToString(),
		DYPuzzleDebug::StateToString(Result.State),
		Result.ResolveCount,
		Result.LightPosition.Current,
		Result.LightPosition.Target,
		Result.LightPosition.EnterTolerance,
		Result.LightPosition.ExitTolerance,
		Result.LightPosition.bIsValid ? TEXT("true") : TEXT("false"),
		Result.PuppetPosition.Current,
		Result.PuppetPosition.Target,
		*Result.CurrentPuppetPoseId.ToString(),
		*Result.RequiredPuppetPoseId.ToString(),
		Result.PuppetPosition.bIsValid && Result.bPuppetPoseValid ? TEXT("true") : TEXT("false"),
		Result.Progress,
		Result.HoldElapsedSeconds,
		Result.HoldRequiredSeconds,
		EvaluationFrequencyHz);
	GEngine->AddOnScreenDebugMessage(
		DYPuzzleDebug::MessageKey,
		FMath::Max(0.5f, static_cast<float>(DevelopmentDebugRefreshIntervalSeconds * 1.5)),
		Result.State == EDYPuzzleRuntimeState::Resolved ? FColor::Green : FColor::Cyan,
		Message);

	if (LightRig && LightRig->GetLightControlComponent())
	{
		FVector RailStart;
		FVector RailEnd;
		LightRig->GetLightControlComponent()->GetRailWorldEndpoints(RailStart, RailEnd);
		const float DebugLifetime = FMath::Max(0.3f, static_cast<float>(DevelopmentDebugRefreshIntervalSeconds * 1.5));
		DrawDebugLine(GetWorld(), RailStart, RailEnd, FColor::Cyan, false, DebugLifetime, 0, 4.0f);
		const FVector TargetLocation = LightRig->GetLightControlComponent()->GetWorldLocationForNormalizedValue(PuzzleDefinition->LightPosition.Target);
		DrawDebugSphere(GetWorld(), TargetLocation, 24.0f, 16, FColor::Green, false, DebugLifetime, 0, 2.0f);
	}
	if (CurrentPuzzleRequiresPuppet() && PuppetActor && PuppetActor->GetPuppetControlComponent())
	{
		FVector RailStart;
		FVector RailEnd;
		PuppetActor->GetPuppetControlComponent()->GetRailWorldEndpoints(RailStart, RailEnd);
		const float DebugLifetime = FMath::Max(0.3f, static_cast<float>(DevelopmentDebugRefreshIntervalSeconds * 1.5));
		DrawDebugLine(GetWorld(), RailStart, RailEnd, FColor::Magenta, false, DebugLifetime, 0, 4.0f);
		const FVector TargetLocation = PuppetActor->GetPuppetControlComponent()->GetWorldLocationForNormalizedValue(PuzzleDefinition->PuppetPosition.Target);
		DrawDebugSphere(GetWorld(), TargetLocation, 24.0f, 16, FColor::Magenta, false, DebugLifetime, 0, 2.0f);
	}
#endif
}

FName ADYPuzzleDirector::GetCurrentPuzzleId() const
{
	return PuzzleDefinition ? PuzzleDefinition->PuzzleId : NAME_None;
}

bool ADYPuzzleDirector::CurrentPuzzleRequiresPuppet() const
{
	return PuzzleDefinition
		&& (PuzzleDefinition->PuppetPosition.bEnabled || !PuzzleDefinition->RequiredPuppetPoseId.IsNone());
}

void ADYPuzzleDirector::HandleControlResetRequested()
{
	ResetCurrentPuzzle();
}

bool ADYPuzzleDirector::ValidateActSequence() const
{
	if (ActSequence.Num() != 3) { return false; }
	TSet<FName> Ids;
	for (const auto& Entry : ActSequence)
	{
		if (!IsValid(Entry.Definition) || Entry.Definition->PuzzleId.IsNone() || Entry.ActTitle.IsEmpty()
			|| Ids.Contains(Entry.Definition->PuzzleId)) { return false; }
		Ids.Add(Entry.Definition->PuzzleId);
	}
	return true;
}

bool ADYPuzzleDirector::AreSequenceActorsReady() const
{
	return IsValid(LightRig) && LightRig->HasActorBegunPlay() && LightRig->GetLightControlComponent()
		&& IsValid(PuppetActor) && PuppetActor->HasActorBegunPlay() && PuppetActor->GetPuppetControlComponent();
}

bool ADYPuzzleDirector::IsFinalSequenceAct() const
{
	return IsActSequenceEnabled() && CurrentActIndex >= 0 && CurrentActIndex == ActSequence.Num() - 1;
}

FDYActSequenceSnapshot ADYPuzzleDirector::GetActSequenceSnapshot() const
{
	FDYActSequenceSnapshot Snapshot;
	Snapshot.bSequenceEnabled = IsActSequenceEnabled();
	if (!Snapshot.bSequenceEnabled) { return Snapshot; }
	Snapshot.ActIndex = CurrentActIndex;
	Snapshot.ActCount = ActSequence.Num();
	Snapshot.Phase = SequencePhase;
	if (ActSequence.IsValidIndex(CurrentActIndex)) { Snapshot.ActTitle = ActSequence[CurrentActIndex].ActTitle; }
	return Snapshot;
}

void ADYPuzzleDirector::SetSequencePhase(const EDYActSequencePhase NewPhase)
{
	SequencePhase = NewPhase;
	const FDYActSequenceSnapshot Snapshot = GetActSequenceSnapshot();
	ActSequenceChanged.Broadcast(Snapshot); // No writes after potentially reentrant listeners.
}

bool ADYPuzzleDirector::RegisterSequencePresentation(ADYStagePresentation* Presentation)
{
	if (bEndingPlay || !IsValid(Presentation) || Presentation->GetWorld() != GetWorld()) { return false; }
	if (SequencePresentation.IsValid() && SequencePresentation.Get() != Presentation) { return false; }
	SequencePresentation = Presentation;
	return true;
}

void ADYPuzzleDirector::UnregisterSequencePresentation(ADYStagePresentation* Presentation)
{
	if (SequencePresentation.Get() == Presentation) { SequencePresentation.Reset(); }
}

bool ADYPuzzleDirector::IsSequenceSubmissionCurrent(const ADYStagePresentation* Presentation,
	const FGuid& Token, const EDYActSequencePhase RequiredPhase) const
{
	return !bBroadcastingResolve && IsActSequenceEnabled() && IsValid(Presentation)
		&& Presentation == SequencePresentation.Get() && Presentation->GetWorld() == GetWorld()
		&& SequencePhase == RequiredPhase && IsResolvedTokenCurrent(Token);
}

bool ADYPuzzleDirector::AcceptActTransition(ADYStagePresentation* Presentation, const FGuid& Token)
{
	if (!IsSequenceSubmissionCurrent(Presentation, Token, EDYActSequencePhase::AwaitingTransition)
		|| IsFinalSequenceAct() || !ActSequence.IsValidIndex(CurrentActIndex + 1)) { return false; }
	const uint64 Operation = InvalidateResolvedSnapshot(); // Consume before notification.
	if (bEndingPlay || !IsValid(this) || Operation != InvalidationSerial || !IsValid(Presentation)
		|| SequencePresentation.Get() != Presentation || Presentation->GetWorld() != GetWorld()) { return false; }
	++CurrentActIndex;
	StartCurrentPuzzle();
	return true;
}

bool ADYPuzzleDirector::AcceptFinaleCompletion(ADYStagePresentation* Presentation, const FGuid& Token)
{
	// Only the registered native Presentation may submit its verified actual full forest.
	if (!IsFinalSequenceAct() || !IsSequenceSubmissionCurrent(Presentation, Token, EDYActSequencePhase::AwaitingFinale)) { return false; }
	SetSequencePhase(EDYActSequencePhase::Complete); // Consume once; preserve Token and resources.
	return true;
}
