#include "Interaction/DYInteractionComponent.h"

#include "DengYingShanHai.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Interaction/DYControllable.h"
#include "Interaction/DYControlTypes.h"
#include "TimerManager.h"

#if !UE_BUILD_SHIPPING
#include "DrawDebugHelpers.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#endif

#if WITH_DEV_AUTOMATION_TESTS
void FDYFocusAutomationSeam::EvaluateFocus(
	UDYInteractionComponent& Component,
	const FVector& ViewLocation,
	const FRotator& ViewRotation,
	const FVector& PawnLocation)
{
	// Test-only bridge to the real private helper. No public API is added for testing.
	Component.EvaluateFocus(ViewLocation, ViewRotation, PawnLocation);
}

bool FDYFocusAutomationSeam::HasActiveFocusTimer(UDYInteractionComponent& Component)
{
	UWorld* World = Component.GetWorld();
	return World && World->GetTimerManager().IsTimerActive(Component.FocusTimerHandle);
}
#endif

UDYInteractionComponent::UDYInteractionComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UDYInteractionComponent::BeginPlay()
{
	Super::BeginPlay();

#if !UE_BUILD_SHIPPING
	// Same explicit opt-in switch the Puzzle Director uses. Absent in Shipping.
	bFocusDebugEnabled = FParse::Param(FCommandLine::Get(), TEXT("DYDebug"));
#endif

	UpdateFocusedActor();
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().SetTimer(
			FocusTimerHandle,
			this,
			&UDYInteractionComponent::UpdateFocusedActor,
			FocusRefreshInterval,
			true);
	}
}

void UDYInteractionComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(FocusTimerHandle);
	}
	EndActiveControl();
	SetFocusedActor(nullptr);
	Super::EndPlay(EndPlayReason);
}

bool UDYInteractionComponent::ToggleControl()
{
	// One line per control-toggle request, never per frame. ToggleControl can be reached
	// from more than the physical E key, so this does not claim a key press happened.
	// An open session is either a live controlled actor or a stale one whose exit has
	// not been broadcast yet (the controlled actor was destroyed while manipulated).
	// Routing both through EndActiveControl keeps the exit contract single-sourced, so
	// pressing the toggle again can never strand the pawn in manipulation mode.
#if !UE_BUILD_SHIPPING
	const bool bWasControlling = ActiveControlledActor.IsValid() || bPendingControlExitNotify;
	AActor* FocusBefore = FocusedActor.Get();
#endif

	if (ActiveControlledActor.IsValid() || bPendingControlExitNotify)
	{
		EndActiveControl();
#if !UE_BUILD_SHIPPING
		if (bFocusDebugEnabled)
		{
			UE_LOG(
				LogDengYingShanHai,
				Display,
				TEXT("InteractDebug ControlToggle requested action=Release FocusBefore=%s ActiveAfter=%d"),
				FocusBefore ? *FocusBefore->GetName() : TEXT("None"),
				ActiveControlledActor.IsValid() ? 1 : 0);
		}
#endif
		return false;
	}

	AActor* Candidate = FocusedActor.Get();
	APawn* OwnerPawn = GetOwnerPawn();
	if (!Candidate || !OwnerPawn || !Candidate->Implements<UDYControllable>())
	{
#if !UE_BUILD_SHIPPING
		if (bFocusDebugEnabled)
		{
			UE_LOG(
				LogDengYingShanHai,
				Display,
				TEXT("InteractDebug ControlToggle requested action=Rejected reason=%s FocusBefore=%s"),
				!Candidate ? TEXT("NoFocusCandidate")
				: (!OwnerPawn ? TEXT("NoOwnerPawn") : TEXT("NotControllable")),
				Candidate ? *Candidate->GetName() : TEXT("None"));
		}
#endif
		return false;
	}

	FDYControlContext Context;
	Context.InstigatorPawn = OwnerPawn;
	if (!IDYControllable::Execute_CanBeginControl(Candidate, Context))
	{
#if !UE_BUILD_SHIPPING
		if (bFocusDebugEnabled)
		{
			UE_LOG(
				LogDengYingShanHai,
				Display,
				TEXT("InteractDebug ControlToggle requested action=Rejected reason=CanBeginControlRefused Candidate=%s"),
				*Candidate->GetName());
		}
#endif
		return false;
	}

	IDYControllable::Execute_BeginControl(Candidate, Context);
	ActiveControlledActor = Candidate;
	SetFocusedActor(nullptr);
	bPendingControlExitNotify = true;
	OnControlStateChanged.Broadcast(Candidate, true);
#if !UE_BUILD_SHIPPING
	if (bFocusDebugEnabled)
	{
		UE_LOG(
			LogDengYingShanHai,
			Display,
			TEXT("InteractDebug ControlToggle requested action=EnterManipulate Candidate=%s WasControlling=%d ActiveAfter=1"),
			*Candidate->GetName(),
			bWasControlling ? 1 : 0);
	}
#endif
	return true;
}

