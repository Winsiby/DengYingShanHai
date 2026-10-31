#include "Stage/DYStagePresentation.h"

#include "DengYingShanHai.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "TimerManager.h"

#include "Core/DYStageGameMode.h"
#include "Engine/StaticMeshActor.h"

#include "Components/StaticMeshComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Stage/DYForestPresentationActor.h"
#include "Stage/DYStaffContactLibrary.h"

ADYStagePresentation::ADYStagePresentation()
{
	PrimaryActorTick.bCanEverTick = false;
}

EDYStageEnvironmentState ADYStagePresentation::MapSequenceToEnvironment(const FDYActSequenceSnapshot& Snapshot)
{
	if (!Snapshot.bSequenceEnabled || Snapshot.ActCount != 3 || Snapshot.ActIndex < 0 || Snapshot.ActIndex > 2)
	{
		return EDYStageEnvironmentState::Dormant;
	}
	switch (Snapshot.Phase)
	{
	case EDYActSequencePhase::Playing:
		return Snapshot.ActIndex == 0 ? EDYStageEnvironmentState::Dormant
			: Snapshot.ActIndex == 1 ? EDYStageEnvironmentState::SunAwakened : EDYStageEnvironmentState::ChaseAwakened;
	case EDYActSequencePhase::AwaitingTransition:
		return Snapshot.ActIndex == 0 ? EDYStageEnvironmentState::SunAwakened
			: Snapshot.ActIndex == 1 ? EDYStageEnvironmentState::ChaseAwakened : EDYStageEnvironmentState::Dormant;
	case EDYActSequencePhase::AwaitingFinale:
		return Snapshot.ActIndex == 2 ? EDYStageEnvironmentState::FinaleReady : EDYStageEnvironmentState::Dormant;
	case EDYActSequencePhase::Complete:
		return Snapshot.ActIndex == 2 ? EDYStageEnvironmentState::ForestComplete : EDYStageEnvironmentState::Dormant;
	default:
		return EDYStageEnvironmentState::Dormant;
	}
}

void ADYStagePresentation::ApplyFiveStateEnvironment(const FDYActSequenceSnapshot& Snapshot)
{
	if (!bEnableFiveStateDevEnvironment || !bStaffPresentationRuntimeActive || !IsValid(this)
		|| !IsValid(StageEnvironment) || StageEnvironment->GetWorld() != GetWorld() || !Snapshot.bSequenceEnabled) { return; }
	StageEnvironment->ApplyState(MapSequenceToEnvironment(Snapshot));
	// No writes after a cosmetic listener can re-enter/reset/destroy this session.
}

void ADYStagePresentation::BeginPlay()
{
	Super::BeginPlay();
	ResetStaffPresentation();
	bStaffPresentationRuntimeActive = true;
	BindDirector();
	SynchronizeFromDirector();
	// Registered only after the existing bind/synchronise work so a late listener
	// reads an already-settled snapshot instead of replaying activation cues.
	RegisterWithGameMode();
}

void ADYStagePresentation::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	bStaffPresentationRuntimeActive = false;
	if (StaffContactAcceptedHandle.IsValid())
	{
		StaffContactAccepted.Remove(StaffContactAcceptedHandle);
		StaffContactAcceptedHandle.Reset();
	}
	CancelActTransition();
	ResetStaffPresentation();
	ResetFeedbackDisplay();
	if (UWorld* World = GetWorld())
	{
		if (ADYStageGameMode* GameMode = World->GetAuthGameMode<ADYStageGameMode>())
		{
			GameMode->UnregisterStagePresentation(this);
		}
	}
	UnbindDirector();
	Super::EndPlay(EndPlayReason);
}

FDYPlayerAlignmentDisplay ADYStagePresentation::BuildPlayerAlignmentDisplay(const FDYEvaluationResult& Result, bool bEnabled)
{
	FDYPlayerAlignmentDisplay Display;
	Display.bEnabled = bEnabled;
	if (!bEnabled || Result.State == EDYPuzzleRuntimeState::Inactive
		|| Result.State == EDYPuzzleRuntimeState::Resolved || Result.Feedback == EDYPuzzleFeedbackState::InvalidSample) { return Display; }
	Display.bHasValidSample = true;
	Display.bLightRequired = Result.LightPosition.bEnabled;
	Display.bLightReady = Display.bLightRequired && Result.LightPosition.bIsValid;
	Display.bPuppetRequired = Result.PuppetPosition.bEnabled || Result.bPuppetPoseEnabled;
	Display.bPuppetReady = Display.bPuppetRequired
		&& (!Result.PuppetPosition.bEnabled || Result.PuppetPosition.bIsValid)
		&& (!Result.bPuppetPoseEnabled || Result.bPuppetPoseValid);
	Display.bJointReady = Result.bAllRequiredConditionsValid;
	Display.bHolding = Display.bJointReady && Result.State == EDYPuzzleRuntimeState::Holding && !Result.bHoldCanceled;
	if (Display.bHolding && FMath::IsFinite(Result.HoldElapsedSeconds)
		&& FMath::IsFinite(Result.HoldRequiredSeconds) && Result.HoldRequiredSeconds > 0.0)
	{
		Display.HoldFraction = FMath::Clamp(Result.HoldElapsedSeconds / Result.HoldRequiredSeconds, 0.0, 1.0);
	}
	return Display;
}

FDYPlayerAlignmentDisplay ADYStagePresentation::GetPlayerAlignmentDisplay() const
{
	if (!bEnablePlayerAlignmentFeedback || !bStaffPresentationRuntimeActive
		|| (PlayerActDisplay.bSequenceEnabled && PlayerActDisplay.Phase != EDYActSequencePhase::Playing)) { return {}; }
	return PlayerAlignmentDisplay;
}

void ADYStagePresentation::SetPlayerAlignmentDisplay(const FDYPlayerAlignmentDisplay& Snapshot)
{
	if (!(PlayerAlignmentDisplay == Snapshot))
	{
		PlayerAlignmentDisplay = Snapshot;
		const FDYPlayerAlignmentDisplay Notification = GetPlayerAlignmentDisplay();
		PlayerAlignmentDisplayChanged.Broadcast(Notification); // No writes after reentrant listeners.
	}
}

