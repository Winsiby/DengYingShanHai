#include "Stage/DYStaffDropLibrary.h"

#include "Stage/DYStaffContactLibrary.h"

namespace DYStaffDrop
{
	bool SamePoint(const FDYStaffProjectionPoint& A, const FDYStaffProjectionPoint& B)
	{
		return A.Status == B.Status && FMath::IsFinite(A.RayParameter)
			&& FMath::IsNearlyEqual(A.RayParameter, B.RayParameter, UE_DOUBLE_SMALL_NUMBER)
			&& A.WorldPosition.Equals(B.WorldPosition, UE_DOUBLE_SMALL_NUMBER)
			&& A.ScreenLocalPosition.Equals(B.ScreenLocalPosition, UE_DOUBLE_SMALL_NUMBER)
			&& A.ScreenUV.Equals(B.ScreenUV, UE_DOUBLE_SMALL_NUMBER);
	}
}

FDYStaffDropSample UDYStaffDropLibrary::SampleStaffDrop(
	const FDYStageResolvedPresentationSnapshot& Resolved, const double NormalizedProgress)
{
	FDYStaffDropSample Result;
	if (!FMath::IsFinite(NormalizedProgress))
	{
		Result.Status = EDYStaffDropStatus::InvalidProgress;
		return Result;
	}
	if (!Resolved.bHasSnapshot || !Resolved.Token.IsValid() || !Resolved.Light.bIsValid || !Resolved.Puppet.bIsValid)
	{
		return Result;
	}
	Result.Status = EDYStaffDropStatus::InvalidGeometry;
	const auto& P = Resolved.Projection;
	const auto& Staff = P.Staff;
	const FVector Scale = Staff.ComponentTransform.GetScale3D();
	if (!P.bHasGeometry || !Staff.bIsValid || Staff.LocalMin.ContainsNaN() || Staff.LocalMax.ContainsNaN()
		|| Staff.ComponentTransform.ContainsNaN() || !Staff.ComponentTransform.GetRotation().IsNormalized()
		|| P.ScreenTransform.ContainsNaN() || !P.ScreenTransform.GetRotation().IsNormalized()
		|| Staff.EndAWorld.ContainsNaN() || Staff.EndBWorld.ContainsNaN()
		|| FMath::Abs(Scale.X) <= UE_SMALL_NUMBER || FMath::Abs(Scale.Y) <= UE_SMALL_NUMBER
		|| FMath::Abs(Scale.Z) <= UE_SMALL_NUMBER || Staff.LocalMax.Z - Staff.LocalMin.Z <= UE_SMALL_NUMBER)
	{
		return Result;
	}
	// Match ADYPuppetActor's actual mesh-bound definition, rather than trusting stored tips/T.
	const FVector Center = (Staff.LocalMin + Staff.LocalMax) * 0.5;
	const FVector LocalA(Center.X, Center.Y, Staff.LocalMin.Z);
	const FVector LocalB(Center.X, Center.Y, Staff.LocalMax.Z);
	const FVector A = Staff.ComponentTransform.TransformPosition(LocalA);
	const FVector B = Staff.ComponentTransform.TransformPosition(LocalB);
	if (!A.Equals(Staff.EndAWorld, UE_DOUBLE_SMALL_NUMBER) || !B.Equals(Staff.EndBWorld, UE_DOUBLE_SMALL_NUMBER)) { return Result; }
	const auto InitialA = UDYStaffProjectionLibrary::ProjectPointToScreen(
		P.EmitterWorld, A, P.ScreenTransform, P.ScreenLocalMin, P.ScreenLocalMax);
	if (InitialA.Status != EDYStaffProjectionStatus::OnScreen || !DYStaffDrop::SamePoint(P.EndA, InitialA)) { return Result; }
	// B may legitimately be OutsideScreen: it is not the chosen contact tip.
	const auto Ground = UDYStaffContactLibrary::CaptureNarrativeGroundLine(P, Resolved.GroundLine.WorldAnchor);
	if (!Resolved.GroundLine.bIsValid || !Ground.bIsValid || !FMath::IsFinite(Resolved.GroundLine.ScreenLocalZ)
		|| !FMath::IsNearlyEqual(Ground.ScreenLocalZ, Resolved.GroundLine.ScreenLocalZ, UE_DOUBLE_SMALL_NUMBER))
	{
		Result.Status = EDYStaffDropStatus::InvalidGroundLine;
		return Result;
	}
	if (InitialA.ScreenLocalPosition.Z <= Ground.ScreenLocalZ)
	{
		Result.Status = EDYStaffDropStatus::NotAboveGround;
		return Result;
	}
	FVector TargetLocal = InitialA.ScreenLocalPosition;
	TargetLocal.Z = Ground.ScreenLocalZ; // Do not replace X/Y with the line anchor's location.
	const FVector ShadowGoal = P.ScreenTransform.TransformPosition(TargetLocal);
	const FVector GoalA = P.EmitterWorld + (ShadowGoal - P.EmitterWorld) / InitialA.RayParameter;
	const FVector FullDelta = GoalA - A;
	if (ShadowGoal.ContainsNaN() || GoalA.ContainsNaN() || FullDelta.ContainsNaN()) { return Result; }
	const double Alpha = FMath::Clamp(NormalizedProgress, 0.0, 1.0);
	const FVector Delta = FullDelta * Alpha;
	FTransform Transform = Staff.ComponentTransform;
	Transform.SetTranslation(Transform.GetTranslation() + Delta);
	if (Transform.ContainsNaN()) { return Result; }
	auto Projection = P;
	Projection.Staff.ComponentTransform = Transform;
	// Rebuild from the output transform, exactly as the live mesh capture does. Adding
	// Delta to cached tips can disagree after floating-point rounding at large coordinates.
	Projection.Staff.EndAWorld = Transform.TransformPosition(LocalA);
	Projection.Staff.EndBWorld = Transform.TransformPosition(LocalB);
	Projection.EndA = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, Projection.Staff.EndAWorld,
		P.ScreenTransform, P.ScreenLocalMin, P.ScreenLocalMax);
	Projection.EndB = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, Projection.Staff.EndBWorld,
		P.ScreenTransform, P.ScreenLocalMin, P.ScreenLocalMax);
	Projection.bHasGeometry = Projection.EndA.Status != EDYStaffProjectionStatus::InvalidGeometry
		&& Projection.EndB.Status != EDYStaffProjectionStatus::InvalidGeometry;
	if (!Projection.bHasGeometry || Projection.EndA.Status != EDYStaffProjectionStatus::OnScreen) { return Result; }
	// A mathematical endpoint must round-trip to the original line and horizontal point.
	// This verifies the value result only; it does not accept a live gameplay contact.
	if (Alpha == 1.0 && (!UDYStaffContactLibrary::IsStaffAOnNarrativeGround(Projection, Ground)
		|| !FMath::IsNearlyEqual(Projection.EndA.ScreenLocalPosition.X, InitialA.ScreenLocalPosition.X, UE_DOUBLE_SMALL_NUMBER)
		|| !FMath::IsNearlyEqual(Projection.EndA.ScreenLocalPosition.Y, InitialA.ScreenLocalPosition.Y, UE_DOUBLE_SMALL_NUMBER)))
	{
		return Result;
	}
	Result.Status = EDYStaffDropStatus::Valid;
	Result.Token = Resolved.Token;
	Result.PuzzleId = Resolved.PuzzleId;
	Result.NormalizedProgress = Alpha;
	Result.StaffWorldTransform = Transform;
	Result.FullTranslationWorld = FullDelta;
	Result.ShadowTargetWorld = ShadowGoal;
	Result.Projection = Projection;
	return Result;
}
