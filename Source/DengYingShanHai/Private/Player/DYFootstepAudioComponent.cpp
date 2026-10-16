#include "Player/DYFootstepAudioComponent.h"

#include "Components/AudioComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundAttenuation.h"

FDYFootstepDistanceDecision FDYFootstepDistanceGate::Observe(const FVector& OldLocation, const FVector& NewLocation,
	double DeltaSeconds, bool bGrounded, bool bTeleported, double StepDistanceCentimeters, double MaximumSpeedCentimetersPerSecond)
{
	FDYFootstepDistanceDecision Result;
	// A long stalled update is not permission to emit a catch-up burst. Numerical faults fail silent.
	if (OldLocation.ContainsNaN() || NewLocation.ContainsNaN() || !FMath::IsFinite(DeltaSeconds)
		|| DeltaSeconds <= 0.0 || DeltaSeconds > 0.5 || !FMath::IsFinite(StepDistanceCentimeters)
		|| StepDistanceCentimeters < 1.0 || !FMath::IsFinite(MaximumSpeedCentimetersPerSecond)
		|| MaximumSpeedCentimetersPerSecond < 0.0)
	{
		ClearMotion();
		Result.bDiscontinuity = true;
		return Result;
	}

	const bool bOutsideUpdateJump = bHasLastLocation && FVector::Distance(OldLocation, LastLocation) > 2.0;
	const double Distance = FVector::Dist2D(OldLocation, NewLocation);
	const bool bImplausibleMove = Distance > MaximumSpeedCentimetersPerSecond * DeltaSeconds * 1.5 + 2.0;
	LastLocation = NewLocation;
	bHasLastLocation = true;
	if (bTeleported || bOutsideUpdateJump || bImplausibleMove)
	{
		AccumulatedDistance = 0.0;
		bMoving = false;
		bHasMotionStartLocation = false;
		Result.bDiscontinuity = true;
		return Result;
	}
	if (!bGrounded || Distance <= 0.001)
	{
		// Stationary (including input blocked by a wall), airborne and landing updates carry no debt.
		Result.bStopped = bMoving;
		bMoving = false;
		bHasMotionStartLocation = false;
		AccumulatedDistance = 0.0;
		return Result;
	}

	if (!bMoving)
	{
		if (!bHasMotionStartLocation)
		{
			MotionStartLocation = OldLocation;
			bHasMotionStartLocation = true;
		}
		// Pending onset is NET travel, so small collision oscillations cannot add up to a fake step.
		AccumulatedDistance = FVector::Dist2D(MotionStartLocation, NewLocation);
		const double StartDistance = FMath::Min(MinimumStartDistanceCentimeters, StepDistanceCentimeters);
		if (AccumulatedDistance + UE_DOUBLE_SMALL_NUMBER < StartDistance) { return Result; }
		bMoving = true;
		Result.bStarted = true;
		Result.bEmit = true;
		// Preserve overshoot relative to the exact onset threshold, independent of update partition.
		AccumulatedDistance = FMath::Fmod(FMath::Max(AccumulatedDistance - StartDistance, 0.0), StepDistanceCentimeters);
	}
	else
	{
		AccumulatedDistance += Distance;
		if (AccumulatedDistance + UE_DOUBLE_SMALL_NUMBER >= StepDistanceCentimeters)
		{
			Result.bEmit = true;
			AccumulatedDistance = FMath::Fmod(AccumulatedDistance, StepDistanceCentimeters);
		}
	}
	if (Result.bEmit)
	{
		Result.bLeft = bNextLeft;
		bNextLeft = !bNextLeft;
		// At most one request per update, even if an onset/low-FPS update crosses several strides.
		if (AccumulatedDistance < UE_DOUBLE_SMALL_NUMBER) { AccumulatedDistance = 0.0; }
	}
	return Result;
}

void FDYFootstepDistanceGate::ClearMotion()
{
	AccumulatedDistance = 0.0;
	LastLocation = FVector::ZeroVector;
	bHasLastLocation = false;
	bMoving = false;
	bHasMotionStartLocation = false;
	MotionStartLocation = FVector::ZeroVector;
}

void FDYFootstepDistanceGate::Reset()
{
	ClearMotion();
	bNextLeft = true;
}