bool ADYStagePresentation::IsStaffPresentationTokenCurrent(const FGuid& Token) const
{
	return bEnableStaffContactPresentation && bStaffPresentationRuntimeActive
		&& IsValid(PuzzleDirector) && PuzzleDirector->GetWorld() == GetWorld()
		&& Token.IsValid() && ResolvedStaffPresentation.bHasSnapshot
		&& Token == ResolvedStaffPresentation.Token && PuzzleDirector->IsResolvedTokenCurrent(Token);
}

FDYStageResolvedPresentationSnapshot ADYStagePresentation::GetResolvedStaffPresentationSnapshot() const
{
	return IsStaffPresentationTokenCurrent(ResolvedStaffPresentation.Token)
		? ResolvedStaffPresentation : FDYStageResolvedPresentationSnapshot();
}

FDYStaffContactPresentationSnapshot ADYStagePresentation::GetStaffContactPresentationSnapshot() const
{
	return StaffContactPresentation.bHasContact && IsStaffPresentationTokenCurrent(StaffContactPresentation.Token)
		? StaffContactPresentation : FDYStaffContactPresentationSnapshot();
}

void ADYStagePresentation::ResetStaffPresentation()
{
	ResolvedStaffPresentation = FDYStageResolvedPresentationSnapshot();
	StaffContactPresentation = FDYStaffContactPresentationSnapshot();
	ResetForestPresentation();
}

void ADYStagePresentation::ResetForestPresentation()
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(CampaignForestTimerHandle);
		World->GetTimerManager().ClearTimer(CampaignForestContactTimerHandle);
	}
	bCampaignForestAwaitingContact = false;
	CampaignForestToken.Invalidate();
	CampaignForestElapsed = 0.f;
	ADYForestPresentationActor* Actor = OwnedForestActor.Get();
	const FGuid Token = OwnedForestToken;
	OwnedForestActor.Reset();
	OwnedForestToken.Invalidate();
	if (IsValid(Actor)) { Actor->ClearSession(this, Token); }
}

bool ADYStagePresentation::PlayCampaignForestFinale(const float Seconds)
{
		if (!bStaffPresentationRuntimeActive || !IsValid(PuzzleDirector) || !PuzzleDirector->IsCampaignEnabled()
		|| !GetWorld())
	{
				return false;
	}
	const FGuid Token = PuzzleDirector->GetResolvedPuzzleSnapshot().Token;
	if (!Token.IsValid() || !PuzzleDirector->IsResolvedTokenCurrent(Token) || OwnedForestToken == Token)
	{
				return false;
	}
		CampaignForestToken = Token;
	CampaignForestSeconds = FMath::Max(0.2f, Seconds);
	if (TryBeginCampaignForestGrowth()) { return true; }
	// The authored contact beat may still be in flight (the presentation blueprint
	// raises it after the resolve broadcast). Wait for the accepted contact instead
	// of dropping the forest; the shot ends with the staff tip on the ground.
	if (!bEnableStaffContactPresentation || GetStaffContactPresentationSnapshot().bHasContact)
	{
				return false;
	}
		if (!bCampaignForestAwaitingContact)
	{
		bCampaignForestAwaitingContact = true;
		if (!StaffContactAcceptedHandle.IsValid())
		{
			StaffContactAcceptedHandle = StaffContactAccepted.AddUObject(
				this, &ADYStagePresentation::HandleCampaignForestContactAccepted);
		}
		GetWorld()->GetTimerManager().SetTimer(CampaignForestContactTimerHandle, this,
			&ADYStagePresentation::HandleCampaignForestContactTimeout, 6.0f, false);
		UE_LOG(LogDengYingShanHai, Display, TEXT("[CampaignForest] waiting for the staff contact beat."));
	}
	return true;
}

bool ADYStagePresentation::TryBeginCampaignForestGrowth()
{
		if (!CampaignForestToken.IsValid()) { return false; }
	if (OwnedForestToken != CampaignForestToken && !BeginForestPresentation(CampaignForestToken))
	{
				const FDYStaffContactPresentationSnapshot Contact = GetStaffContactPresentationSnapshot();
		UE_LOG(LogDengYingShanHai, Warning,
			TEXT("[CampaignForest] skipped contact=%d contactToken=%d scene=%d forest=%s owned=%d screen=%d ground=%d"),
			Contact.bHasContact ? 1 : 0, Contact.Token == CampaignForestToken ? 1 : 0, IsContactSceneUnchanged() ? 1 : 0,
			*GetNameSafe(GetForestPresentationActor()), OwnedForestToken.IsValid() ? 1 : 0,
			IsValid(StaffProjectionScreen) ? 1 : 0, IsValid(NarrativeGroundLine) ? 1 : 0);
		return false;
	}
	bCampaignForestAwaitingContact = false;
	CampaignForestElapsed = 0.f;
		if (!SetForestNormalizedGrowth(CampaignForestToken, 0.0))
	{
		ResetForestPresentation();
		return false;
	}
		GetWorld()->GetTimerManager().SetTimer(CampaignForestTimerHandle, this,
		&ADYStagePresentation::TickCampaignForestFinale, 0.05f, true);
	UE_LOG(LogDengYingShanHai, Display, TEXT("[CampaignForest] growing over %.2f s."), CampaignForestSeconds);
	return true;
}

void ADYStagePresentation::HandleCampaignForestContactAccepted(const FDYStaffContactPresentationSnapshot& Contact)
{
		if (!bCampaignForestAwaitingContact || !Contact.bHasContact || Contact.Token != CampaignForestToken) { return; }
	bCampaignForestAwaitingContact = false;
	if (UWorld* World = GetWorld())
	{
		// Leave the contact callback stack first: authored cleanup that runs after the
		// accept node must not wipe a forest that was started inside the broadcast.
		World->GetTimerManager().ClearTimer(CampaignForestContactTimerHandle);
		World->GetTimerManager().SetTimer(CampaignForestContactTimerHandle, this,
			&ADYStagePresentation::StartPendingCampaignForestGrowth, 0.25f, false);
	}
}

void ADYStagePresentation::StartPendingCampaignForestGrowth()
{
		TryBeginCampaignForestGrowth();
}

