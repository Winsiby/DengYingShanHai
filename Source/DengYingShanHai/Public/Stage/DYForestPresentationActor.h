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

	/** Optional authored leaf clusters; cosmetic only and separate from branch diagnostics. */
	UFUNCTION(BlueprintPure, Category = "DY|Forest Presentation")
	TArray<UStaticMeshComponent*> GetCanopyMeshComponents() const;

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

	/** Optional leaf-crown mesh, with mesh-local +Z as its growth axis. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Forest Presentation", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMesh> CanopyMesh;

	/** Branch indices that receive an authored canopy cluster. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Forest Presentation", meta = (AllowPrivateAccess = "true"))
	TArray<int32> CanopyBranches;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Forest Presentation", meta = (AllowPrivateAccess = "true", ClampMin = "0.05", ClampMax = "3.0"))
	float CanopyWorldScale = 0.6f;

	/** Optional per-cluster scale, aligned with CanopyBranches. Empty falls back to CanopyWorldScale.
	 *  Varied cluster sizes keep one wide crown from reading as the same stamp repeated. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Forest Presentation", meta = (AllowPrivateAccess = "true"))
	TArray<double> CanopyScales;

	/** Optional material applied to every canopy slot; keeps the crown inside the ink palette. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Forest Presentation", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UMaterialInterface> CanopyMaterial;

	/** World-space nudge applied to every branch and canopy. The growth library places the
	 *  forest exactly on the authored narrative ground line, which normally lies on the shadow
	 *  screen; a small offset toward the audience keeps the geometry in front of the screen
	 *  instead of half-buried inside it. Zero by default so geometry tests stay exact. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Forest Presentation", meta = (AllowPrivateAccess = "true"))
	FVector WorldOffset = FVector::ZeroVector;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> BranchComponents;
	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> CanopyComponents;
	UPROPERTY(Transient)
	TArray<int32> SessionCanopyBranches;
	UPROPERTY(Transient)
	TArray<double> SessionCanopyScales;
	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> SessionMesh;
	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> CanopySessionMesh;
	UPROPERTY(Transient)
	TArray<FDYForestBranchDefinition> SessionLayout;
	UPROPERTY(Transient)
	FDYStaffContactPresentationSnapshot SessionContact;
	UPROPERTY(Transient)
	FDYForestGeometrySample LastSample;

	TWeakObjectPtr<ADYStagePresentation> SessionOwner;
	FVector MeshLocalMin = FVector::ZeroVector;
	FVector MeshLocalMax = FVector::ZeroVector;
	FVector CanopyLocalMin = FVector::ZeroVector;
	FVector CanopyLocalMax = FVector::ZeroVector;
	bool bEndingPlay = false;
};
