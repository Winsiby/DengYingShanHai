#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Interaction/DYControlTypes.h"
#include "DYLightControlComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FDYNormalizedLightValueSignature, double, NormalizedValue);

UCLASS(ClassGroup = (DY), meta = (BlueprintSpawnableComponent))
class DENGYINGSHANHAI_API UDYLightControlComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UDYLightControlComponent();

	UFUNCTION(BlueprintCallable, Category = "DY|Light Control")
	void BeginControl();

	UFUNCTION(BlueprintCallable, Category = "DY|Light Control")
	void EndControl();

	UFUNCTION(BlueprintCallable, Category = "DY|Light Control")
	void ApplyControlIntent(const FDYControlIntent& Intent);

	UFUNCTION(BlueprintCallable, Category = "DY|Light Control")
	void SetControlEnabled(bool bEnabled);

	UFUNCTION(BlueprintCallable, Category = "DY|Light Control")
	void SetNormalizedValue(double NewValue);

	UFUNCTION(BlueprintCallable, Category = "DY|Light Control")
	void ResetToInitialValue();

	UFUNCTION(BlueprintPure, Category = "DY|Light Control")
	double GetNormalizedValue() const { return CurrentNormalizedValue; }

	UFUNCTION(BlueprintPure, Category = "DY|Light Control")
	bool IsControlEnabled() const { return bControlEnabled; }

	UFUNCTION(BlueprintPure, Category = "DY|Light Control")
	bool IsUnderControl() const { return bUnderControl; }

	UFUNCTION(BlueprintPure, Category = "DY|Light Control")
	FDYControlSnapshot GetControlSnapshot() const;

	FVector GetWorldLocationForNormalizedValue(double Value) const;
	void GetRailWorldEndpoints(FVector& OutStart, FVector& OutEnd) const;

	UPROPERTY(BlueprintAssignable, Category = "DY|Light Control")
	FDYNormalizedLightValueSignature OnNormalizedValueChanged;

protected:
	virtual void BeginPlay() override;

private:
	FVector GetSafeWorldAxis() const;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Light Control", meta = (AllowPrivateAccess = "true"))
	FVector WorldTravelAxis = FVector::RightVector;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Light Control", meta = (AllowPrivateAccess = "true", ClampMin = "1.0", Units = "cm"))
	double TravelDistance = 600.0;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Light Control", meta = (AllowPrivateAccess = "true", ClampMin = "0.0", ClampMax = "1.0"))
	double InitialNormalizedValue = 0.15;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Light Control", meta = (AllowPrivateAccess = "true", ClampMin = "0.01"))
	double NormalizedUnitsPerSecond = 0.35;

	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "DY|Light Control", meta = (AllowPrivateAccess = "true"))
	double CurrentNormalizedValue = 0.15;

	FVector RailCenter = FVector::ZeroVector;
	bool bRailInitialized = false;
	bool bControlEnabled = true;
	bool bUnderControl = false;
};