void ADYStagePresentation::HandleCampaignForestContactTimeout()
{
	if (!bCampaignForestAwaitingContact) { return; }
	bCampaignForestAwaitingContact = false;
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[CampaignForest] staff contact never arrived; forest skipped."));
	}

void ADYStagePresentation::TickCampaignForestFinale()
{
	if (!bStaffPresentationRuntimeActive || !IsValid(PuzzleDirector) || !CampaignForestToken.IsValid())
	{
				ResetForestPresentation();
		return;
	}
	CampaignForestElapsed += 0.05f;
	const float Alpha = FMath::Clamp(CampaignForestElapsed / CampaignForestSeconds, 0.f, 1.f);
	if (!SetForestNormalizedGrowth(CampaignForestToken, Alpha))
	{
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[CampaignForest] growth rejected at %.2f."), Alpha);
				ResetForestPresentation();
		return;
	}
	if (Alpha >= 1.f)
	{
		GetWorld()->GetTimerManager().ClearTimer(CampaignForestTimerHandle);
		UE_LOG(LogDengYingShanHai, Display, TEXT("[CampaignForest] full growth reached."));
			}
}

void ADYStagePresentation::HandleResolvedSnapshotInvalidated(const FGuid& Token)
{
	if (Token == PendingTransitionToken) { CancelActTransition(); }
	// A prior native listener may already have resolved a new activation.
	if (Token.IsValid() && (Token == ResolvedStaffPresentation.Token
		|| Token == StaffContactPresentation.Token || Token == OwnedForestToken))
	{
		ResetStaffPresentation();
	}
	// Forward the real old identity even if a prior listener already captured a new
	// native snapshot. BP must filter its own cue token. No writes after this hook:
	// reset/destroy/restart from a listener cannot be overwritten by stale cleanup.
	if (bStaffPresentationRuntimeActive && bEnableStaffContactPresentation && Token.IsValid())
	{
		ReceiveStaffPresentationInvalidated(Token);
	}
}

ADYForestPresentationActor* ADYStagePresentation::GetForestPresentationActor() const
{
	return IsValid(ForestPresentationActor) && ForestPresentationActor->GetWorld() == GetWorld()
		? ForestPresentationActor.Get() : nullptr;
}

bool ADYStagePresentation::BeginForestPresentation(const FGuid& Token)
{
	const auto Contact = GetStaffContactPresentationSnapshot();
	const bool bContactOk = Contact.bHasContact && Contact.Token == Token;
	const bool bForestOk = IsValid(ForestPresentationActor) && ForestPresentationActor->GetWorld() == GetWorld();
	const bool bOwnedOk = !OwnedForestToken.IsValid();
	const bool bSceneOk = IsContactSceneUnchanged();
	if (!bContactOk || !bForestOk || !bOwnedOk || !bSceneOk)
	{
				return false;
	}
	if (!ForestPresentationActor->BeginSession(this, Contact)) { return false; }
	OwnedForestActor = ForestPresentationActor;
	OwnedForestToken = Token;
	return true;
}

bool ADYStagePresentation::SetForestNormalizedGrowth(const FGuid& Token, const double Progress)
{
	if (IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled()
		&& PuzzleDirector->GetActSequenceSnapshot().Phase == EDYActSequencePhase::Complete)
	{
				return false;
	}
	if (!Token.IsValid() || Token != OwnedForestToken)
	{
				return false;
	}
	ADYForestPresentationActor* Actor = OwnedForestActor.Get();
	const bool bHasContact = GetStaffContactPresentationSnapshot().bHasContact;
	const bool bSceneSame = IsContactSceneUnchanged();
	const bool bActorOk = IsValid(Actor) && Actor->GetWorld() == GetWorld();
	if (!bHasContact || !bSceneSame || !bActorOk
		|| !Actor->ApplyNormalizedGrowth(this, Token, Progress))
	{
				ResetForestPresentation();
		return false;
	}
	return true;
}

bool ADYStagePresentation::IsContactSceneUnchanged() const
{
	if (!GetStaffContactPresentationSnapshot().bHasContact || !IsValid(StaffProjectionScreen)
		|| !IsValid(NarrativeGroundLine) || StaffProjectionScreen->GetWorld() != GetWorld()
		|| NarrativeGroundLine->GetWorld() != GetWorld()) { return false; }
	const ADYLightRigActor* Light = PuzzleDirector->GetLightRigActor();
	const ADYPuppetActor* Puppet = PuzzleDirector->GetPuppetActor();
	if (!IsValid(Light) || !IsValid(Puppet) || Light->GetWorld() != GetWorld() || Puppet->GetWorld() != GetWorld()
		|| !Light->GetActorTransform().Equals(ResolvedStaffPresentation.Light.WorldTransform, UE_DOUBLE_SMALL_NUMBER)
		|| !Puppet->GetActorTransform().Equals(ResolvedStaffPresentation.Puppet.WorldTransform, UE_DOUBLE_SMALL_NUMBER)) { return false; }
	const auto Current = UDYStaffProjectionLibrary::CaptureStaffProjection(Light, Puppet,
		StaffProjectionScreen->GetStaticMeshComponent());
	const auto& Contact = StaffContactPresentation.Projection;
	return Current.bHasGeometry && Current.Staff.bIsValid
		&& Current.EmitterWorld.Equals(Contact.EmitterWorld, UE_DOUBLE_SMALL_NUMBER)
		&& Current.ScreenTransform.Equals(Contact.ScreenTransform, UE_DOUBLE_SMALL_NUMBER)
		&& Current.ScreenLocalMin.Equals(Contact.ScreenLocalMin, UE_DOUBLE_SMALL_NUMBER)
		&& Current.ScreenLocalMax.Equals(Contact.ScreenLocalMax, UE_DOUBLE_SMALL_NUMBER)
		&& Current.Staff.ComponentTransform.Equals(Contact.Staff.ComponentTransform, UE_DOUBLE_SMALL_NUMBER)
		&& Current.Staff.EndAWorld.Equals(Contact.Staff.EndAWorld, UE_DOUBLE_SMALL_NUMBER)
		&& Current.Staff.EndBWorld.Equals(Contact.Staff.EndBWorld, UE_DOUBLE_SMALL_NUMBER)
		&& NarrativeGroundLine->GetActorLocation().Equals(ResolvedStaffPresentation.GroundLine.WorldAnchor, UE_DOUBLE_SMALL_NUMBER);
}

