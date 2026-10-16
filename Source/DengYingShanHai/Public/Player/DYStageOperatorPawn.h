#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "DYStageOperatorPawn.generated.h"

class UCameraComponent;
class UInputAction;
class UInputComponent;
class USpringArmComponent;
class UStaticMeshComponent;
class UDamageType;
class UDYInteractionComponent;
class AActor;
struct FInputActionValue;

UENUM(BlueprintType)
enum class EDYOperatorResetReason : uint8
{
	Manual,
	OutOfWorld
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FDYOperatorResetSignature, EDYOperatorResetReason, Reason, int32, ResetCount);

/**
 * Minimal third-person operation carrier for the development interaction lab.
 * Input produces semantic move/look/reset intent; no puzzle or stage-object logic lives here.
 */
UCLASS()
class DENGYINGSHANHAI_API ADYStageOperatorPawn : public ACharacter
{
	GENERATED_BODY()

public:
	ADYStageOperatorPawn();

	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	UFUNCTION(BlueprintCallable, Category = "DY|Input")
	void ApplyMoveIntent(const FVector2D& MovementIntent);

	UFUNCTION(BlueprintCallable, Category = "DY|Input")
	void ApplyLookIntent(const FVector2D& LookIntent);

	/** Resets only this operator pawn; this is not the whole-experience reset policy. */
	UFUNCTION(BlueprintCallable, Category = "DY|Development")
	void ResetOperatorToStart(EDYOperatorResetReason Reason = EDYOperatorResetReason::Manual);

	UFUNCTION(BlueprintPure, Category = "DY|Development")
	int32 GetOperatorResetCount() const
	{
		return OperatorResetCount;
	}

	UFUNCTION(BlueprintPure, Category = "DY|Camera")
	USpringArmComponent* GetCameraBoom() const
	{
		return CameraBoom;
	}

	UFUNCTION(BlueprintPure, Category = "DY|Camera")
	UCameraComponent* GetFollowCamera() const
	{
		return FollowCamera;
	}

	UFUNCTION(BlueprintPure, Category = "DY|Interaction")
	UDYInteractionComponent* GetInteractionComponent() const
	{
		return InteractionComponent;
	}

	const UInputAction* GetMoveActionAsset() const { return MoveActionAsset; }
	const UInputAction* GetLookActionAsset() const { return LookActionAsset; }
	const UInputAction* GetResetActionAsset() const { return ResetActionAsset; }
	const UInputAction* GetInteractActionAsset() const { return InteractActionAsset; }
	const UInputAction* GetManipulateActionAsset() const { return ManipulateActionAsset; }
	const UInputAction* GetResetControlledActionAsset() const { return ResetControlledActionAsset; }

	UPROPERTY(BlueprintAssignable, Category = "DY|Development")
	FDYOperatorResetSignature OnOperatorReset;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void FellOutOfWorld(const UDamageType& DamageType) override;

private:
	void HandleMoveInput(const FInputActionValue& Value);
	void HandleLookInput(const FInputActionValue& Value);
	void HandleResetInput(const FInputActionValue& Value);
	void HandleInteractInput(const FInputActionValue& Value);
	void HandleManipulateInput(const FInputActionValue& Value);
	void HandleResetControlledInput(const FInputActionValue& Value);

	UFUNCTION()
	void HandleControlStateChanged(AActor* ControlledActor, bool bIsControlling);

	void CaptureInitialState();
	bool HasCompleteInputConfiguration() const;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Camera", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Camera", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UCameraComponent> FollowCamera;

	/** Engine-basic-shape placeholders only; replace without changing movement or input code. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Development", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> DevPlaceholderBody;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Development", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> DevPlaceholderHead;

	/** Reusable focus/control capability. The pawn only routes semantic input into this component. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Interaction", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UDYInteractionComponent> InteractionComponent;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputAction> MoveActionAsset;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputAction> LookActionAsset;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputAction> ResetActionAsset;

	/** Dev-only physical binding; the gameplay contract is the semantic Interact action. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputAction> InteractActionAsset;

	/** Dev-only physical binding; the gameplay contract is the semantic manipulation axis. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputAction> ManipulateActionAsset;

	/** Dev-only contextual reset action; currently mapped only while manipulating. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputAction> ResetControlledActionAsset;

	TWeakObjectPtr<UInputComponent> BoundInputComponent;

	FTransform InitialActorTransform = FTransform::Identity;
	FRotator InitialControlRotation = FRotator::ZeroRotator;
	bool bHasInitialState = false;
	int32 OperatorResetCount = 0;
};