UDYFootstepAudioComponent::UDYFootstepAudioComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	bAutoActivate = false;
}

float UDYFootstepAudioComponent::SanitizeReverbSendLevel(float InLevel)
{
	return FMath::IsFinite(InLevel) ? FMath::Clamp(InLevel, 0.0f, 1.0f) : 0.0f;
}

void UDYFootstepAudioComponent::BeginPlay()
{
	Super::BeginPlay();
	Gate.Reset();
	Diagnostics = {};
	bSkipNextMovementUpdate = false;
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	UWorld* World = GetWorld();
	if (!bEnableDevelopmentFootsteps || !IsValid(Character) || !World || !World->IsGameWorld()
		|| Character->GetWorld() != World || !Character->GetCharacterMovement())
	{
		return;
	}

	FootstepVoice = NewObject<UAudioComponent>(Character,
		MakeUniqueObjectName(Character, UAudioComponent::StaticClass(), TEXT("DYFootstepVoice")));
	Character->AddOwnedComponent(FootstepVoice);
	FootstepVoice->bAutoActivate = false;
	FootstepVoice->bAutoDestroy = false;
	FootstepVoice->bStopWhenOwnerDestroyed = true;
	// Allow applying native attenuation settings, while the actual source remains unattenuated 2D.
	FootstepVoice->bAllowSpatialization = true;
	FootstepVoice->bOverrideAttenuation = true;
	FootstepVoice->AttenuationOverrides.bSpatialize = false;
	FootstepVoice->AttenuationOverrides.bAttenuate = false;
	FootstepVoice->AttenuationOverrides.bEnableReverbSend = true;
	FootstepVoice->AttenuationOverrides.ReverbSendMethod = EReverbSendMethod::Manual;
	FootstepVoice->AttenuationOverrides.ManualReverbSendLevel = SanitizeReverbSendLevel(TheatreReverbSendLevel);
	FootstepVoice->bReverb = true;
	FootstepVoice->bIsUISound = false;
	FootstepVoice->PrimaryComponentTick.bCanEverTick = false;
	FootstepVoice->SetupAttachment(Character->GetRootComponent());
	FootstepVoice->RegisterComponentWithWorld(World);

	BoundCharacter = Character;
	BoundOperator = Cast<ADYStageOperatorPawn>(Character);
	Character->OnCharacterMovementUpdated.AddUniqueDynamic(this, &UDYFootstepAudioComponent::HandleMovementUpdated);
	Character->MovementModeChangedDelegate.AddUniqueDynamic(this, &UDYFootstepAudioComponent::HandleMovementModeChanged);
	if (ADYStageOperatorPawn* Operator = BoundOperator.Get())
	{
		Operator->OnOperatorReset.AddUniqueDynamic(this, &UDYFootstepAudioComponent::HandleOperatorReset);
	}
	Diagnostics.bRuntimeActive = true;
	Diagnostics.bMuted = FParse::Param(FCommandLine::Get(), TEXT("DYAudioMuted"));
}

bool UDYFootstepAudioComponent::HasLiveCharacter() const
{
	const ACharacter* Character = BoundCharacter.Get();
	return Diagnostics.bRuntimeActive && IsValid(Character) && Character == GetOwner()
		&& Character->GetWorld() == GetWorld() && GetWorld() && GetWorld()->IsGameWorld();
}

