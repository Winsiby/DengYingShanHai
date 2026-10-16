#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Stage/DYStaffProjectionLibrary.h"
#include "DYStaffProjectionProbe.generated.h"

class ADYLightRigActor;
class ADYPuppetActor;
class AStaticMeshActor;
class UTextRenderComponent;

/** Dev-only observer: explicit references, event-driven geometry, no gameplay authority. */
UCLASS(NotBlueprintable)
class DENGYINGSHANHAI_API ADYStaffProjectionProbe : public AActor
{
	GENERATED_BODY()

public:
	ADYStaffProjectionProbe();

	UPROPERTY(EditInstanceOnly, Category = "DY|Dev Projection")
	TObjectPtr<ADYLightRigActor> Light;

	UPROPERTY(EditInstanceOnly, Category = "DY|Dev Projection")
	TObjectPtr<ADYPuppetActor> Puppet;

	UPROPERTY(EditInstanceOnly, Category = "DY|Dev Projection")
	TObjectPtr<AStaticMeshActor> ScreenActor;

	UFUNCTION(BlueprintCallable, CallInEditor, Category = "DY|Dev Projection", meta = (DevelopmentOnly))
	void RefreshProjection();

	UFUNCTION(BlueprintPure, Category = "DY|Dev Projection")
	FDYStaffProjectionCapture GetLastCapture() const { return LastCapture; }

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	UFUNCTION()
	void HandleLightChanged(double Value);
	UFUNCTION()
	void HandlePuppetChanged(double Value, FName Pose);
	void QueueRefresh();
	void UpdateMarker(UTextRenderComponent* Marker, const FDYStaffProjectionPoint& Point);

	UPROPERTY(VisibleAnywhere, Category = "DY|Dev Projection")
	TObjectPtr<UTextRenderComponent> Readout;
	UPROPERTY(VisibleAnywhere, Category = "DY|Dev Projection")
	TObjectPtr<UTextRenderComponent> MarkerA;
	UPROPERTY(VisibleAnywhere, Category = "DY|Dev Projection")
	TObjectPtr<UTextRenderComponent> MarkerB;
	UPROPERTY(Transient)
	FDYStaffProjectionCapture LastCapture;
	FTimerHandle RefreshTimer;
};