void UDYInteractionComponent::EndActiveControl()
{
	if (!bPendingControlExitNotify)
	{
		// No open control session, or its exit was already broadcast. Without this
		// guard a repeated EndActiveControl would notify listeners more than once.
		return;
	}

	AActor* ControlledActor = ActiveControlledActor.Get();
	if (!ControlledActor)
	{
		// The weak reference expired: the controlled actor was destroyed while being
		// manipulated. The previous early return skipped the exit broadcast entirely,
		// leaving the operator pawn in manipulation mode with nothing left to release.
		// Clear the stale handle and notify exactly once with a null actor so listeners
		// (e.g. SetManipulationMode(false)) can restore the explore input mode.
		ActiveControlledActor.Reset();
		bPendingControlExitNotify = false;
		OnControlStateChanged.Broadcast(nullptr, false);
		UpdateFocusedActor();
		return;
	}

	if (ControlledActor->Implements<UDYControllable>())
	{
		FDYControlContext Context;
		Context.InstigatorPawn = GetOwnerPawn();
		IDYControllable::Execute_EndControl(ControlledActor, Context);
	}

	ActiveControlledActor.Reset();
	bPendingControlExitNotify = false;
	OnControlStateChanged.Broadcast(ControlledActor, false);
	UpdateFocusedActor();
}

void UDYInteractionComponent::ApplyPrimaryAxis(const double AxisValue, const double DeltaSeconds)
{
	AActor* ControlledActor = ActiveControlledActor.Get();
	if (!ControlledActor || !ControlledActor->Implements<UDYControllable>())
	{
		return;
	}

	FDYControlIntent Intent;
	Intent.Channel = EDYControlChannel::PrimaryAxis;
	Intent.Value = FVector2D(AxisValue, 0.0);
	Intent.DeltaSeconds = FMath::Max(0.0, DeltaSeconds);
	Intent.Phase = EDYControlPhase::Ongoing;
	IDYControllable::Execute_ApplyControlIntent(ControlledActor, Intent);
}

bool UDYInteractionComponent::ResetActiveControl()
{
	AActor* ControlledActor = ActiveControlledActor.Get();
	if (!ControlledActor || !ControlledActor->Implements<UDYControllable>())
	{
		return false;
	}

	FDYControlContext Context;
	Context.InstigatorPawn = GetOwnerPawn();
	IDYControllable::Execute_ResetControlState(ControlledActor, Context);
	return true;
}

void UDYInteractionComponent::UpdateFocusedActor()
{
	// Finish an interrupted control session exactly once: the controlled actor was
	// destroyed while manipulated and its exit broadcast is still pending. The focus
	// timer is the one periodic observer that runs without any player input, so the
	// pawn leaves manipulation mode even if the player never presses the toggle again.
	// EndActiveControl re-enters this function once the notify flag is cleared.
	if (bPendingControlExitNotify && !ActiveControlledActor.IsValid())
	{
		EndActiveControl();
		return;
	}

	if (ActiveControlledActor.IsValid())
	{
		return;
	}

	APawn* OwnerPawn = GetOwnerPawn();
	APlayerController* PlayerController = OwnerPawn ? Cast<APlayerController>(OwnerPawn->GetController()) : nullptr;
	if (!OwnerPawn || !PlayerController)
	{
		SetFocusedActor(nullptr);
		return;
	}

	FVector ViewLocation;
	FRotator ViewRotation;
	PlayerController->GetPlayerViewPoint(ViewLocation, ViewRotation);
	EvaluateFocus(ViewLocation, ViewRotation, OwnerPawn->GetActorLocation());
}