void UDYFootstepAudioComponent::HandleMovementUpdated(float DeltaSeconds, FVector OldLocation, FVector OldVelocity)
{
	(void)OldVelocity;
	if (!HasLiveCharacter()) { DeactivateSession(); return; }
	ACharacter* Character = BoundCharacter.Get();
	UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	if (!IsValid(Movement)) { DeactivateSession(); return; }
	++Diagnostics.MovementUpdates;
	if (bSkipNextMovementUpdate)
	{
		// A landing/reset update can include travel that happened before its new movement mode.
		bSkipNextMovementUpdate = false;
		Gate.ClearMotion();
		return;
	}
	const FDYFootstepDistanceDecision Decision = Gate.Observe(OldLocation, Character->GetActorLocation(), DeltaSeconds,
		Movement->IsMovingOnGround(), Movement->bJustTeleported, StepDistanceCentimeters, Movement->GetMaxSpeed());
	if (Decision.bDiscontinuity)
	{
		++Diagnostics.Discontinuities;
		if (IsValid(FootstepVoice)) { FootstepVoice->Stop(); }
	}
	if (Decision.bStarted)
	{
		++Diagnostics.MovementStartEvents;
		Diagnostics.LastMovementStartSeconds = GetWorld()->GetTimeSeconds();
	}
	if (Decision.bStopped)
	{
		++Diagnostics.StopEvents;
		Diagnostics.LastStopSeconds = GetWorld()->GetTimeSeconds();
		// End only this dry source; the independently owned room effect may decay naturally.
		if (IsValid(FootstepVoice)) { FootstepVoice->Stop(); }
	}
	if (!Decision.bEmit) { return; }
	++Diagnostics.Steps;
	Diagnostics.bLastStepLeft = Decision.bLeft;
	USoundBase* Sound = Decision.bLeft ? LeftSound.Get() : RightSound.Get();
	if (Diagnostics.bMuted || !IsValid(Sound) || !IsValid(FootstepVoice) || !FootstepVoice->IsRegistered()
		|| !FMath::IsFinite(Volume)) { return; }
	FootstepVoice->Stop();
	FootstepVoice->SetSound(Sound);
	FootstepVoice->SetVolumeMultiplier(static_cast<float>(FMath::Clamp(Volume, 0.0, 2.0)));
	FootstepVoice->Play();
	Diagnostics.LastPlaybackStartSeconds = GetWorld()->GetTimeSeconds();
	++Diagnostics.PlaybackStarts; // Request count; not a claim about operating-system output or human hearing.
}

void UDYFootstepAudioComponent::HandleMovementModeChanged(ACharacter* Character, EMovementMode PreviousMode, uint8 PreviousCustomMode)
{
	(void)PreviousMode;
	(void)PreviousCustomMode;
	if (Character != BoundCharacter.Get() || !HasLiveCharacter()) { return; }
	ClearMotionAndStop();
	bSkipNextMovementUpdate = true;
}

void UDYFootstepAudioComponent::HandleOperatorReset(EDYOperatorResetReason Reason, int32 ResetCount)
{
	(void)Reason;
	(void)ResetCount;
	if (!HasLiveCharacter()) { return; }
	++Diagnostics.ResetEvents;
	ClearMotionAndStop();
	bSkipNextMovementUpdate = true;
}

void UDYFootstepAudioComponent::ClearMotionAndStop()
{
	Gate.ClearMotion();
	if (IsValid(FootstepVoice)) { FootstepVoice->Stop(); }
}

void UDYFootstepAudioComponent::SetMuted(bool bInMuted)
{
	if (Diagnostics.bMuted == bInMuted) { return; }
	Diagnostics.bMuted = bInMuted;
	ClearMotionAndStop();
}

FDYFootstepAudioDiagnostics UDYFootstepAudioComponent::GetFootstepDiagnostics() const
{
	FDYFootstepAudioDiagnostics Result = Diagnostics;
	Result.AccumulatedDistanceCentimeters = Gate.GetAccumulatedDistance();
	Result.bMoving = Gate.IsMoving();
	return Result;
}

void UDYFootstepAudioComponent::DeactivateSession()
{
	Diagnostics.bRuntimeActive = false;
	if (ACharacter* Character = BoundCharacter.Get())
	{
		Character->OnCharacterMovementUpdated.RemoveDynamic(this, &UDYFootstepAudioComponent::HandleMovementUpdated);
		Character->MovementModeChangedDelegate.RemoveDynamic(this, &UDYFootstepAudioComponent::HandleMovementModeChanged);
	}
	if (ADYStageOperatorPawn* Operator = BoundOperator.Get())
	{
		Operator->OnOperatorReset.RemoveDynamic(this, &UDYFootstepAudioComponent::HandleOperatorReset);
	}
	BoundCharacter.Reset();
	BoundOperator.Reset();
	Gate.Reset();
	bSkipNextMovementUpdate = false;
	if (IsValid(FootstepVoice))
	{
		FootstepVoice->Stop();
		FootstepVoice->DestroyComponent();
	}
	FootstepVoice = nullptr;
}

void UDYFootstepAudioComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	DeactivateSession();
	Super::EndPlay(EndPlayReason);
}
