#include "Puzzles/DYPuzzleDirector.h"

#include "Puppets/DYPuppetPerformanceComponent.h"

#include "Core/DYEntryWalkTypes.h"
#include "Core/DYStageGameMode.h"
#include "DengYingShanHai.h"
#include "DrawDebugHelpers.h"
#include "Engine/Engine.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Interaction/DYInteractionComponent.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "HAL/FileManager.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/Parse.h"
#include "Puzzles/DYPuzzleDefinition.h"
#include "Puzzles/DYPuzzleEvaluatorComponent.h"
#include "TimerManager.h"
#include "Stage/DYStagePresentation.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/StaticMeshActor.h"
#include "EngineUtils.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UI/DYInteractionHUD.h"
#include "UI/DYInteractionHUDWidget.h"
#include "UObject/UObjectIterator.h"

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

FText ADYPuzzleDirector::MakeReachHint(const bool bLightInReach, const bool bPuppetRequired, const bool bPuppetInReach)
{
	if (bLightInReach && (!bPuppetRequired || bPuppetInReach)) { return FText::GetEmpty(); }
	if (!bPuppetRequired)
	{
		return NSLOCTEXT("DYPuzzleReach", "ReachLightOnly", "走近灯架，灯要够得到才推得动");
	}
	// One line for every both-parts state: whether the player is short of the lamp, the
	// puppet or both, the answer is the same standing zone between them.
	return NSLOCTEXT("DYPuzzleReach", "ReachBoth", "往灯与偶中间站，两件都够得到再动手");
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
	BindPuppetPerformance();
	if (bFourActCampaign)
	{
		BaseActSequence = ActSequence;
		EnsureCampaignChapters();
		ApplyChapterPalette();
	}

	// Verification-only harness: DY_CAMPAIGN_AUTOPLAY=1 drives the two control
	// values onto each act's authored targets so a packaged build can be walked
	// through all four chapters without a human at the keyboard. It never writes
	// the puzzle verdict itself; evaluation, hold timing, transitions and the
	// finale still run through their normal owners.
	const FString AutoPlayEnv = FPlatformMisc::GetEnvironmentVariable(TEXT("DY_CAMPAIGN_AUTOPLAY"));
	if (bFourActCampaign && !AutoPlayEnv.IsEmpty() && AutoPlayEnv != TEXT("0"))
	{
		bCampaignAutoPlay = true;
		if (UWorld* AutoPlayWorld = GetWorld())
		{
			AutoPlayWorld->GetTimerManager().SetTimer(CampaignAutoPlayHandle, this,
				&ADYPuzzleDirector::HandleCampaignAutoPlayTick, 0.2, true);
		}
		UE_LOG(LogDengYingShanHai, Display, TEXT("Campaign autoplay harness enabled (DY_CAMPAIGN_AUTOPLAY)."));
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
	if (UDYPuppetPerformanceComponent* Performance = BoundPerformanceComponent.Get())
	{
		Performance->OnPerformanceFinished.RemoveAll(this);
		Performance->CancelPlayback();
		BoundPerformanceComponent.Reset();
	}
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
	// A new activation supersedes any still-pending resolution notification; a show left
	// over from the previous chapter must not keep the mesh.
	bResolveNotificationDeferred = false;
	DeferredResolveToken.Invalidate();
	LastFeedbackBand = 0;
	if (UDYPuppetPerformanceComponent* RunningShow = PuppetActor ? PuppetActor->GetPerformanceComponent() : nullptr)
	{
		RunningShow->CancelPlayback();
	}
	BindPuppetPerformance();
	Evaluator->ResetEvaluation();
	LastEvaluationTimeSeconds = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	if (PuppetActor)
	{
		// Chapter appearance is presentation only; the control rail and judgement stay unchanged.
		PuppetActor->ApplyChapterFigure(FMath::Max(0, CurrentChapterIndex), true);
	}
	ApplyChapterTitlePlaque(FMath::Max(0, CurrentChapterIndex));
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
		OutOfReachSeconds = 0.0;
		bReachHintShownThisAct = false;
		const bool bCarryEntry = bCarryEntryValuesOnNextStart && bCarryControlValuesAcrossActs
			&& bFourActCampaign && ActSequence.IsValidIndex(CurrentActIndex - 1);
		bCarryEntryValuesOnNextStart = false;
		// Carrying the previous act's settled Target (not wherever the player released) keeps the
		// stage continuous without letting two neighbouring windows overlap into a free pass.
		const UDYPuzzleDefinition* PreviousDefinition = nullptr;
		if (bCarryEntry) { PreviousDefinition = ActSequence[CurrentActIndex - 1].Definition.Get(); }
		if (LightRig->GetLightControlComponent())
		{
			if (PreviousDefinition && PreviousDefinition->LightPosition.bEnabled)
			{
				LightRig->GetLightControlComponent()->SetNormalizedValue(PreviousDefinition->LightPosition.Target);
			}
			else
			{
				LightRig->GetLightControlComponent()->ResetToInitialValue();
			}
		}
		if (bEndingPlay || Operation != InvalidationSerial || ActivationToken != StartedToken) { return; }
		if (PuppetActor && PuppetActor->GetPuppetControlComponent())
		{
			if (PreviousDefinition && PreviousDefinition->PuppetPosition.bEnabled)
			{
				PuppetActor->GetPuppetControlComponent()->SetNormalizedValue(PreviousDefinition->PuppetPosition.Target);
			}
			else
			{
				PuppetActor->GetPuppetControlComponent()->ResetToInitialValue();
			}
		}
		ProbeCarriedEntryValues(bCarryEntry);
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
	ApplyChapterPalette();
	ScheduleEvaluation();
	EvaluatePuzzleNow();
}

void ADYPuzzleDirector::ResetCurrentPuzzle()
{
	if (bEndingPlay || !IsValid(this)) { return; }
	if (IsActSequenceEnabled())
	{
		// Start resets both entry values in sequence mode, without rewinding the act index.
		bCarryEntryValuesOnNextStart = false;
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

void ADYPuzzleDirector::ApplyChapterTitlePlaque(const int32 ChapterIndex)
{
	if (!TitleGlyphActor.IsValid())
	{
		if (UWorld* World = GetWorld())
		{
			for (TActorIterator<AActor> It(World); It; ++It)
			{
				if (It->ActorHasTag(TEXT("ART_ZhuRiTitleGlyph")))
				{
					TitleGlyphActor = *It;
					break;
				}
			}
		}
	}
	AActor* Plaque = TitleGlyphActor.Get();
	if (!IsValid(Plaque))
	{
		return;
	}

	static const TCHAR* ShippedInstances[] = {
		TEXT("/Game/DengYingShanHai/Stage/ArtMainline/Materials/MI_DY_TitleGlyph_Act1.MI_DY_TitleGlyph_Act1"),
		TEXT("/Game/DengYingShanHai/Stage/ArtMainline/Materials/MI_DY_TitleGlyph_Act2.MI_DY_TitleGlyph_Act2"),
		TEXT("/Game/DengYingShanHai/Stage/ArtMainline/Materials/MI_DY_TitleGlyph_Act3.MI_DY_TitleGlyph_Act3"),
		TEXT("/Game/DengYingShanHai/Stage/ArtMainline/Materials/MI_DY_TitleGlyph_Act4.MI_DY_TitleGlyph_Act4"),
	};
	const int32 Index = FMath::Clamp(ChapterIndex, 0, UE_ARRAY_COUNT(ShippedInstances) - 1);
	UMaterialInterface* Desired = nullptr;
	if (ChapterTitleMaterials.IsValidIndex(Index) && !ChapterTitleMaterials[Index].IsNull())
	{
		Desired = ChapterTitleMaterials[Index].LoadSynchronous();
	}
	if (!Desired)
	{
		Desired = LoadObject<UMaterialInterface>(nullptr, ShippedInstances[Index]);
	}
	if (!Desired)
	{
		return;
	}

	TArray<UStaticMeshComponent*> Meshes;
	Plaque->GetComponents(Meshes);
	for (UStaticMeshComponent* Mesh : Meshes)
	{
		if (IsValid(Mesh))
		{
			Mesh->SetMaterial(0, Desired);
		}
	}
}

void ADYPuzzleDirector::BindPuppetPerformance()
{
	UDYPuppetPerformanceComponent* Performance = PuppetActor ? PuppetActor->GetPerformanceComponent() : nullptr;
	if (!Performance || BoundPerformanceComponent.Get() == Performance) { return; }

	if (UDYPuppetPerformanceComponent* Previous = BoundPerformanceComponent.Get())
	{
		Previous->OnPerformanceFinished.RemoveAll(this);
	}
	Performance->OnPerformanceFinished.AddUObject(this, &ADYPuzzleDirector::HandlePuppetPerformanceFinished);
	BoundPerformanceComponent = Performance;
}

void ADYPuzzleDirector::HandlePuppetPerformanceFinished(int32 ChapterIndex, bool bSkipped)
{
	if (!bResolveNotificationDeferred) { return; }
	if (ChapterIndex != FMath::Max(0, CurrentChapterIndex)) { return; }
	PublishResolvedSequence();

	// Campaign Act 1 ends on 弃杖化林: after the fall, grow the authored forest on the
	// receiver so the screen shows the forest instead of cutting to the next chapter.
	if (ChapterIndex == 0 && IsCampaignEnabled() && !bEndingPlay)
	{
		if (UWorld* World = GetWorld())
		{
			if (ADYStageGameMode* GameMode = World->GetAuthGameMode<ADYStageGameMode>())
			{
				if (ADYStagePresentation* Presentation = GameMode->GetPlayerStagePresentation())
				{
					Presentation->PlayCampaignForestFinale(2.6f);
				}
			}
		}
	}
}

void ADYPuzzleDirector::PublishResolvedSequence()
{
	if (!bResolveNotificationDeferred) { return; }

	const FGuid NotifiedToken = DeferredResolveToken;
	const bool bStillCurrent = !bEndingPlay && IsValid(this) && ActivationToken == NotifiedToken;
	bResolveNotificationDeferred = false;
	if (!bStillCurrent) { return; }

	const FName ResolvedPuzzleId = DeferredResolvePuzzleId;
	const FDYEvaluationResult Result = DeferredResolveResult;
	// The show defers this broadcast; re-scope the notification identity so presentation
	// listeners see the same current token they would have during EvaluatePuzzleNow.
	TGuardValue<FGuid> NotificationScope(PuzzleNotificationToken, NotifiedToken);
	TGuardValue<bool> ResolveGuard(bBroadcastingResolve, true);
	if (IsActSequenceEnabled())
	{
		ScheduleCampaignChapterFallback();
		if (bEndingPlay || ActivationToken != NotifiedToken) { return; }
	}
	OnPuzzleResolved.Broadcast(ResolvedPuzzleId, Result);
	if (ActivationToken != NotifiedToken) { return; }
	UE_LOG(LogDengYingShanHai, Display, TEXT("Puzzle %s resolved exactly once."), *ResolvedPuzzleId.ToString());
}

void ADYPuzzleDirector::TriggerProgressFeedback(double Progress)
{
	if (!PuppetActor) { return; }

	UDYPuppetPerformanceComponent* Performance = PuppetActor->GetPerformanceComponent();
	if (!Performance || Performance->IsPerforming()) { return; }

	// Coarse progress bands, not per-frame sampling: one reaction per band crossing.
	const int32 Band = Progress >= 0.85 ? 3 : Progress >= 0.6 ? 2 : Progress >= 0.35 ? 1 : 0;
	if (Band <= LastFeedbackBand) { return; }

	LastFeedbackBand = Band;
	Performance->TriggerFeedback(FMath::Max(0, CurrentChapterIndex));
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
	UpdateReachHint(DeltaSeconds);

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
	if (!Result.bJustResolved)
	{
		TriggerProgressFeedback(Result.Progress);
		if (ActivationToken != EvaluationToken) { return; }
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
		const FName ResolvedPuzzleId = PuzzleDefinition->PuzzleId;
		// The whole notification stack must retain this act and snapshot. Presentation
		// callbacks cannot advance synchronously even with a valid resolved identity.
		TGuardValue<bool> ResolveGuard(bBroadcastingResolve, true);
		if (IsActSequenceEnabled())
		{
			// The chapter outcome is final here; only its notification waits for the show.
			SetSequencePhase(IsFinalSequenceAct() ? EDYActSequencePhase::AwaitingFinale : EDYActSequencePhase::AwaitingTransition);
			if (bEndingPlay || ActivationToken != EvaluationToken) { return; }
		}
		// The continuous myth show belongs to the chapter finale only: earlier acts keep the
		// short joint reactions (progress bands) and advance exactly as before. The show owns
		// the puppet mesh for its authored beats; nothing downstream runs until it reports
		// finished, so a listener cannot advance mid-performance.
		const bool bChapterFinaleShow = IsActSequenceEnabled() && IsFinalSequenceAct();
		if (bChapterFinaleShow && PuppetActor && PuppetActor->GetPerformanceComponent()
			&& PuppetActor->GetPerformanceComponent()->StartChapterPerformance(FMath::Max(0, CurrentChapterIndex)))
		{
			bResolveNotificationDeferred = true;
			DeferredResolveResult = Result;
			DeferredResolvePuzzleId = ResolvedPuzzleId;
			DeferredResolveToken = EvaluationToken;
			UpdateDevelopmentDebug(Result);
			return;
		}
		if (IsActSequenceEnabled())
		{
			ScheduleCampaignChapterFallback();
			if (bEndingPlay || ActivationToken != EvaluationToken) { return; }
		}
		OnPuzzleResolved.Broadcast(ResolvedPuzzleId, Result);
		if (ActivationToken != EvaluationToken) { return; }
		UE_LOG(LogDengYingShanHai, Display, TEXT("Puzzle %s resolved exactly once."), *ResolvedPuzzleId.ToString());
	}

	UpdateDevelopmentDebug(Result);
}

void ADYPuzzleDirector::UpdateReachHint(const double DeltaSeconds)
{
	if (bReachHintShownThisAct || ReachHintDelaySeconds <= 0.0 || !LightRig) { return; }
	UWorld* World = GetWorld();
	APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
	APawn* Pawn = PC ? PC->GetPawn() : nullptr;
	// The act is already playing while the player walks the entry corridor, and the walk
	// guide owns the plaque until the doorway. Arm only inside the theater.
	if (!Pawn || Pawn->GetActorLocation().X <= DYEntryWalk::TheaterThresholdX)
	{
		OutOfReachSeconds = 0.0;
		return;
	}
	const UDYInteractionComponent* Interaction = Pawn->FindComponentByClass<UDYInteractionComponent>();
	if (!Interaction)
	{
		OutOfReachSeconds = 0.0;
		return;
	}
	const FVector PawnLocation = Pawn->GetActorLocation();
	const double Reach = Interaction->GetFocusDistance();
	const bool bLightInReach = UDYInteractionComponent::IsWithinFocusDistance(PawnLocation, LightRig->GetActorLocation(), Reach);
	const bool bPuppetRequired = CurrentPuzzleRequiresPuppet();
	const bool bPuppetInReach = bPuppetRequired && PuppetActor
		&& UDYInteractionComponent::IsWithinFocusDistance(PawnLocation, PuppetActor->GetActorLocation(), Reach);
	const FText Hint = MakeReachHint(bLightInReach, bPuppetRequired, bPuppetInReach);
	if (Hint.IsEmpty())
	{
		// Walking into range clears the clock: the line only marks a genuinely stuck start.
		OutOfReachSeconds = 0.0;
		return;
	}
	OutOfReachSeconds += FMath::Max(0.0, DeltaSeconds);
	if (OutOfReachSeconds < ReachHintDelaySeconds) { return; }
	bReachHintShownThisAct = true;
	PublishReachHint(Hint);
}

void ADYPuzzleDirector::PublishReachHint(const FText& Hint)
{
	UWorld* World = GetWorld();
	if (!World) { return; }
	if (APlayerController* PC = World->GetFirstPlayerController())
	{
		if (ADYInteractionHUD* Hud = Cast<ADYInteractionHUD>(PC->GetHUD()))
		{
			Hud->ShowTransientHint(Hint, static_cast<float>(ReachHintDurationSeconds));
			return;
		}
	}
	// The presentation HUD may be a Blueprint wrapper that owns the widget directly.
	for (TObjectIterator<UDYInteractionHUDWidget> It; It; ++It)
	{
		UDYInteractionHUDWidget* Candidate = *It;
		if (!IsValid(Candidate) || Candidate->GetWorld() != World) { continue; }
		Candidate->ShowHint(Hint, static_cast<float>(ReachHintDurationSeconds));
		return;
	}
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
	bResolveNotificationDeferred = false;
	DeferredResolveToken.Invalidate();
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
	Snapshot.ChapterCount = GetChapterCount();
	if (IsCampaignEnabled())
	{
		Snapshot.ChapterIndex = CurrentChapterIndex;
		if (Chapters.IsValidIndex(CurrentChapterIndex)) { Snapshot.ChapterTitle = Chapters[CurrentChapterIndex].ChapterTitle; }
	}
	if (ActSequence.IsValidIndex(CurrentActIndex)) { Snapshot.ActTitle = ActSequence[CurrentActIndex].ActTitle; }
	return Snapshot;
}

namespace DYCampaign
{
	struct FPalette
	{
		FLinearColor Horizon;
		FLinearColor Zenith;
		float SkyIntensity = 60.f;
		float FogDensity = 0.008f;
	};

	FPalette GetPalette(const int32 ChapterIndex, const int32 StepIndex)
	{
		switch (ChapterIndex)
		{
		case 1: // 精卫填海：海雨天青
			return { FLinearColor(0.05f, 0.26f, 0.32f), FLinearColor(0.02f, 0.10f, 0.22f), 66.f, 0.022f };
		case 2: // 刑天舞干戚：赤霞
			return { FLinearColor(0.36f, 0.12f, 0.07f), FLinearColor(0.14f, 0.04f, 0.04f), 58.f, 0.014f };
		case 3: // 烛龙昼夜：第一步仍是夜，但天光要够看见门厅和幕布。
			return StepIndex >= 1
				? FPalette{ FLinearColor(0.80f, 0.70f, 0.52f), FLinearColor(0.36f, 0.52f, 0.70f), 115.f, 0.004f }
				: FPalette{ FLinearColor(0.05f, 0.07f, 0.14f), FLinearColor(0.02f, 0.03f, 0.08f), 48.f, 0.010f };
		default: // 第一幕：沿用现有夜色
			return { FLinearColor(0.10f, 0.14f, 0.24f), FLinearColor(0.05f, 0.08f, 0.16f), 60.f, 0.008f };
		}
	}
}

const TArray<FText>& ADYPuzzleDirector::GetCampaignChapterTitles()
{
	static const TArray<FText> Titles = {
		FText::FromString(TEXT("第一幕 · 夸父逐日")),
		FText::FromString(TEXT("第二幕 · 精卫填海")),
		FText::FromString(TEXT("第三幕 · 刑天舞干戚")),
		FText::FromString(TEXT("第四幕 · 烛龙昼夜"))
	};
	return Titles;
}

int32 ADYPuzzleDirector::GetChapterCount() const
{
	return bFourActCampaign && Chapters.Num() > 0 ? Chapters.Num() : 1;
}

FText ADYPuzzleDirector::GetChapterTitle(const int32 ChapterIndex) const
{
	if (Chapters.IsValidIndex(ChapterIndex)) { return Chapters[ChapterIndex].ChapterTitle; }
	const TArray<FText>& Titles = GetCampaignChapterTitles();
	return Titles.IsValidIndex(ChapterIndex) ? Titles[ChapterIndex] : FText::GetEmpty();
}

bool ADYPuzzleDirector::StartCampaignChapter(const int32 ChapterIndex, ADYStagePresentation* Requester)
{
	if (!bFourActCampaign || !Chapters.IsValidIndex(ChapterIndex) || !IsValid(Requester)
		|| Requester->GetWorld() != GetWorld() || SequencePresentation.Get() != Requester) { return false; }
	if (!CanStartManualSequence(Requester))
	{
		// Pause-menu chapter picks arrive while a chapter is already playing.
		const bool bLive = SequencePhase == EDYActSequencePhase::Playing
			|| SequencePhase == EDYActSequencePhase::AwaitingTransition
			|| SequencePhase == EDYActSequencePhase::AwaitingFinale;
		if (!bLive) { return false; }
		if (UWorld* World = GetWorld())
		{
			World->GetTimerManager().ClearTimer(CampaignChapterTimerHandle);
			World->GetTimerManager().ClearTimer(SequenceActivationTimerHandle);
		}
		bSequenceActivationDeferred = false;
		StopEvaluation();
		CurrentActIndex = INDEX_NONE;
		SequencePhase = EDYActSequencePhase::Inactive; // no broadcast: an inactive frame would reopen the title menu
	}
	if (!CanStartManualSequence(Requester)) { return false; }
	CurrentChapterIndex = ChapterIndex;
	ActSequence = Chapters[ChapterIndex].Steps;
	CurrentActIndex = INDEX_NONE; // StartCurrentPuzzle assigns act 0 of the new chapter.
	bCarryEntryValuesOnNextStart = false; // A chapter always opens on the accepted .15 baseline.
	TGuardValue<bool> StartGuard(bAcceptingManualStart, true);
	StartCurrentPuzzle();
	return !bEndingPlay && ActivationToken.IsValid() && SequencePresentation.Get() == Requester
		&& CurrentActIndex == 0 && SequencePhase != EDYActSequencePhase::Inactive;
}

void ADYPuzzleDirector::AdvanceCampaignChapter()
{
	if (!bFourActCampaign || !Chapters.IsValidIndex(CurrentChapterIndex + 1)) { return; }
	++CurrentChapterIndex;
	ActSequence = Chapters[CurrentChapterIndex].Steps;
	CurrentActIndex = INDEX_NONE;
	bCarryEntryValuesOnNextStart = false;
	TGuardValue<bool> StartGuard(bAcceptingManualStart, true);
	StartCurrentPuzzle();
}

void ADYPuzzleDirector::ScheduleCampaignChapterFallback()
{
	UWorld* World = GetWorld();
	if (!World || !IsCampaignEnabled() || SequencePhase != EDYActSequencePhase::AwaitingFinale) { return; }
	World->GetTimerManager().ClearTimer(CampaignChapterTimerHandle);
	// The last chapter has no successor: its fallback closes the campaign instead
	// of advancing, so it must still be scheduled.
	const bool bLastChapter = !Chapters.IsValidIndex(CurrentChapterIndex + 1);
	const float Delay = bLastChapter ? 6.f : (CurrentChapterIndex == 0 ? 40.f : 8.f);
	World->GetTimerManager().SetTimer(CampaignChapterTimerHandle, this,
		&ADYPuzzleDirector::HandleCampaignChapterTimeout, Delay, false);
}

void ADYPuzzleDirector::HandleCampaignChapterTimeout()
{
	if (bEndingPlay || !IsCampaignEnabled() || SequencePhase != EDYActSequencePhase::AwaitingFinale) { return; }
	if (!Chapters.IsValidIndex(CurrentChapterIndex + 1))
	{
		// True ending: the last chapter has no successor, so the fallback closes the
		// campaign instead of asking for a chapter that does not exist.
		UE_LOG(LogDengYingShanHai, Display, TEXT("Campaign finale closed by fallback timeout (four acts complete)."));
		SetSequencePhase(EDYActSequencePhase::Complete);
		return;
	}
	UE_LOG(LogDengYingShanHai, Display, TEXT("Campaign chapter %d advanced by fallback timeout."), CurrentChapterIndex);
	AdvanceCampaignChapter();
}

void ADYPuzzleDirector::ProbeCampaignPhase(const TCHAR* Where) const
{
	if (!bCampaignAutoPlay) { return; }
	const FDYActSequenceSnapshot Snapshot = GetActSequenceSnapshot();
	const FString Line = FString::Printf(TEXT("%s phase=%d chapter=%d/%d act=%d title=%s"),
		Where, static_cast<int32>(Snapshot.Phase), Snapshot.ChapterIndex + 1, Snapshot.ChapterCount,
		Snapshot.ActIndex + 1, *Snapshot.ActTitle.ToString());
	const FString Path = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("CampaignProbe.log"));
	FFileHelper::SaveStringToFile(Line + TEXT("\n"), *Path, FFileHelper::EEncodingOptions::ForceUTF8,
		&IFileManager::Get(), EFileWrite::FILEWRITE_Append);
}

void ADYPuzzleDirector::ProbeCarriedEntryValues(const bool bCarried)
{
	const FString Probe = FPlatformMisc::GetEnvironmentVariable(TEXT("DY_CARRY_PROBE"));
	if (Probe.IsEmpty() || Probe == TEXT("0")) { return; }
	const double LightValue = LightRig && LightRig->GetLightControlComponent()
		? LightRig->GetLightControlComponent()->GetNormalizedValue() : -1.0;
	const double PuppetValue = PuppetActor && PuppetActor->GetPuppetControlComponent()
		? PuppetActor->GetPuppetControlComponent()->GetNormalizedValue() : -1.0;
	const FString Line = FString::Printf(TEXT("carry act=%d chapter=%d/%d light=%.3f puppet=%.3f carried=%d"),
		CurrentActIndex + 1, CurrentChapterIndex + 1, Chapters.Num(), LightValue, PuppetValue, bCarried ? 1 : 0);
	const FString Path = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("CarryProbe.log"));
	FFileHelper::SaveStringToFile(Line + TEXT("\n"), *Path, FFileHelper::EEncodingOptions::ForceUTF8,
		&IFileManager::Get(), EFileWrite::FILEWRITE_Append);
}

void ADYPuzzleDirector::HandleCampaignAutoPlayTick()
{
	if (!bCampaignAutoPlay || bEndingPlay || !PuzzleDefinition) { return; }
	// Only steer while the act is actually playable: the verdict, the hold window
	// and the transition remain owned by the evaluator and the presentation.
	if (SequencePhase != EDYActSequencePhase::Playing) { return; }
	if (LightRig && LightRig->GetLightControlComponent())
	{
		LightRig->GetLightControlComponent()->SetNormalizedValue(PuzzleDefinition->LightPosition.Target);
	}
	if (CurrentPuzzleRequiresPuppet() && PuppetActor && PuppetActor->GetPuppetControlComponent())
	{
		// The target must also live inside the required pose's normalized band, so
		// authored chapters keep puppet position and pose mutually solvable.
		PuppetActor->GetPuppetControlComponent()->SetNormalizedValue(PuzzleDefinition->PuppetPosition.Target);
	}
}

void ADYPuzzleDirector::EnsureCampaignChapters()
{
	if (Chapters.Num() > 0) { return; }
	Chapters.SetNum(4);
	const TArray<FText>& Titles = GetCampaignChapterTitles();
	const TCHAR* Subtitles[4] = {
		TEXT("以灯为日，以影为夸父"),
		TEXT("衔木石入海，影连成途"),
		TEXT("断首犹舞，盾影合击"),
		TEXT("昼夜交替，晦明同光")
	};
	for (int32 Index = 0; Index < 4; ++Index)
	{
		Chapters[Index].ChapterTitle = Titles[Index];
		Chapters[Index].ChapterSubtitle = FText::FromString(Subtitles[Index]);
	}
	Chapters[0].Steps = BaseActSequence;

	auto MakeDefinition = [this](const TCHAR* Id, const TCHAR* Display, const double LightTarget, const double PuppetTarget,
		const FName Pose, const double HoldSeconds) -> UDYPuzzleDefinition*
	{
		UDYPuzzleDefinition* Definition = NewObject<UDYPuzzleDefinition>(this);
		Definition->PuzzleId = FName(Id);
		Definition->DisplayName = FText::FromString(Display);
		Definition->LightPosition.bEnabled = true;
		Definition->LightPosition.Target = LightTarget;
		Definition->LightPosition.EnterTolerance = 0.11;
		Definition->LightPosition.ExitTolerance = 0.17;
		Definition->PuppetPosition.bEnabled = true;
		Definition->PuppetPosition.Target = PuppetTarget;
		Definition->PuppetPosition.EnterTolerance = 0.12;
		Definition->PuppetPosition.ExitTolerance = 0.18;
		Definition->RequiredPuppetPoseId = Pose;
		Definition->RequiredHoldSeconds = HoldSeconds;
		RuntimeDefinitions.Add(Definition);
		return Definition;
	};
	auto MakeStep = [](UDYPuzzleDefinition* Definition, const TCHAR* Title) -> FDYActSequenceEntry
	{
		FDYActSequenceEntry Entry;
		Entry.Definition = Definition;
		Entry.ActTitle = FText::FromString(Title);
		return Entry;
	};
	const FName Reach(TEXT("P02_StrideReach"));

	// 第二幕 精卫填海：灯位与石影逐段接成通路。开局偶位 0.15，容差 0.12，0.20 会直接算到位。
	Chapters[1].Steps.Add(MakeStep(MakeDefinition(TEXT("P04_Jingwei_01"), TEXT("衔石入海"), 0.66, 0.38, NAME_None, 1.0), TEXT("衔石入海")));
	Chapters[1].Steps.Add(MakeStep(MakeDefinition(TEXT("P04_Jingwei_02"), TEXT("石影连途"), 0.34, 0.60, NAME_None, 1.0), TEXT("石影连途")));
	Chapters[1].Steps.Add(MakeStep(MakeDefinition(TEXT("P04_Jingwei_03"), TEXT("填海成洲"), 0.78, 0.86, Reach, 1.25), TEXT("填海成洲")));

	// 第三幕 刑天舞干戚：盾影角度与节奏。开局灯位 0.15，容差 0.11，0.22 会直接算到位。
	Chapters[2].Steps.Add(MakeStep(MakeDefinition(TEXT("P05_Xingtian_01"), TEXT("断首犹立"), 0.38, 0.50, NAME_None, 1.0), TEXT("断首犹立")));
	Chapters[2].Steps.Add(MakeStep(MakeDefinition(TEXT("P05_Xingtian_02"), TEXT("举盾成影"), 0.50, 0.84, Reach, 1.0), TEXT("举盾成影")));
	Chapters[2].Steps.Add(MakeStep(MakeDefinition(TEXT("P05_Xingtian_03"), TEXT("舞干戚"), 0.84, 0.84, Reach, 1.25), TEXT("舞干戚")));

	// 第四幕 烛龙昼夜：开局灯位是 0.15，目标必须离开这个容差，否则一进门就显示「灯已就位」。
	Chapters[3].Steps.Add(MakeStep(MakeDefinition(TEXT("P06_Zhulong_01"), TEXT("夜伏"), 0.58, 0.86, NAME_None, 1.0), TEXT("夜伏")));
	Chapters[3].Steps.Add(MakeStep(MakeDefinition(TEXT("P06_Zhulong_02"), TEXT("睁眼为昼"), 0.86, 0.86, Reach, 1.0), TEXT("睁眼为昼")));
	Chapters[3].Steps.Add(MakeStep(MakeDefinition(TEXT("P06_Zhulong_03"), TEXT("晦明同光"), 0.50, 0.88, Reach, 1.25), TEXT("晦明同光")));
}

void ADYPuzzleDirector::ApplyChapterPalette()
{
	UWorld* World = GetWorld();
	if (!World || !bFourActCampaign) { return; }
	const int32 StepIndex = CurrentActIndex == INDEX_NONE ? 0 : CurrentActIndex;
	// The daylight change follows the solved second step, rather than its entry.
	const bool bDaylight = StepIndex > 1 || (StepIndex == 1
		&& (SequencePhase == EDYActSequencePhase::AwaitingTransition
			|| SequencePhase == EDYActSequencePhase::AwaitingFinale
			|| SequencePhase == EDYActSequencePhase::Complete));
	if (PuppetActor) { PuppetActor->SetChapterDaylight(CurrentChapterIndex == 3 && bDaylight); }
	const int32 PaletteStep = CurrentChapterIndex == 3 ? (bDaylight ? 1 : 0) : StepIndex;
	const DYCampaign::FPalette Palette = DYCampaign::GetPalette(CurrentChapterIndex, PaletteStep);
	if (!SkyInstance)
	{
		for (TActorIterator<AStaticMeshActor> It(World); It; ++It)
		{
			AStaticMeshActor* Sky = *It;
			if (!Sky || !Sky->GetStaticMeshComponent() || !Sky->GetName().Contains(TEXT("Sky_Dome"))) { continue; }
			UMaterialInterface* Current = Sky->GetStaticMeshComponent()->GetMaterial(0);
			if (!Current) { continue; }
			SkyInstance = UMaterialInstanceDynamic::Create(Current, this);
			if (!SkyInstance) { continue; }
			Sky->GetStaticMeshComponent()->SetMaterial(0, SkyInstance);
			break;
		}
	}
	if (SkyInstance)
	{
		SkyInstance->SetVectorParameterValue(TEXT("Horizon"), Palette.Horizon);
		SkyInstance->SetVectorParameterValue(TEXT("Zenith"), Palette.Zenith);
		SkyInstance->SetScalarParameterValue(TEXT("SkyIntensity"), Palette.SkyIntensity);
	}
	if (!ExteriorFog)
	{
		for (TActorIterator<AExponentialHeightFog> It(World); It; ++It)
		{
			AExponentialHeightFog* Fog = *It;
			if (!Fog || !Fog->GetComponent() || !Fog->GetName().Contains(TEXT("ExtFog"))) { continue; }
			ExteriorFog = Fog;
			break;
		}
	}
	if (ExteriorFog) { ExteriorFog->GetComponent()->SetFogDensity(Palette.FogDensity); }

	// Each act gets its own key-light colour so the projected shadow and the screen
	// wash read as a different myth even though the theatre is shared. The puzzle
	// verdict only ever reads normalized light/puppet values, so this is presentational.
	static const FLinearColor ChapterKeyColors[4] = {
		FLinearColor(1.00f, 0.86f, 0.66f),
		FLinearColor(0.55f, 0.86f, 0.92f),
		FLinearColor(1.00f, 0.55f, 0.38f),
		FLinearColor(0.58f, 0.66f, 1.00f)
	};
	static const float ChapterKeyIntensity[4] = { 1.00f, 0.92f, 1.10f, 1.15f };
	const int32 ColorIndex = FMath::Clamp(CurrentChapterIndex, 0, 3);
	if (ADYLightRigActor* Rig = LightRig.Get())
	{
		const FLinearColor KeyColor = CurrentChapterIndex == 3
			? (bDaylight ? FLinearColor(1.0f, 0.86f, 0.64f) : FLinearColor(0.24f, 0.42f, 0.82f))
			: ChapterKeyColors[ColorIndex];
		Rig->SetChapterKeyColor(KeyColor * ChapterKeyIntensity[ColorIndex]);
	}
}

void ADYPuzzleDirector::SetSequencePhase(const EDYActSequencePhase NewPhase)
{
	SequencePhase = NewPhase;
	if (CurrentChapterIndex == 3) { ApplyChapterPalette(); }
	ProbeCampaignPhase(TEXT("phase"));
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
	bCarryEntryValuesOnNextStart = bCarryControlValuesAcrossActs && bFourActCampaign;
	++CurrentActIndex;
	StartCurrentPuzzle();
	return true;
}

bool ADYPuzzleDirector::AcceptFinaleCompletion(ADYStagePresentation* Presentation, const FGuid& Token)
{
	// Only the registered native Presentation may submit its verified actual full forest.
	if (!IsFinalSequenceAct() || !IsSequenceSubmissionCurrent(Presentation, Token, EDYActSequencePhase::AwaitingFinale)) { return false; }
	if (IsCampaignEnabled() && Chapters.IsValidIndex(CurrentChapterIndex + 1))
	{
		AdvanceCampaignChapter(); // Consume: the next chapter opens its own act 0 and token.
		return true;
	}
	if (UWorld* World = GetWorld()) { World->GetTimerManager().ClearTimer(CampaignChapterTimerHandle); }
	SetSequencePhase(EDYActSequencePhase::Complete); // Consume once; preserve Token and resources.
	return true;
}