void UDYInteractionComponent::EvaluateFocus(
	const FVector& ViewLocation,
	const FRotator& ViewRotation,
	const FVector& PawnLocation)
{
	APawn* OwnerPawn = GetOwnerPawn();
	UWorld* World = GetWorld();
	if (!OwnerPawn || !World)
	{
		SetFocusedActor(nullptr);
		return;
	}

	// The third-person camera sits behind the operator, so a trace measured from the
	// viewpoint with the operator's own radius can expire before reaching an object the
	// operator can legitimately walk up to. Compensate for the camera-to-operator
	// offset; FocusDistance keeps its meaning as the operator's real reach.
	const double TraceLength = ComputeFocusTraceLength(ViewLocation, PawnLocation, FocusDistance);
	FVector TraceEnd = ViewLocation + ViewRotation.Vector() * TraceLength;

	FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(DYInteractionFocus), false, OwnerPawn);
	// Center ray still decides occlusion. Four rays 7° off it may pick a lamp or puppet
	// the crosshair only just missed, and only when that hit is closer than the center
	// hit, so a wall on the crosshair cannot be seen through.
	constexpr float FocusSlackDegrees = 7.0f;
	const FRotator SlackRays[] = {
		ViewRotation,
		ViewRotation + FRotator(FocusSlackDegrees, 0.0f, 0.0f),
		ViewRotation + FRotator(-FocusSlackDegrees, 0.0f, 0.0f),
		ViewRotation + FRotator(0.0f, FocusSlackDegrees, 0.0f),
		ViewRotation + FRotator(0.0f, -FocusSlackDegrees, 0.0f),
	};
	FHitResult Hit;
	double CenterDistance = TNumericLimits<double>::Max();
	bool bChose = false;
	for (int32 RayIndex = 0; RayIndex < UE_ARRAY_COUNT(SlackRays); ++RayIndex)
	{
		const FVector RayEnd = ViewLocation + SlackRays[RayIndex].Vector() * TraceLength;
		FHitResult RayHit;
		if (!World->LineTraceSingleByChannel(RayHit, ViewLocation, RayEnd, ECC_Visibility, QueryParams))
		{
			continue;
		}
		if (RayIndex == 0)
		{
			Hit = RayHit;
			CenterDistance = RayHit.Distance;
			bChose = true;
			AActor* CenterActor = RayHit.GetActor();
			if (CenterActor
				&& CenterActor->Implements<UDYControllable>()
				&& IsWithinFocusDistance(PawnLocation, CenterActor->GetActorLocation(), FocusDistance))
			{
				FDYControlContext CenterContext;
				CenterContext.InstigatorPawn = OwnerPawn;
				if (IDYControllable::Execute_CanBeginControl(CenterActor, CenterContext))
				{
					TraceEnd = RayEnd;
					break;
				}
			}
			continue;
		}
		if (RayHit.Distance >= CenterDistance) { continue; }
		AActor* SideActor = RayHit.GetActor();
		if (!SideActor
			|| !SideActor->Implements<UDYControllable>()
			|| !IsWithinFocusDistance(PawnLocation, SideActor->GetActorLocation(), FocusDistance))
		{
			continue;
		}
		FDYControlContext SideContext;
		SideContext.InstigatorPawn = OwnerPawn;
		if (!IDYControllable::Execute_CanBeginControl(SideActor, SideContext)) { continue; }
		Hit = RayHit;
		CenterDistance = RayHit.Distance;
		TraceEnd = RayEnd;
		bChose = true;
	}
	if (!bChose)
	{
		Hit = FHitResult();
	}

	AActor* Candidate = Hit.GetActor();
	// The trace establishes line of sight; this gate establishes the operator radius.
	// Both must hold, so neither the camera boom nor the camera position can widen reach.
	const bool bHasCandidate = Candidate != nullptr;
	const bool bCandidateIsControllable = bHasCandidate && Candidate->Implements<UDYControllable>();
	const FVector CandidateLocation = bHasCandidate ? Candidate->GetActorLocation() : PawnLocation;
	const bool bWithinReach = bHasCandidate
		&& IsWithinFocusDistance(PawnLocation, CandidateLocation, FocusDistance);

	bool bCanBeginControl = false;
	if (bHasCandidate && bCandidateIsControllable && bWithinReach)
	{
		FDYControlContext Context;
		Context.InstigatorPawn = OwnerPawn;
		bCanBeginControl = IDYControllable::Execute_CanBeginControl(Candidate, Context);
	}

#if !UE_BUILD_SHIPPING
	FDYFocusDebugState State;
	State.ViewLocation = ViewLocation;
	State.PawnLocation = PawnLocation;
	State.TraceEnd = TraceEnd;
	State.TraceLength = ComputeFocusTraceLength(ViewLocation, PawnLocation, FocusDistance);
	State.HitActor = Candidate;
	State.bControllable = bCandidateIsControllable;
	State.bWithinReach = bWithinReach;
	State.bCanBeginControl = bCanBeginControl;
	State.PawnToCandidateDistance = bHasCandidate
		? FVector::Distance(PawnLocation, CandidateLocation)
		: 0.0;
	if (!bHasCandidate)
	{
		State.RejectReason = FName(TEXT("NoHit"));
	}
	else if (!bCandidateIsControllable)
	{
		// Occlusion semantics: the first Visibility blocker wins even when it is scenery.
		State.RejectReason = FName(TEXT("BlockedByNonControllable"));
	}
	else if (!bWithinReach)
	{
		// Radius semantics: visible, but the operator is too far from it.
		State.RejectReason = FName(TEXT("BeyondOperatorReach"));
	}
	else
	{
		State.RejectReason = bCanBeginControl ? NAME_None : FName(TEXT("CanBeginControlRefused"));
	}
