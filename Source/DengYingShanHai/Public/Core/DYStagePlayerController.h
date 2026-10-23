#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "DYStagePlayerController.generated.h"

class UInputMappingContext;
class UEnhancedInputLocalPlayerSubsystem;

/**
 * Owns local-player Enhanced Input context lifetime and basic camera pitch limits.
 */
UCLASS()
class DENGYINGSHANHAI_API ADYStagePlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	ADYStagePlayerController();

	const UInputMappingContext* GetExploreMappingContextAsset() const
	{
		return ExploreMappingContextAsset;
	}

	int32 GetExploreMappingPriority() const
	{
		return ExploreMappingPriority;
	}

	const UInputMappingContext* GetManipulateMappingContextAsset() const
	{
		return ManipulateMappingContextAsset;
	}

	UFUNCTION(BlueprintCallable, Category = "DY|Input")
	void SetManipulationMode(bool bEnabled);

	UFUNCTION(BlueprintPure, Category = "DY|Input")
	bool IsManipulationModeActive() const { return bManipulationModeActive; }

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	void ApplyExploreMappingContext();
	void RemoveExploreMappingContext();
	void RemoveManipulateMappingContext();
	UEnhancedInputLocalPlayerSubsystem* GetEnhancedInputSubsystem() const;

	/** Dev-only keyboard/mouse exploration context. Physical bindings remain replaceable. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputMappingContext> ExploreMappingContextAsset;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	int32 ExploreMappingPriority = 0;

	/** Dev-only mutually exclusive lamp-manipulation context. Final physical bindings remain unapproved. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputMappingContext> ManipulateMappingContextAsset;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	int32 ManipulateMappingPriority = 10;

	UPROPERTY(Transient)
	TObjectPtr<UInputMappingContext> AppliedExploreMappingContext;

	UPROPERTY(Transient)
	TObjectPtr<UInputMappingContext> AppliedManipulateMappingContext;

	bool bExploreMappingContextApplied = false;
	bool bManipulationModeActive = false;
};
