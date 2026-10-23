#include "Stage/DYForestPresentationActor.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Stage/DYStagePresentation.h"

ADYForestPresentationActor::ADYForestPresentationActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

bool ADYForestPresentationActor::HasForestSession() const
{
	return !bEndingPlay && SessionOwner.IsValid() && SessionContact.bHasContact
		&& SessionContact.Token.IsValid() && IsValid(SessionMesh)
		&& BranchComponents.Num() == SessionLayout.Num() && !BranchComponents.IsEmpty()
		&& (!IsValid(CanopySessionMesh) || CanopyComponents.Num() == SessionCanopyBranches.Num());
}

TArray<UStaticMeshComponent*> ADYForestPresentationActor::GetBranchMeshComponents() const
{
	TArray<UStaticMeshComponent*> Result;
	for (UStaticMeshComponent* Component : BranchComponents) { Result.Add(Component); }
	return Result;
}

TArray<UStaticMeshComponent*> ADYForestPresentationActor::GetCanopyMeshComponents() const
{
	TArray<UStaticMeshComponent*> Result;
	for (UStaticMeshComponent* Component : CanopyComponents) { Result.Add(Component); }
	return Result;
}

bool ADYForestPresentationActor::IsSessionOwner(const ADYStagePresentation* PresentationOwner, const FGuid& Token) const
{
	return HasForestSession() && SessionOwner.Get() == PresentationOwner && Token == SessionContact.Token;
}

bool ADYForestPresentationActor::BeginSession(ADYStagePresentation* PresentationOwner,
	const FDYStaffContactPresentationSnapshot& Contact)
{
		// Never replace another owner's session, or silently rewind an active one.
	if (bEndingPlay || !IsValid(PresentationOwner) || PresentationOwner->GetWorld() != GetWorld()
		|| SessionContact.bHasContact || !IsValid(BranchMesh)) { return false; }
	const FBox Bounds = BranchMesh->GetBoundingBox();
	const auto Initial = UDYForestGeometryLibrary::SampleForestGeometry(Contact, BranchLayout,
		0.0, Bounds.Min, Bounds.Max);
	if (Initial.Status != EDYForestGeometryStatus::Valid)
	{
				return false;
	}
		SessionOwner = PresentationOwner;
	SessionContact = Contact;
	SessionLayout = BranchLayout; // Freeze content for this session, not future author edits.
	SessionCanopyScales = CanopyScales;
	SessionMesh = BranchMesh;
	MeshLocalMin = Bounds.Min;
	MeshLocalMax = Bounds.Max;
	for (int32 Index = 0; Index < SessionLayout.Num(); ++Index)
	{
		UStaticMeshComponent* Component = NewObject<UStaticMeshComponent>(this, NAME_None, RF_Transient);
		BranchComponents.Add(Component);
		AddInstanceComponent(Component);
		Component->SetupAttachment(GetRootComponent());
		// Library produces mesh WORLD transforms; an authored Actor transform is not a multiplier.
		Component->SetAbsolute(true, true, true);
		Component->SetMobility(EComponentMobility::Movable);
		Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Component->SetGenerateOverlapEvents(false);
		Component->SetVisibility(false);
		Component->SetHiddenInGame(true);
		Component->SetCastShadow(false);
		Component->SetStaticMesh(SessionMesh);
		if (BranchMaterial) { Component->SetMaterial(0, BranchMaterial); }
		Component->RegisterComponent();
		FVector ActualMin, ActualMax;
		Component->GetLocalBounds(ActualMin, ActualMax);
		if (!ActualMin.Equals(MeshLocalMin, UE_DOUBLE_SMALL_NUMBER)
			|| !ActualMax.Equals(MeshLocalMax, UE_DOUBLE_SMALL_NUMBER))
		{
						ReleaseResources();
			return false;
		}
	}
		if (IsValid(CanopyMesh) && !CanopyBranches.IsEmpty())
	{
		const FBox CanopyBounds = CanopyMesh->GetBoundingBox();
		CanopySessionMesh = CanopyMesh;
		CanopyLocalMin = CanopyBounds.Min;
		CanopyLocalMax = CanopyBounds.Max;
		for (const int32 BranchIndex : CanopyBranches)
		{
			if (!SessionLayout.IsValidIndex(BranchIndex)) { continue; }
			UStaticMeshComponent* Canopy = NewObject<UStaticMeshComponent>(this, NAME_None, RF_Transient);
			CanopyComponents.Add(Canopy);
			SessionCanopyBranches.Add(BranchIndex);
			AddInstanceComponent(Canopy);
			Canopy->SetupAttachment(GetRootComponent());
			Canopy->SetAbsolute(true, true, true);
			Canopy->SetMobility(EComponentMobility::Movable);
			Canopy->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			Canopy->SetGenerateOverlapEvents(false);
			Canopy->SetVisibility(false);
			Canopy->SetHiddenInGame(true);
			Canopy->SetCastShadow(false);
			Canopy->SetStaticMesh(CanopySessionMesh);
			Canopy->RegisterComponent();
			if (CanopyMaterial)
			{
				for (int32 Slot = 0; Slot < Canopy->GetNumMaterials(); ++Slot)
				{
					Canopy->SetMaterial(Slot, CanopyMaterial);
				}
			}
			FVector ActualMin, ActualMax;
			Canopy->GetLocalBounds(ActualMin, ActualMax);
			if (!ActualMin.Equals(CanopyLocalMin, UE_DOUBLE_SMALL_NUMBER)
				|| !ActualMax.Equals(CanopyLocalMax, UE_DOUBLE_SMALL_NUMBER))
			{
								ReleaseResources();
				return false;
			}
		}
	}
		LastSample = Initial;
	return true;
}