#endif

	SetFocusedActor(bCanBeginControl ? Candidate : nullptr);

#if !UE_BUILD_SHIPPING
	// Record the focused actor only after SetFocusedActor, so the log reports the
	// decision that actually took effect.
	State.FocusedActor = FocusedActor.Get();
	PublishFocusDebug(State);
#endif
}

#if !UE_BUILD_SHIPPING
void UDYInteractionComponent::PublishFocusDebug(const FDYFocusDebugState& State)
{
	if (!bFocusDebugEnabled)
	{
		return;
	}

	if (UWorld* World = GetWorld())
	{
		// The real trace segment, and non-persistent: the lifetime only just covers one
		// refresh window, so a stale line can never be read as the current one.
		DrawDebugLine(
			World,
			State.ViewLocation,
			State.TraceEnd,
			State.bCanBeginControl ? FColor::Green : FColor::Orange,
			false,
			static_cast<float>(FocusRefreshInterval) + 0.05f,
			0,
			1.0f);
	}

	// Throttle against what was last written, not against the current snapshot, so an
	// unchanged state logs exactly once no matter how many refreshes follow.
	if (bHasLoggedFocus
		&& LastLoggedHitActor == State.HitActor
		&& LastLoggedRejectReason == State.RejectReason
		&& LastLoggedFocusedActor == State.FocusedActor)
	{
		FocusDebugState = State;
		return;
	}

	bHasLoggedFocus = true;
	LastLoggedHitActor = State.HitActor;
	LastLoggedRejectReason = State.RejectReason;
	LastLoggedFocusedActor = State.FocusedActor;
	FocusDebugState = State;

	UE_LOG(
		LogDengYingShanHai,
		Display,
		TEXT("FocusDebug ViewLocation=(%.1f,%.1f,%.1f) PawnLocation=(%.1f,%.1f,%.1f) TraceLength=%.1f ")
		TEXT("HitActor=%s Controllable=%d PawnToCandidate=%.1f WithinReach=%d CanBeginControl=%d ")
		TEXT("FocusedActor=%s RejectReason=%s"),
		State.ViewLocation.X, State.ViewLocation.Y, State.ViewLocation.Z,
		State.PawnLocation.X, State.PawnLocation.Y, State.PawnLocation.Z,
		State.TraceLength,
		State.HitActor.IsValid() ? *State.HitActor->GetName() : TEXT("None"),
		State.bControllable ? 1 : 0,
		State.PawnToCandidateDistance,
		State.bWithinReach ? 1 : 0,
		State.bCanBeginControl ? 1 : 0,
		State.FocusedActor.IsValid() ? *State.FocusedActor->GetName() : TEXT("None"),
		*State.RejectReason.ToString());
}
#endif

void UDYInteractionComponent::SetFocusedActor(AActor* NewFocusedActor)
{
	AActor* PreviousActor = FocusedActor.Get();
	if (PreviousActor == NewFocusedActor)
	{
		return;
	}

	FocusedActor = NewFocusedActor;
	OnFocusChanged.Broadcast(PreviousActor, NewFocusedActor);
}

APawn* UDYInteractionComponent::GetOwnerPawn() const
{
	return Cast<APawn>(GetOwner());
}

double UDYInteractionComponent::ComputeFocusTraceLength(
	const FVector& ViewLocation,
	const FVector& PawnLocation,
	const double InFocusDistance)
{
	// Camera-to-operator offset plus the operator's own reach. Any point inside the
	// operator's reach sphere is at most this far from the viewpoint, so the compensated
	// length can never truncate a legitimate candidate.
	return FVector::Distance(ViewLocation, PawnLocation) + FMath::Max(InFocusDistance, 0.0);
}

bool UDYInteractionComponent::IsWithinFocusDistance(
	const FVector& PawnLocation,
	const FVector& CandidateLocation,
	const double InFocusDistance)
{
	return FVector::Distance(PawnLocation, CandidateLocation) <= FMath::Max(InFocusDistance, 0.0);
}
