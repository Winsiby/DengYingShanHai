#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interaction/DYControllable.h"
#include "Interaction/DYStaffGeometryTypes.h"
#include "DYPuppetActor.generated.h"

class USceneComponent;
class UStaticMeshComponent;
class UDYPuppetControlComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FDYPuppetResetRequestedSignature);

/** Shadow-casting puppet shell whose reusable control capability is enabled per puzzle. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYPuppetActor : public AActor, public IDYControllable
{
	GENERATED_BODY()

public:
	ADYPuppetActor();

	UFUNCTION(BlueprintPure, Category = "DY|Puppet")
	FName GetPoseId() const;

	/** Reads mesh bounds and the full component transform; never changes control or pose. */
	UFUNCTION(BlueprintPure, Category = "DY|Puppet")
	FDYStaffGeometrySnapshot GetStaffGeometrySnapshot() const;

	UDYPuppetControlComponent* GetPuppetControlComponent() const { return PuppetControl; }

	virtual bool CanBeginControl_Implementation(const FDYControlContext& Context) const override;
	virtual void BeginControl_Implementation(const FDYControlContext& Context) override;
	virtual void ApplyControlIntent_Implementation(const FDYControlIntent& Intent) override;
	virtual void EndControl_Implementation(const FDYControlContext& Context) override;
	virtual void ResetControlState_Implementation(const FDYControlContext& Context) override;
	virtual void SetControlEnabled_Implementation(bool bEnabled) override;
	virtual FDYControlSnapshot GetControlSnapshot_Implementation() const override;

	UPROPERTY(BlueprintAssignable, Category = "DY|Puppet")
	FDYPuppetResetRequestedSignature OnResetRequested;

protected:
	virtual void BeginPlay() override;

private:
	UFUNCTION()
	void HandleControlChanged(double NormalizedValue, FName NewPoseId);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> Torso;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> Head;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> Staff;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UDYPuppetControlComponent> PuppetControl;
};
