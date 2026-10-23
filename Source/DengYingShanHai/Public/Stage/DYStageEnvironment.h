#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DYStageEnvironment.generated.h"

class UAudioComponent;
class UMaterialInstanceDynamic;
class UPointLightComponent;
class USceneComponent;
class USoundBase;

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

	/** Turns the tagged exterior dead canopies green once P03 resolves. Presentation only: never reads the puzzle director. */
	UFUNCTION(BlueprintCallable, Category = "DY|Exterior")
	void TriggerExteriorGreening();

	/** Restores the dormant exterior look (used by reset flows). */
	UFUNCTION(BlueprintCallable, Category = "DY|Exterior")
	void ResetExteriorGreening();


protected:
	virtual void BeginPlay() override;

private:
	void ApplyVisualState();
	void SpawnExteriorAmbience();
	void AdvanceExteriorGreening();

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

	/** Actors with this tag are treated as the exterior grove that answers 杖落成林. */
	UPROPERTY(EditAnywhere, Category = "DY|Exterior")
	FName ExteriorTreeTag = TEXT("DYExterior_DeadTree");
	/** Second tag carried only by the canopy meshes so the runtime filter never touches the trunks. */
	FName ExteriorCanopyTag = TEXT("DYExterior_Canopy");

	UPROPERTY(EditAnywhere, Category = "DY|Exterior")
	float ExteriorGreeningSeconds = 4.0f;

	/** Set once the first 杖落成林 fade finished so later re-applies snap back without replaying the fade. */
	bool bExteriorGreeningDone = false;

	UPROPERTY(EditAnywhere, Category = "DY|Exterior")
	FLinearColor ExteriorDeadTint = FLinearColor(0.26f, 0.22f, 0.17f);

	UPROPERTY(EditAnywhere, Category = "DY|Exterior")
	FLinearColor ExteriorAliveTint = FLinearColor(0.07f, 0.50f, 0.10f);

	UPROPERTY(EditAnywhere, Category = "DY|Exterior")
	TSoftObjectPtr<USoundBase> ExteriorWindSound;

	UPROPERTY(EditAnywhere, Category = "DY|Exterior")
	TSoftObjectPtr<USoundBase> ExteriorLeavesSound;

	TArray<TObjectPtr<UMaterialInstanceDynamic>> ExteriorCanopyMaterials;
	TObjectPtr<UAudioComponent> ExteriorAmbienceComponent;
	double ExteriorGreeningStartSeconds = 0.0;
	FTimerHandle ExteriorGreeningHandle;
	bool bExteriorGreeningActive = false;
};