bool ADYStagePresentation::ClearForestPresentation(const FGuid& Token)
{
	if (IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled()
		&& PuzzleDirector->GetActSequenceSnapshot().Phase == EDYActSequencePhase::Complete) { return false; }
	if (!Token.IsValid() || Token != OwnedForestToken) { return false; }
	ResetForestPresentation();
	return true;
}

void ADYStagePresentation::CaptureResolvedStaffPresentation(const FName PuzzleId)
{
	if (!bEnableStaffContactPresentation || !bStaffPresentationRuntimeActive || !IsValid(PuzzleDirector)
		|| PuzzleDirector->GetWorld() != GetWorld()
		|| (PuzzleDirector->IsActSequenceEnabled() && !PuzzleDirector->IsFinalSequenceAct())) { return; }
	const FDYResolvedPuzzleSnapshot Resolved = PuzzleDirector->GetResolvedPuzzleSnapshot();
	if (!Resolved.bIsResolved || Resolved.PuzzleId != PuzzleId
		|| !PuzzleDirector->IsResolvedTokenCurrent(Resolved.Token)) { return; }
	if (ResolvedStaffPresentation.bHasSnapshot && ResolvedStaffPresentation.Token == Resolved.Token)
	{
		return; // Never recapture an initial pose from a later animation/duplicate event.
	}
	ResetStaffPresentation();
	FDYStageResolvedPresentationSnapshot Captured;
	Captured.bHasSnapshot = true;
	Captured.Token = Resolved.Token;
	Captured.PuzzleId = Resolved.PuzzleId;
	Captured.Light = Resolved.Light;
	Captured.Puppet = Resolved.Puppet;
	ADYLightRigActor* Light = PuzzleDirector->GetLightRigActor();
	ADYPuppetActor* Puppet = PuzzleDirector->GetPuppetActor();
	if (IsValid(Light) && IsValid(Puppet) && IsValid(StaffProjectionScreen)
		&& Light->GetWorld() == GetWorld() && Puppet->GetWorld() == GetWorld()
		&& StaffProjectionScreen->GetWorld() == GetWorld()
		&& Captured.Light.bIsValid && Captured.Puppet.bIsValid
		&& Light->GetActorTransform().Equals(Captured.Light.WorldTransform, UE_DOUBLE_SMALL_NUMBER)
		&& Puppet->GetActorTransform().Equals(Captured.Puppet.WorldTransform, UE_DOUBLE_SMALL_NUMBER))
	{
		Captured.Projection = UDYStaffProjectionLibrary::CaptureStaffProjection(Light, Puppet,
			StaffProjectionScreen->GetStaticMeshComponent());
		if (IsValid(NarrativeGroundLine) && NarrativeGroundLine->GetWorld() == GetWorld())
		{
			Captured.GroundLine = UDYStaffContactLibrary::CaptureNarrativeGroundLine(Captured.Projection,
				NarrativeGroundLine->GetActorLocation());
		}
	}
	// Missing cosmetic geometry cannot revoke the authoritative resolved fact.
	if (PuzzleDirector->IsResolvedTokenCurrent(Captured.Token)) { ResolvedStaffPresentation = Captured; }
	UE_LOG(LogDengYingShanHai, Display, TEXT("[StaffContact] captured puzzle=%s geometry=%d ground=%d"),
		*PuzzleId.ToString(), Captured.Projection.bHasGeometry ? 1 : 0, Captured.GroundLine.bIsValid ? 1 : 0);
}

bool ADYStagePresentation::TryAcceptStaffContact(const FGuid& Token)
{
	if (!IsStaffPresentationTokenCurrent(Token) || StaffContactPresentation.bHasContact
		|| !ResolvedStaffPresentation.Projection.bHasGeometry || !ResolvedStaffPresentation.GroundLine.bIsValid
		|| !IsValid(StaffProjectionScreen) || !IsValid(NarrativeGroundLine)
		|| StaffProjectionScreen->GetWorld() != GetWorld() || NarrativeGroundLine->GetWorld() != GetWorld())
	{
		UE_LOG(LogDengYingShanHai, Warning,
			TEXT("[StaffContact] reject tokenCurrent=%d already=%d geometry=%d ground=%d screen=%d noun=%d"),
			IsStaffPresentationTokenCurrent(Token) ? 1 : 0, StaffContactPresentation.bHasContact ? 1 : 0,
			ResolvedStaffPresentation.Projection.bHasGeometry ? 1 : 0, ResolvedStaffPresentation.GroundLine.bIsValid ? 1 : 0,
			IsValid(StaffProjectionScreen) ? 1 : 0, IsValid(NarrativeGroundLine) ? 1 : 0);
		return false;
	}
	ADYLightRigActor* Light = PuzzleDirector->GetLightRigActor();
	ADYPuppetActor* Puppet = PuzzleDirector->GetPuppetActor();
	if (!IsValid(Light) || !IsValid(Puppet) || Light->GetWorld() != GetWorld() || Puppet->GetWorld() != GetWorld()) { return false; }
	const auto Current = UDYStaffProjectionLibrary::CaptureStaffProjection(Light, Puppet,
		StaffProjectionScreen->GetStaticMeshComponent());
	const auto& Initial = ResolvedStaffPresentation.Projection;
	if (!Current.bHasGeometry || !Current.EmitterWorld.Equals(Initial.EmitterWorld, UE_DOUBLE_SMALL_NUMBER)
		|| !Current.ScreenTransform.Equals(Initial.ScreenTransform, UE_DOUBLE_SMALL_NUMBER)
		|| !Current.ScreenLocalMin.Equals(Initial.ScreenLocalMin, UE_DOUBLE_SMALL_NUMBER)
		|| !Current.ScreenLocalMax.Equals(Initial.ScreenLocalMax, UE_DOUBLE_SMALL_NUMBER)
		|| !NarrativeGroundLine->GetActorLocation().Equals(ResolvedStaffPresentation.GroundLine.WorldAnchor, UE_DOUBLE_SMALL_NUMBER)
		|| !UDYStaffContactLibrary::IsStaffAOnNarrativeGround(Current, ResolvedStaffPresentation.GroundLine))
	{
		return false;
	}
	FDYStaffContactPresentationSnapshot Accepted;
	Accepted.bHasContact = true;
	Accepted.Token = Token;
	Accepted.PuzzleId = ResolvedStaffPresentation.PuzzleId;
	Accepted.Projection = Current;
	Accepted.ContactWorldPosition = Current.EndA.WorldPosition;
	UE_LOG(LogDengYingShanHai, Display, TEXT("[StaffContact] accepted token=%s position=%s"),
		*Token.ToString(), *Current.EndA.WorldPosition.ToCompactString());
	StaffContactPresentation = Accepted; // Consume before any reentrant callback.
	ReceiveStaffContactAccepted(Accepted);
	if (IsStaffPresentationTokenCurrent(Token)) { StaffContactAccepted.Broadcast(Accepted); }
	// No mutation after callbacks: reset/destroy/restart from a listener stays intact.
	return true;
}

