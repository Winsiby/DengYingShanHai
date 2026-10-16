#include "Stage/DYStaffProjectionLibrary.h"

#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"

FDYStaffProjectionPoint UDYStaffProjectionLibrary::ProjectPointToScreen(
	const FVector& EmitterWorld, const FVector& SourceWorld, const FTransform& ScreenTransform,
	const FVector& LocalMin, const FVector& LocalMax)
{
	FDYStaffProjectionPoint Result;
	const FVector Scale = ScreenTransform.GetScale3D();
	if (EmitterWorld.ContainsNaN() || SourceWorld.ContainsNaN() || ScreenTransform.ContainsNaN()
		|| LocalMin.ContainsNaN() || LocalMax.ContainsNaN()
		|| FMath::Abs(Scale.X) <= UE_SMALL_NUMBER || FMath::Abs(Scale.Y) <= UE_SMALL_NUMBER
		|| FMath::Abs(Scale.Z) <= UE_SMALL_NUMBER || LocalMax.X <= LocalMin.X
		|| LocalMax.Y <= LocalMin.Y || LocalMax.Z <= LocalMin.Z)
	{
		return Result;
	}
	const FVector LightLocal = ScreenTransform.InverseTransformPosition(EmitterWorld);
	const FVector SourceLocal = ScreenTransform.InverseTransformPosition(SourceWorld);
	if (LightLocal.ContainsNaN() || SourceLocal.ContainsNaN()) { return Result; }
	// Choose the actual receiver face facing the emitter, not the cube's centre.
	double FaceX = 0.0;
	if (LightLocal.X < LocalMin.X) { FaceX = LocalMin.X; }
	else if (LightLocal.X > LocalMax.X) { FaceX = LocalMax.X; }
	else { return Result; }
	const double DirectionX = SourceLocal.X - LightLocal.X;
	if (FMath::Abs(DirectionX) <= UE_SMALL_NUMBER)
	{
		Result.Status = EDYStaffProjectionStatus::ParallelRay;
		return Result;
	}
	const double T = (FaceX - LightLocal.X) / DirectionX;
	if (!FMath::IsFinite(T)) { return Result; }
	if (T <= 1.0)
	{
		Result.Status = EDYStaffProjectionStatus::ScreenNotBeyondSource;
		return Result;
	}
	Result.ScreenLocalPosition = LightLocal + (SourceLocal - LightLocal) * T;
	Result.WorldPosition = ScreenTransform.TransformPosition(Result.ScreenLocalPosition);
	Result.ScreenUV = FVector2D(
		(Result.ScreenLocalPosition.Y - LocalMin.Y) / (LocalMax.Y - LocalMin.Y),
		(Result.ScreenLocalPosition.Z - LocalMin.Z) / (LocalMax.Z - LocalMin.Z));
	if (Result.ScreenLocalPosition.ContainsNaN() || Result.WorldPosition.ContainsNaN()
		|| Result.ScreenUV.ContainsNaN()) { return FDYStaffProjectionPoint(); }
	Result.RayParameter = T;
	// Floating-point round trips through a rotated/scaled frame can put an exact
	// edge infinitesimally outside. Numerical epsilon only, NOT a puzzle tolerance.
	constexpr double EdgeEpsilon = UE_DOUBLE_SMALL_NUMBER;
	Result.Status = Result.ScreenUV.X >= -EdgeEpsilon && Result.ScreenUV.X <= 1.0 + EdgeEpsilon
		&& Result.ScreenUV.Y >= -EdgeEpsilon && Result.ScreenUV.Y <= 1.0 + EdgeEpsilon
		? EDYStaffProjectionStatus::OnScreen : EDYStaffProjectionStatus::OutsideScreen;
	return Result;
}

FDYStaffProjectionCapture UDYStaffProjectionLibrary::CaptureStaffProjection(
	const ADYLightRigActor* Light, const ADYPuppetActor* Puppet, const UStaticMeshComponent* Screen)
{
	FDYStaffProjectionCapture Result;
	if (!IsValid(Light) || !IsValid(Puppet) || !IsValid(Screen) || !Screen->GetStaticMesh()
		|| !IsValid(Light->GetKeyLightComponent())) { return Result; }
	Result.Staff = Puppet->GetStaffGeometrySnapshot();
	if (!Result.Staff.bIsValid) { return Result; }
	Result.EmitterWorld = Light->GetKeyLightComponent()->GetComponentLocation();
	Result.ScreenTransform = Screen->GetComponentTransform();
	Screen->GetLocalBounds(Result.ScreenLocalMin, Result.ScreenLocalMax);
	Result.EndA = ProjectPointToScreen(Result.EmitterWorld, Result.Staff.EndAWorld,
		Result.ScreenTransform, Result.ScreenLocalMin, Result.ScreenLocalMax);
	Result.EndB = ProjectPointToScreen(Result.EmitterWorld, Result.Staff.EndBWorld,
		Result.ScreenTransform, Result.ScreenLocalMin, Result.ScreenLocalMax);
	Result.bHasGeometry = Result.EndA.Status != EDYStaffProjectionStatus::InvalidGeometry
		&& Result.EndB.Status != EDYStaffProjectionStatus::InvalidGeometry;
	return Result;
}