bool ADYForestPresentationActor::ApplyNormalizedGrowth(ADYStagePresentation* PresentationOwner,
	const FGuid& Token, const double Progress)
{
	if (!IsSessionOwner(PresentationOwner, Token)) { return false; }
	for (UStaticMeshComponent* Component : BranchComponents)
	{
		FVector ActualMin, ActualMax;
		if (!IsValid(Component) || Component->GetStaticMesh() != SessionMesh
			|| Component->GetOwner() != this || Component->GetWorld() != GetWorld())
		{
						ReleaseResources();
			return false;
		}
		Component->GetLocalBounds(ActualMin, ActualMax);
		if (!ActualMin.Equals(MeshLocalMin, UE_DOUBLE_SMALL_NUMBER)
			|| !ActualMax.Equals(MeshLocalMax, UE_DOUBLE_SMALL_NUMBER))
		{
			ReleaseResources();
			return false;
		}
	}
	const auto Sample = UDYForestGeometryLibrary::SampleForestGeometry(SessionContact,
		SessionLayout, Progress, MeshLocalMin, MeshLocalMax);
	if (Sample.Status != EDYForestGeometryStatus::Valid || Sample.Branches.Num() != BranchComponents.Num())
	{
				ReleaseResources(); // Fail closed: no previous or partly-updated tree shadow remains.
		return false;
	}
	// Full sample and every component checked before applying any transforms.
	for (int32 Index = 0; Index < BranchComponents.Num(); ++Index)
	{
		UStaticMeshComponent* Component = BranchComponents[Index];
		const auto& Geometry = Sample.Branches[Index];
		if (Geometry.bVisible)
		{
			// These branches are non-physics presentation components (NoCollision, absolute
			// transform, no simulation), so they only need a normal scene update. The generic
			// SetWorldTransform path compares the previous transform and can drop a sub-milli-
			// centimetre move near the sample position; the split public setters below apply the
			// authored scale and world location directly. The rotation goes through Rotator(),
			// so quaternion round-trip equality is NOT guaranteed bit-for-bit here: the existing
			// UE_DOUBLE_SMALL_NUMBER (1e-8) full-transform check remains the authority.
			// This is NOT a general solution for simulated physics components.
			Component->SetWorldScale3D(Geometry.MeshWorldTransform.GetScale3D());
			Component->SetWorldLocationAndRotationNoPhysics(
				Geometry.MeshWorldTransform.GetLocation() + WorldOffset,
				Geometry.MeshWorldTransform.GetRotation().Rotator());
		}
		Component->SetVisibility(Geometry.bVisible);
		Component->SetHiddenInGame(!Geometry.bVisible);
		Component->SetCastShadow(Geometry.bVisible);
	}
	for (int32 CanopyIndex = 0; CanopyIndex < CanopyComponents.Num(); ++CanopyIndex)
	{
		UStaticMeshComponent* Canopy = CanopyComponents[CanopyIndex];
		const int32 BranchIndex = SessionCanopyBranches[CanopyIndex];
		if (!IsValid(Canopy) || !BranchComponents.IsValidIndex(BranchIndex)
			|| !IsValid(BranchComponents[BranchIndex]) || !Sample.Branches.IsValidIndex(BranchIndex))
		{
			ReleaseResources();
			return false;
		}
		const FVector TipWorld = BranchComponents[BranchIndex]->GetComponentTransform()
			.TransformPosition(FVector(0.0, 0.0, MeshLocalMax.Z));
		const double Growth = FMath::Clamp((Progress - 0.55) / 0.45, 0.0, 1.0);
		const bool bVisible = Sample.Branches[BranchIndex].bVisible && Growth > 0.0;
		const double ClusterScale = (SessionCanopyScales.IsValidIndex(CanopyIndex) && SessionCanopyScales[CanopyIndex] > 0.0)
			? SessionCanopyScales[CanopyIndex] : CanopyWorldScale;
		const double Scale = ClusterScale * FMath::Max(Growth, 0.05);
		const FVector BaseOffset(0.0, 0.0, -CanopyLocalMin.Z * Scale);
		Canopy->SetWorldScale3D(FVector(Scale));
		Canopy->SetWorldLocationAndRotationNoPhysics(TipWorld + BaseOffset + WorldOffset, FRotator::ZeroRotator);
		Canopy->SetVisibility(bVisible);
		Canopy->SetHiddenInGame(!bVisible);
		Canopy->SetCastShadow(bVisible);
	}
	LastSample = Sample;
	return true;
}