void ADYStagePresentation::RegisterWithGameMode()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	// Public cosmetic registration; Dev getters and diagnostics retain their gates.
	if (ADYStageGameMode* GameMode = World->GetAuthGameMode<ADYStageGameMode>())
	{
		GameMode->RegisterStagePresentation(this);
	}
}

bool ADYStagePresentation::IsDevFeedbackEnabledForWorld(const UWorld* World)
{
#if !UE_BUILD_SHIPPING
	if (!World)
	{
		return false;
	}
	const UPackage* Package = World->GetPackage();
	return Package && IsDevContentPackage(Package->GetName());
#else
	return false;
#endif
}

void ADYStagePresentation::UpdateBaselineDisplay(const EDYPuzzleFeedbackState FeedbackState)
{
	if (!GetWorld())
	{
		return;
	}
	EDYStageFeedbackDisplay Baseline = EDYStageFeedbackDisplay::Hidden;
	switch (FeedbackState)
	{
	case EDYPuzzleFeedbackState::Far:
		Baseline = EDYStageFeedbackDisplay::Adjust;
		break;
	case EDYPuzzleFeedbackState::Near:
		Baseline = EDYStageFeedbackDisplay::Near;
		break;
	case EDYPuzzleFeedbackState::InsideTarget:
		Baseline = EDYStageFeedbackDisplay::Holding;
		break;
	case EDYPuzzleFeedbackState::Holding:
		Baseline = EDYStageFeedbackDisplay::Holding;
		break;
	case EDYPuzzleFeedbackState::Resolved:
		Baseline = EDYStageFeedbackDisplay::Complete;
		break;
	case EDYPuzzleFeedbackState::InvalidSample:
	default:
		Baseline = EDYStageFeedbackDisplay::Hidden;
		break;
	}

	FeedbackBaseline = Baseline;

	// A fresh Holding or Complete always wins over a running interrupted overlay.
	if (Baseline == EDYStageFeedbackDisplay::Holding || Baseline == EDYStageFeedbackDisplay::Complete)
	{
		ClearInterruptedOverlay();
		return;
	}

	// While an interruption overlay is running the baseline updates silently; the
	// overlay keeps showing until its one-shot expires.
	if (FeedbackDisplay == EDYStageFeedbackDisplay::Interrupted)
	{
		return;
	}

	SetFeedbackDisplay(Baseline);
}

void ADYStagePresentation::SetFeedbackDisplay(const EDYStageFeedbackDisplay NewDisplay)
{
	if (FeedbackDisplay != NewDisplay)
	{
		FeedbackDisplay = NewDisplay;
		PlayerFeedbackDisplayChanged.Broadcast(NewDisplay);
		if (IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled()
			&& (!bStaffPresentationRuntimeActive || FeedbackDisplay != NewDisplay)) { return; }
		if (IsDevFeedbackEnabledForWorld(GetWorld()))
		{
			FeedbackDisplayChanged.Broadcast(NewDisplay);
		}
	}
}

void ADYStagePresentation::ShowInterruptedTemporarily()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	if (FeedbackDisplay == EDYStageFeedbackDisplay::Interrupted
		&& World->GetTimerManager().IsTimerActive(DevInterruptedTimerHandle))
	{
		// EvaluationUpdated and HoldCanceled describe the same cancellation.
		return;
	}

	// One-shot only. A later sample may keep updating the baseline, but it must never
	// cancel this overlay, so the baseline is written without touching the timer.
	World->GetTimerManager().SetTimer(
		DevInterruptedTimerHandle,
		this,
		&ADYStagePresentation::ClearInterruptedOverlay,
		FMath::Max(DevInterruptedDisplaySeconds, 0.1f),
		false);
	SetFeedbackDisplay(EDYStageFeedbackDisplay::Interrupted);
}

void ADYStagePresentation::ClearInterruptedOverlay()
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(DevInterruptedTimerHandle);
	}

	SetFeedbackDisplay(FeedbackBaseline);
}

void ADYStagePresentation::ResetFeedbackDisplay()
{
	const bool bGuardSequence = bStaffPresentationRuntimeActive && IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled();
	const FGuid OperationToken = IsValid(PuzzleDirector) ? PuzzleDirector->ActivationToken : FGuid();
	SetPlayerAlignmentDisplay(FDYPlayerAlignmentDisplay());
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(DevInterruptedTimerHandle);
	}

	FeedbackBaseline = EDYStageFeedbackDisplay::Hidden;
	SetFeedbackDisplay(EDYStageFeedbackDisplay::Hidden);
}

