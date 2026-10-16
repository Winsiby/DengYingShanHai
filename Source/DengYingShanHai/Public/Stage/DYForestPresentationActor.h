#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Stage/DYForestGeometryLibrary.h"
#include "DYForestPresentationActor.generated.h"

class ADYStagePresentation;
class UMaterialInterface;
class UStaticMesh;
class UStaticMeshComponent;

/** Cosmetic resource owner. No puzzle reads, world scans, timer, input or Tick. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYForestPresentationActor : public AActor
{
	GENERATED_BODY()

public:
	ADYForestPresentationActor();

	UFUNCTION(BlueprintPure, Category = "DY|Forest Presentation")
	bool HasForestSession() const;

	UFUNCTION(BlueprintPure, Category = "DY|Forest Presentation")
	FDYForestGeometrySample GetForestGeometrySample() const { return LastSample; }

	/** Diagnostic components only; callers must not animate or replace their meshes. */
	UFUNCTION(BlueprintPure, Category = "DY|Forest Presentation")
	TArray<UStaticMeshComponent*> GetBranchMeshComponents() const;

protected:
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	friend class ADYStagePresentation;
	bool BeginSession(ADYStagePresentation* PresentationOwner, const FDYStaffContactPresentationSnapshot& Contact);
	bool ApplyNormalizedGrowth(ADYStagePresentation* PresentationOwner, const FGuid& Token, double Progress);
	bool ClearSession(ADYStagePresentation* PresentationOwner, const FGuid& Token);
	void ReleaseResources();
	bool IsSessionOwner(const ADYStagePresentation* PresentationOwner, const FGuid& Token) const;

	/** Authored asset must use mesh-local Z as the branch axis. No built-in art asset. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Forest Presentation", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMesh> BranchMesh;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Forest Presentation", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UMaterialInterface> BranchMaterial;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Forest Presentation", meta = (AllowPrivateAccess = "true"))
	TArray<FDYForestBranchDefinition> BranchLayout;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> BranchComponents;
	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> SessionMesh;
	UPROPERTY(Transient)
	TArray<FDYForestBranchDefinition> SessionLayout;
	UPROPERTY(Transient)
	FDYStaffContactPresentationSnapshot SessionContact;
	UPROPERTY(Transient)
	FDYForestGeometrySample LastSample;

	TWeakObjectPtr<ADYStagePresentation> SessionOwner;
	FVector MeshLocalMin = FVector::ZeroVector;
	FVector MeshLocalMax = FVector::ZeroVector;
	bool bEndingPlay = false;
};
