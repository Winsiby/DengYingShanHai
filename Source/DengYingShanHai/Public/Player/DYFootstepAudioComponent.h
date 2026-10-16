#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Player/DYStageOperatorPawn.h"
#include "DYFootstepAudioComponent.generated.h"

class UAudioComponent;
class USoundBase;

/** A distance-clock result, not a claim about an animation's actual left/right foot. */
struct DENGYINGSHANHAI_API FDYFootstepDistanceDecision
{
	bool bEmit = false;
	bool bLeft = true;
	bool bDiscontinuity = false;
	bool bStarted = false;
	bool bStopped = false;
};

/** World-independent cadence; consumes actual grounded displacement, never input intent. */
struct DENGYINGSHANHAI_API FDYFootstepDistanceGate
{
	FDYFootstepDistanceDecision Observe(const FVector& OldLocation, const FVector& NewLocation,
		double DeltaSeconds, bool bGrounded, bool bTeleported,
		double StepDistanceCentimeters, double MaximumSpeedCentimetersPerSecond);
	void ClearMotion();
	void Reset();
	double GetAccumulatedDistance() const { return AccumulatedDistance; }
	bool IsMoving() const { return bMoving; }
	// Reject a sub-centimetre correction; do not wait a full stride before the first impact.
	static constexpr double MinimumStartDistanceCentimeters = 2.0;

private:
	double AccumulatedDistance = 0.0;
	FVector LastLocation = FVector::ZeroVector;
	bool bHasLastLocation = false;
	bool bNextLeft = true;
	bool bMoving = false;
	FVector MotionStartLocation = FVector::ZeroVector;
	bool bHasMotionStartLocation = false;
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYFootstepAudioDiagnostics
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") bool bRuntimeActive = false;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") bool bMuted = false;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") bool bLastStepLeft = true;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") int32 MovementUpdates = 0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") int32 Steps = 0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") int32 PlaybackStarts = 0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") int32 ResetEvents = 0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") int32 Discontinuities = 0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") bool bMoving = false;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") int32 MovementStartEvents = 0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") int32 StopEvents = 0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") double LastMovementStartSeconds = -1.0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") double LastStopSeconds = -1.0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") double LastPlaybackStartSeconds = -1.0;
	UPROPERTY(BlueprintReadOnly, Category = "DY|Footsteps") double AccumulatedDistanceCentimeters = 0.0;
};

/**
 * Opt-in local footstep capability for the existing unanimated operation carrier.
 * Character movement updates provide displacement; one owned voice presents it.
 * No Tick, timer, input binding, world discovery or puzzle/state-machine dependency.
 */
UCLASS(ClassGroup = (DY), meta = (BlueprintSpawnableComponent))
class DENGYINGSHANHAI_API UDYFootstepAudioComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UDYFootstepAudioComponent();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Footsteps")
	bool bEnableDevelopmentFootsteps = false;

	/** Dev candidate: 150 cm / existing 360 cm/s = about 2.4 impacts per second at full speed. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Footsteps", meta = (ClampMin = "1.0", Units = "cm"))
	double StepDistanceCentimeters = 150.0;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Footsteps")
	TObjectPtr<USoundBase> LeftSound;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Footsteps")
	TObjectPtr<USoundBase> RightSound;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Footsteps", meta = (ClampMin = "0.0", ClampMax = "2.0"))
	double Volume = 1.0;

	/** Native constant reverb send; the Stage's separately owned room effect supplies the wet tail. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Footsteps", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float TheatreReverbSendLevel = 0.22f;

	static float SanitizeReverbSendLevel(float InLevel);

	/** Development silence switch. Unmuting never replays an earlier footstep. */
	UFUNCTION(BlueprintCallable, Category = "DY|Footsteps")
	void SetMuted(bool bInMuted);

	UFUNCTION(BlueprintPure, Category = "DY|Footsteps")
	FDYFootstepAudioDiagnostics GetFootstepDiagnostics() const;

	/** Voice exists only in a valid opted-in runtime Character session. */
	UFUNCTION(BlueprintPure, Category = "DY|Footsteps")
	UAudioComponent* GetFootstepVoice() const { return FootstepVoice; }

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	UFUNCTION()
	void HandleMovementUpdated(float DeltaSeconds, FVector OldLocation, FVector OldVelocity);

	UFUNCTION()
	void HandleMovementModeChanged(ACharacter* Character, EMovementMode PreviousMode, uint8 PreviousCustomMode);

	UFUNCTION()
	void HandleOperatorReset(EDYOperatorResetReason Reason, int32 ResetCount);

	void ClearMotionAndStop();
	void DeactivateSession();
	bool HasLiveCharacter() const;

	UPROPERTY(Transient)
	TObjectPtr<UAudioComponent> FootstepVoice;

	TWeakObjectPtr<ACharacter> BoundCharacter;
	TWeakObjectPtr<ADYStageOperatorPawn> BoundOperator;
	FDYFootstepDistanceGate Gate;
	FDYFootstepAudioDiagnostics Diagnostics;
	bool bSkipNextMovementUpdate = false;

#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYFootstepAudioTestSeam;
#endif
};