void ADYStagePresentation::SynchronizeFromDirector()
{
	if (!PuzzleDirector || !StageEnvironment)
	{
		UE_LOG(
			LogDengYingShanHai,
			Error,
			TEXT("Stage Presentation %s requires explicit PuzzleDirector and StageEnvironment references."),
			*GetNameSafe(this));
		return;
	}

	const bool bGuardSequence = PuzzleDirector->IsActSequenceEnabled();
	const FGuid OperationToken = PuzzleDirector->ActivationToken;
	HandleActSequenceChanged(PuzzleDirector->GetActSequenceSnapshot());
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	const FName PuzzleId = PuzzleDirector->GetCurrentPuzzleId();
	const FDYEvaluationResult Snapshot = PuzzleDirector->GetLastEvaluation();
	if (Snapshot.State == EDYPuzzleRuntimeState::Resolved)
	{
		if (PlayerActDisplay.bSequenceEnabled && PlayerActDisplay.Phase == EDYActSequencePhase::Complete)
		{
			if (bEnableFiveStateDevEnvironment) { ApplyFiveStateEnvironment(PlayerActDisplay); }
			else { StageEnvironment->ApplyState(EDYStageEnvironmentState::ChaseAwakened); }
			if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
			UpdateBaselineDisplay(EDYPuzzleFeedbackState::Resolved);
			return; // Synchronization must never replay the finished authored cue.
		}
		// A late listener cannot synthesize historical Staff geometry from an already
		// animated pose. Only the original live Resolve event establishes that capture.
		ApplyResolvedPresentation(PuzzleId, Snapshot);
		return;
	}
	if (Snapshot.State == EDYPuzzleRuntimeState::Inactive)
	{
		// Presentation may BeginPlay before the Director. Establish a safe visual
		// baseline now, but let OnPuzzleActivated emit the cue exactly once later.
		bHasForwardedFeedback = false;
		LastForwardedFeedback = EDYPuzzleFeedbackState::InvalidSample;
		ResetFeedbackDisplay();
		if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
		StageEnvironment->ResetToDormant();
		return;
	}

	ApplyActivatedPresentation(PuzzleId);
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	ApplyEvaluationPresentation(Snapshot);
}

void ADYStagePresentation::BindDirector()
{
	if (!PuzzleDirector)
	{
		return;
	}

	PuzzleDirector->OnPuzzleActivated.AddUniqueDynamic(this, &ADYStagePresentation::HandlePuzzleActivated);
	PuzzleDirector->OnEvaluationUpdated.AddUniqueDynamic(this, &ADYStagePresentation::HandleEvaluationUpdated);
	PuzzleDirector->OnHoldStarted.AddUniqueDynamic(this, &ADYStagePresentation::HandleHoldStarted);
	PuzzleDirector->OnHoldCanceled.AddUniqueDynamic(this, &ADYStagePresentation::HandleHoldCanceled);
	PuzzleDirector->OnPuzzleResolved.AddUniqueDynamic(this, &ADYStagePresentation::HandlePuzzleResolved);
	UE_LOG(LogDengYingShanHai, Display, TEXT("[StagePresentation] bound director %s on %s."),
		*PuzzleDirector->GetName(), *GetName());
	InvalidationDirector = PuzzleDirector;
	if (PuzzleDirector->IsActSequenceEnabled())
	{
		if (!PuzzleDirector->RegisterSequencePresentation(this))
		{
			UE_LOG(LogDengYingShanHai, Error, TEXT("A different Presentation already owns this Director's sequence callbacks."));
		}
		ActSequenceHandle = PuzzleDirector->OnActSequenceChanged().AddUObject(this, &ADYStagePresentation::HandleActSequenceChanged);
	}
	ResolvedInvalidationHandle = PuzzleDirector->OnResolvedSnapshotInvalidated().AddUObject(
		this, &ADYStagePresentation::HandleResolvedSnapshotInvalidated);
}

void ADYStagePresentation::UnbindDirector()
{
	if (ADYPuzzleDirector* Bound = InvalidationDirector.Get())
	{
		Bound->OnResolvedSnapshotInvalidated().Remove(ResolvedInvalidationHandle);
		Bound->OnActSequenceChanged().Remove(ActSequenceHandle);
		Bound->UnregisterSequencePresentation(this);
	}
	ActSequenceHandle.Reset();
	InvalidationDirector.Reset();
	ResolvedInvalidationHandle.Reset();
	if (!PuzzleDirector)
	{
		return;
	}

	PuzzleDirector->OnPuzzleActivated.RemoveDynamic(this, &ADYStagePresentation::HandlePuzzleActivated);
	PuzzleDirector->OnEvaluationUpdated.RemoveDynamic(this, &ADYStagePresentation::HandleEvaluationUpdated);
	PuzzleDirector->OnHoldStarted.RemoveDynamic(this, &ADYStagePresentation::HandleHoldStarted);
	PuzzleDirector->OnHoldCanceled.RemoveDynamic(this, &ADYStagePresentation::HandleHoldCanceled);
	PuzzleDirector->OnPuzzleResolved.RemoveDynamic(this, &ADYStagePresentation::HandlePuzzleResolved);
}

void ADYStagePresentation::ApplyActivatedPresentation(const FName PuzzleId)
{
	const bool bGuardSequence = IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled();
	const FGuid OperationToken = IsValid(PuzzleDirector) ? PuzzleDirector->ActivationToken : FGuid();
	CancelActTransition();
	ResetStaffPresentation();
	bHasForwardedFeedback = false;
	LastForwardedFeedback = EDYPuzzleFeedbackState::InvalidSample;
	// A new activation must not inherit a stale Complete or Interrupted from the
	// previous puzzle, and must not leave an old one-shot running.
	ResetFeedbackDisplay();
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	if (StageEnvironment)
	{
		if (IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled())
		{
			const auto State = PuzzleDirector->GetActSequenceSnapshot();
			if (bEnableFiveStateDevEnvironment) { ApplyFiveStateEnvironment(State); }
			else { StageEnvironment->ApplyState(State.ActIndex <= 0 ? EDYStageEnvironmentState::Dormant
				: State.ActIndex == 1 ? EDYStageEnvironmentState::SunAwakened : EDYStageEnvironmentState::ChaseAwakened); }
		}
		else { StageEnvironment->ResetToDormant(); }
	}
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	ReceivePuzzleActivated(PuzzleId);
}

