#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DYStageEnvironment.generated.h"

class UPointLightComponent;
class USceneComponent;

UENUM(BlueprintType)
enum class EDYStageEnvironmentState : uint8
{
	Dormant,
	SunAwakened,
	ChaseAwakened,
	// Append only: accepted assets retain the old 0/1/2 serialized values.
	FinaleReady,
	ForestComplete
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
	FDYStageEnvironmentStateChangedSignature,
	EDYStageEnvironmentState, PreviousState,
	EDYStageEnvironmentState, NewState);

/**
 * Owns the small set of stage-wide visual states requested by Stage Presentation.
 * It is deliberately separate from the puzzle evaluator and the controllable lamp.
 */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYStageEnvironment : public AActor
{
	GENERATED_BODY()

public:
	ADYStageEnvironment();

	UFUNCTION(BlueprintCallable, Category = "DY|Stage")
	void ApplyState(EDYStageEnvironmentState NewState);

	UFUNCTION(BlueprintCallable, Category = "DY|Stage")
	void ResetToDormant();

	UFUNCTION(BlueprintPure, Category = "DY|Stage")
	EDYStageEnvironmentState GetCurrentState() const { return CurrentState; }

	UFUNCTION(BlueprintPure, Category = "DY|Stage")
	UPointLightComponent* GetSunAwakenedAccent() const { return SunAwakenedAccent; }

	UFUNCTION(BlueprintPure, Category = "DY|Stage")
	UPointLightComponent* GetChaseAwakenedAccent() const { return ChaseAwakenedAccent; }

	UPROPERTY(BlueprintAssignable, Category = "DY|Stage")
	FDYStageEnvironmentStateChangedSignature OnStateChanged;

protected:
	virtual void BeginPlay() override;

private:
	void ApplyVisualState();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Stage", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<USceneComponent> SceneRoot;

	/** Dev success accent only; formal art and cue composition remain a presentation-layer task. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Stage", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UPointLightComponent> SunAwakenedAccent;

	/** Dev-only wider stage-wing accent proving that P02 has a distinct semantic result. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Stage", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UPointLightComponent> ChaseAwakenedAccent;

	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "DY|Stage", meta = (AllowPrivateAccess = "true"))
	EDYStageEnvironmentState CurrentState = EDYStageEnvironmentState::Dormant;
};
