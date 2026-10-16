#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Interaction/DYControlTypes.h"
#include "DYPuppetControlComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
	FDYPuppetControlChangedSignature,
	double,
	NormalizedValue,
	FName,
	PoseId);

/**
 * Reusable, frame-rate-independent control capability for a shadow puppet.
 * One semantic axis drives an authored rail and selects the nearest pose stop;
 * input ownership remains in UDYInteractionComponent.
 */
UCLASS(ClassGroup = (DY), meta = (BlueprintSpawnableComponent))
class DENGYINGSHANHAI_API UDYPuppetControlComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UDYPuppetControlComponent();

	UFUNCTION(BlueprintCallable, Category = "DY|Puppet Control")
	void BeginControl();

	UFUNCTION(BlueprintCallable, Category = "DY|Puppet Control")
	void EndControl();

	UFUNCTION(BlueprintCallable, Category = "DY|Puppet Control")
	void ApplyControlIntent(const FDYControlIntent& Intent);

	UFUNCTION(BlueprintCallable, Category = "DY|Puppet Control")
	void SetControlEnabled(bool bEnabled);

	UFUNCTION(BlueprintCallable, Category = "DY|Puppet Control")
	void SetNormalizedValue(double NewValue);

	UFUNCTION(BlueprintCallable, Category = "DY|Puppet Control")
	void ResetToInitialValue();

	UFUNCTION(BlueprintPure, Category = "DY|Puppet Control")
	double GetNormalizedValue() const { return CurrentNormalizedValue; }

	UFUNCTION(BlueprintPure, Category = "DY|Puppet Control")
	FName GetPoseId() const;

	UFUNCTION(BlueprintPure, Category = "DY|Puppet Control")
	bool IsControlEnabled() const { return bControlEnabled; }

	UFUNCTION(BlueprintPure, Category = "DY|Puppet Control")
	bool IsUnderControl() const { return bUnderControl; }

	UFUNCTION(BlueprintPure, Category = "DY|Puppet Control")
	FDYControlSnapshot GetControlSnapshot() const;

	FVector GetWorldLocationForNormalizedValue(double Value) const;
	void GetRailWorldEndpoints(FVector& OutStart, FVector& OutEnd) const;

	UPROPERTY(BlueprintAssignable, Category = "DY|Puppet Control")
	FDYPuppetControlChangedSignature OnControlChanged;

protected:
	virtual void BeginPlay() override;

private:
	FVector GetSafeWorldAxis() const;
	int32 GetPoseIndexForNormalizedValue(double Value) const;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet Control", meta = (AllowPrivateAccess = "true"))
	FVector WorldTravelAxis = FVector::RightVector;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet Control", meta = (AllowPrivateAccess = "true", ClampMin = "1.0", Units = "cm"))
	double TravelDistance = 320.0;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet Control", meta = (AllowPrivateAccess = "true", ClampMin = "0.0", ClampMax = "1.0"))
	double InitialNormalizedValue = 0.15;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet Control", meta = (AllowPrivateAccess = "true", ClampMin = "0.01"))
	double NormalizedUnitsPerSecond = 0.28;

	/** Ordered pose stops selected by the same normalized rail used for movement. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet Control", meta = (AllowPrivateAccess = "true"))
	TArray<FName> PoseIds;

	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "DY|Puppet Control", meta = (AllowPrivateAccess = "true"))
	double CurrentNormalizedValue = 0.15;

	FVector RailCenter = FVector::ZeroVector;
	bool bRailInitialized = false;
	bool bControlEnabled = false;
	bool bUnderControl = false;
};