void ADYStagePresentation::ApplyResolvedPresentation(
	const FName PuzzleId,
	const FDYEvaluationResult& ResolvedSnapshot)
{
	const bool bGuardSequence = IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled();
	const FGuid OperationToken = IsValid(PuzzleDirector) ? PuzzleDirector->ActivationToken : FGuid();
	if (StageEnvironment)
	{
		const auto State = IsValid(PuzzleDirector) ? PuzzleDirector->GetActSequenceSnapshot() : FDYActSequenceSnapshot();
		if (bEnableFiveStateDevEnvironment && State.bSequenceEnabled) { ApplyFiveStateEnvironment(State); }
		else { StageEnvironment->ApplyState(State.bSequenceEnabled
			? (State.ActIndex == 0 ? EDYStageEnvironmentState::SunAwakened : EDYStageEnvironmentState::ChaseAwakened)
			: ResolvedEnvironmentState); }
	}
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	UpdateBaselineDisplay(EDYPuzzleFeedbackState::Resolved);
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	ReceivePuzzleResolved(PuzzleId, ResolvedSnapshot);
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	ScheduleActTransition();
}

void ADYStagePresentation::HandlePuzzleActivated(const FName PuzzleId)
{
	if (!IsIncomingPuzzleNotificationCurrent()
		|| (IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled() && PuzzleId != PuzzleDirector->GetCurrentPuzzleId())) { return; }
	ApplyActivatedPresentation(PuzzleId);
}

void ADYStagePresentation::HandleEvaluationUpdated(const FDYEvaluationResult& Result)
{
	if (!IsIncomingPuzzleNotificationCurrent()) { return; }
	ApplyEvaluationPresentation(Result);
}

void ADYStagePresentation::ApplyEvaluationPresentation(const FDYEvaluationResult& Result)
{
	const bool bGuardSequence = IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled();
	const FGuid OperationToken = IsValid(PuzzleDirector) ? PuzzleDirector->ActivationToken : FGuid();
	const FName PuzzleId = PuzzleDirector ? PuzzleDirector->GetCurrentPuzzleId() : NAME_None;
	// The Director broadcasts OnEvaluationUpdated before OnHoldCanceled, and a canceled
	// sample reports Near/Far rather than InsideTarget. The overlay is therefore raised
	// here, before the de-duplication early-out, so a repeated Feedback value can never
	// swallow the interruption.
	// Order matters: the overlay is raised first so the baseline update below sees an
	// active override and stays silent instead of overwriting it.
	if (Result.bHoldCanceled)
	{
		ShowInterruptedTemporarily();
	}
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }

	UpdateBaselineDisplay(Result.Feedback);
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	// Readiness can change while Near remains Near; the hold clock also advances
	// within Holding. Project every existing evaluation, dedup only the display data.
	SetPlayerAlignmentDisplay(BuildPlayerAlignmentDisplay(Result, bEnablePlayerAlignmentFeedback));
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }

	if (bHasForwardedFeedback && LastForwardedFeedback == Result.Feedback)
	{
		return;
	}

	const EDYPuzzleFeedbackState PreviousState = bHasForwardedFeedback
		? LastForwardedFeedback
		: EDYPuzzleFeedbackState::InvalidSample;
	LastForwardedFeedback = Result.Feedback;
	bHasForwardedFeedback = true;
	ReceiveFeedbackStateChanged(
		PuzzleId,
		PreviousState,
		Result.Feedback,
		Result.Progress);
}

void ADYStagePresentation::HandleHoldStarted(const FName PuzzleId)
{
	if (!IsIncomingPuzzleNotificationCurrent()
		|| (IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled() && PuzzleId != PuzzleDirector->GetCurrentPuzzleId())) { return; }
	const bool bGuardSequence = IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled();
	const FGuid OperationToken = IsValid(PuzzleDirector) ? PuzzleDirector->ActivationToken : FGuid();
	// A new hold attempt must cancel a still-running interruption overlay.
	ClearInterruptedOverlay();
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	ReceiveHoldStarted(PuzzleId);
}

void ADYStagePresentation::HandleHoldCanceled(const FName PuzzleId)
{
	if (!IsIncomingPuzzleNotificationCurrent()
		|| (IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled() && PuzzleId != PuzzleDirector->GetCurrentPuzzleId())) { return; }
	const bool bGuardSequence = IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled();
	const FGuid OperationToken = IsValid(PuzzleDirector) ? PuzzleDirector->ActivationToken : FGuid();
	// Idempotent second confirmation: the overlay was already raised from the
	// evaluation sample, so this only guarantees visibility even if a future Director
	// reports the cancellation without a matching sample.
	ShowInterruptedTemporarily();
	if (bGuardSequence && !IsSequenceOperationCurrent(OperationToken)) { return; }
	ReceiveHoldCanceled(PuzzleId);
}

void ADYStagePresentation::HandlePuzzleResolved(
	const FName PuzzleId,
	const FDYEvaluationResult& ResolvedSnapshot)
{
	UE_LOG(LogDengYingShanHai, Display, TEXT("[StagePresentation] OnPuzzleResolved id=%s current=%d currentPuzzle=%s"),
		*PuzzleId.ToString(), IsIncomingPuzzleNotificationCurrent() ? 1 : 0,
		IsValid(PuzzleDirector) ? *PuzzleDirector->GetCurrentPuzzleId().ToString() : TEXT("none"));
	if (!IsIncomingPuzzleNotificationCurrent()
		|| (IsValid(PuzzleDirector) && PuzzleDirector->IsActSequenceEnabled() && PuzzleId != PuzzleDirector->GetCurrentPuzzleId())) { return; }
	CaptureResolvedStaffPresentation(PuzzleId);
	ApplyResolvedPresentation(PuzzleId, ResolvedSnapshot);
}

