#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interaction/DYControllable.h"
#include "DYLightRigActor.generated.h"

class USceneComponent;
class USpotLightComponent;
class UStaticMeshComponent;
class UDYLightControlComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FDYLightRigResetRequestedSignature);

UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYLightRigActor : public AActor, public IDYControllable
{
	GENERATED_BODY()

public:
	ADYLightRigActor();

	UDYLightControlComponent* GetLightControlComponent() const { return LightControl; }
	USpotLightComponent* GetKeyLightComponent() const { return KeyLight; }

	UFUNCTION(BlueprintCallable, Category = "DY|Light Rig")
	void ApplyResolvedDevFeedback(bool bResolved);

	virtual bool CanBeginControl_Implementation(const FDYControlContext& Context) const override;
	virtual void BeginControl_Implementation(const FDYControlContext& Context) override;
	virtual void ApplyControlIntent_Implementation(const FDYControlIntent& Intent) override;
	virtual void EndControl_Implementation(const FDYControlContext& Context) override;
	virtual void ResetControlState_Implementation(const FDYControlContext& Context) override;
	virtual void SetControlEnabled_Implementation(bool bEnabled) override;
	virtual FDYControlSnapshot GetControlSnapshot_Implementation() const override;

	/** Director subscribes through its explicit LightRig reference; no world scan is used. */
	UPROPERTY(BlueprintAssignable, Category = "DY|Light Rig")
	FDYLightRigResetRequestedSignature OnResetRequested;

private:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Light Rig", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Light Rig", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> LampBody;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Light Rig", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> LampStand;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Light Rig", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<USpotLightComponent> KeyLight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Light Rig", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UDYLightControlComponent> LightControl;
};