bool ADYForestPresentationActor::ClearSession(ADYStagePresentation* PresentationOwner, const FGuid& Token)
{
	if (SessionOwner.Get() != PresentationOwner || !Token.IsValid() || Token != SessionContact.Token) { return false; }
	ReleaseResources();
	return true;
}

void ADYForestPresentationActor::ReleaseResources()
{
	SessionOwner.Reset();
	SessionContact = FDYStaffContactPresentationSnapshot();
	SessionLayout.Reset();
	SessionMesh = nullptr;
	CanopySessionMesh = nullptr;
	SessionCanopyBranches.Reset();
	CanopyLocalMin = FVector::ZeroVector;
	CanopyLocalMax = FVector::ZeroVector;
	LastSample = FDYForestGeometrySample();
	for (UStaticMeshComponent* Component : BranchComponents)
	{
		if (IsValid(Component))
		{
			Component->SetVisibility(false);
			Component->SetHiddenInGame(true);
			Component->SetCastShadow(false);
			RemoveInstanceComponent(Component);
			Component->DestroyComponent();
		}
	}
	BranchComponents.Reset();
	for (UStaticMeshComponent* Component : CanopyComponents)
	{
		if (IsValid(Component))
		{
			Component->SetVisibility(false);
			Component->SetHiddenInGame(true);
			Component->SetCastShadow(false);
			RemoveInstanceComponent(Component);
			Component->DestroyComponent();
		}
	}
	CanopyComponents.Reset();
}

void ADYForestPresentationActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	bEndingPlay = true;
	ReleaseResources();
	Super::EndPlay(EndPlayReason);
}
