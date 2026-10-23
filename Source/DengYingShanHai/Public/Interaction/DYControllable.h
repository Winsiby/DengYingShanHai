#pragma once

#include "CoreMinimal.h"
#include "Interaction/DYControlTypes.h"
#include "UObject/Interface.h"
#include "DYControllable.generated.h"

UINTERFACE(BlueprintType, MinimalAPI)
class UDYControllable : public UInterface
{
	GENERATED_BODY()
};

class DENGYINGSHANHAI_API IDYControllable
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "DY|Interaction")
	bool CanBeginControl(const FDYControlContext& Context) const;

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "DY|Interaction")
	void BeginControl(const FDYControlContext& Context);

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "DY|Interaction")
	void ApplyControlIntent(const FDYControlIntent& Intent);

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "DY|Interaction")
	void EndControl(const FDYControlContext& Context);

	/** Requests a reset through the controlled Actor's owning gameplay system. */
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "DY|Interaction")
	void ResetControlState(const FDYControlContext& Context);

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "DY|Interaction")
	void SetControlEnabled(bool bEnabled);

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "DY|Interaction")
	FDYControlSnapshot GetControlSnapshot() const;
};