void ADYStagePresentation::HandleActSequenceChanged(const FDYActSequenceSnapshot& Snapshot)
{
	if (!bStaffPresentationRuntimeActive || !IsValid(PuzzleDirector) || PuzzleDirector->GetWorld() != GetWorld()) { return; }
	const auto Current = PuzzleDirector->GetActSequenceSnapshot();
	// A prior listener may reset during a native multicast. Never let the remaining
	// old notification overwrite the newer settled phase from that nested broadcast.
	if (Snapshot.bSequenceEnabled != Current.bSequenceEnabled || Snapshot.ActIndex != Current.ActIndex
		|| Snapshot.ActCount != Current.ActCount || Snapshot.Phase != Current.Phase
		|| !Snapshot.ActTitle.EqualTo(Current.ActTitle)) { return; }
	PlayerActDisplay = Snapshot;
	if (IsValid(StageEnvironment) && PuzzleDirector->IsCampaignEnabled())
	{
		StageEnvironment->ApplyChapterScenery(Snapshot.ChapterIndex, Snapshot.ActIndex,
			Snapshot.Phase != EDYActSequencePhase::Playing);
	}
	if (bEnableFiveStateDevEnvironment)
	{
		const FGuid EnvironmentOperationToken = PuzzleDirector->ActivationToken;
		ApplyFiveStateEnvironment(Snapshot);
		if (!IsSequenceOperationCurrent(EnvironmentOperationToken)) { return; }
		// Complete can preserve the activation token. An environment listener may
		// accept a fully verified finale during late synchronization; do not forward
		// the older AwaitingFinale payload after its nested Complete notification.
		const auto Settled = PuzzleDirector->GetActSequenceSnapshot();
		if (Snapshot.bSequenceEnabled != Settled.bSequenceEnabled || Snapshot.ActIndex != Settled.ActIndex
			|| Snapshot.ActCount != Settled.ActCount || Snapshot.Phase != Settled.Phase
			|| !Snapshot.ActTitle.EqualTo(Settled.ActTitle)) { return; }
	}
	if (Snapshot.Phase != EDYActSequencePhase::Playing)
	{
		const FGuid OperationToken = PuzzleDirector->ActivationToken;
		SetPlayerAlignmentDisplay(FDYPlayerAlignmentDisplay());
		if (!IsSequenceOperationCurrent(OperationToken)) { return; }
	}
	PlayerActDisplayChanged.Broadcast(Snapshot); // Cosmetic snapshot only, no writes after listener reentry.
}

bool ADYStagePresentation::IsSequenceOperationCurrent(const FGuid& Token) const
{
	return bStaffPresentationRuntimeActive && IsValid(this) && IsValid(PuzzleDirector)
		&& PuzzleDirector->GetWorld() == GetWorld() && !PuzzleDirector->bEndingPlay
		&& PuzzleDirector->ActivationToken == Token;
}

bool ADYStagePresentation::IsIncomingPuzzleNotificationCurrent() const
{
	if (!IsValid(PuzzleDirector) || !PuzzleDirector->IsActSequenceEnabled()) { return true; }
	return PuzzleDirector->PuzzleNotificationToken.IsValid()
		&& IsSequenceOperationCurrent(PuzzleDirector->PuzzleNotificationToken);
}

void ADYStagePresentation::CancelActTransition()
{
	PendingTransitionToken.Invalidate();
	if (UWorld* World = GetWorld()) { World->GetTimerManager().ClearTimer(ActTransitionTimerHandle); }
}

void ADYStagePresentation::ScheduleActTransition()
{
	if (!bStaffPresentationRuntimeActive || !IsValid(PuzzleDirector) || !GetWorld()) { return; }
	const auto State = PuzzleDirector->GetActSequenceSnapshot();
	const FGuid Token = PuzzleDirector->GetResolvedPuzzleSnapshot().Token;
	if (!State.bSequenceEnabled || State.Phase != EDYActSequencePhase::AwaitingTransition
		|| !PuzzleDirector->IsResolvedTokenCurrent(Token)) { return; }
	if (PendingTransitionToken == Token && GetWorld()->GetTimerManager().IsTimerActive(ActTransitionTimerHandle)) { return; }
	CancelActTransition();
	PendingTransitionToken = Token;
	FTimerDelegate Callback = FTimerDelegate::CreateWeakLambda(this, [this, Token]()
	{
		if (!bStaffPresentationRuntimeActive || PendingTransitionToken != Token || !IsValid(PuzzleDirector)) { return; }
		PendingTransitionToken.Invalidate(); // Consume before the Director emits any callback.
		PuzzleDirector->AcceptActTransition(this, Token);
	});
	GetWorld()->GetTimerManager().SetTimer(ActTransitionTimerHandle, Callback,
		FMath::Max(DevActTransitionSeconds, 0.1f), false);
}

bool ADYStagePresentation::HasCompletedForestForToken(const FGuid& Token) const
{
	ADYForestPresentationActor* Forest = OwnedForestActor.Get();
	if (!IsStaffPresentationTokenCurrent(Token) || Token != OwnedForestToken || !IsContactSceneUnchanged()
		|| !IsValid(Forest) || Forest->GetWorld() != GetWorld() || !Forest->IsSessionOwner(this, Token)) { return false; }
	const auto Sample = Forest->GetForestGeometrySample();
	const auto Meshes = Forest->GetBranchMeshComponents();
	if (Sample.Status != EDYForestGeometryStatus::Valid || Sample.ContactToken != Token
		|| Sample.Branches.IsEmpty() || Sample.Branches.Num() != Meshes.Num()) { return false; }
	for (int32 Index = 0; Index < Meshes.Num(); ++Index)
	{
		const auto& Branch = Sample.Branches[Index];
		const UStaticMeshComponent* Mesh = Meshes[Index];
		if (!Branch.bVisible || Branch.Portion < 1.0 - UE_DOUBLE_SMALL_NUMBER || !IsValid(Mesh)
			|| Mesh->GetWorld() != GetWorld() || !Mesh->IsRegistered() || !Mesh->IsVisible() || Mesh->bHiddenInGame
			|| Mesh->GetOwner() != Forest || Forest->IsHidden() || !Mesh->CastShadow || Mesh->GetStaticMesh() != Forest->SessionMesh
			|| !Mesh->GetComponentTransform().Equals(Branch.MeshWorldTransform, UE_DOUBLE_SMALL_NUMBER)) { return false; }
	}
	return true;
}

bool ADYStagePresentation::SubmitForestFinaleCompletion(const FGuid& Token)
{
	if (!bStaffPresentationRuntimeActive || !IsValid(PuzzleDirector) || !PuzzleDirector->IsActSequenceEnabled()
		|| !PuzzleDirector->IsFinalSequenceAct() || !HasCompletedForestForToken(Token)) { return false; }
	// The native resource proof is never accepted through a public Director Blueprint node.
	return PuzzleDirector->AcceptFinaleCompletion(this, Token);
}
