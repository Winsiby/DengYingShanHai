#include "Stage/DYStaffContactLibrary.h"

FDYNarrativeGroundLineSnapshot UDYStaffContactLibrary::CaptureNarrativeGroundLine(
	const FDYStaffProjectionCapture& Projection, const FVector& WorldAnchor)
{
	FDYNarrativeGroundLineSnapshot Result;
	const FVector Scale = Projection.ScreenTransform.GetScale3D();
	if (!Projection.bHasGeometry || WorldAnchor.ContainsNaN() || Projection.EmitterWorld.ContainsNaN()
		|| Projection.ScreenTransform.ContainsNaN() || Projection.ScreenLocalMin.ContainsNaN()
		|| Projection.ScreenLocalMax.ContainsNaN() || FMath::Abs(Scale.X) <= UE_SMALL_NUMBER
		|| FMath::Abs(Scale.Y) <= UE_SMALL_NUMBER || FMath::Abs(Scale.Z) <= UE_SMALL_NUMBER
		|| Projection.ScreenLocalMax.X <= Projection.ScreenLocalMin.X
		|| Projection.ScreenLocalMax.Y <= Projection.ScreenLocalMin.Y
		|| Projection.ScreenLocalMax.Z <= Projection.ScreenLocalMin.Z)
	{
		return Result;
	}
	const FVector Anchor = Projection.ScreenTransform.InverseTransformPosition(WorldAnchor);
	const FVector Emitter = Projection.ScreenTransform.InverseTransformPosition(Projection.EmitterWorld);
	if (Anchor.ContainsNaN() || Emitter.ContainsNaN()) { return Result; }
	double FaceX = 0.0;
	if (Emitter.X < Projection.ScreenLocalMin.X) { FaceX = Projection.ScreenLocalMin.X; }
	else if (Emitter.X > Projection.ScreenLocalMax.X) { FaceX = Projection.ScreenLocalMax.X; }
	else { return Result; }
	constexpr double Epsilon = UE_DOUBLE_SMALL_NUMBER;
	if (!FMath::IsNearlyEqual(Anchor.X, FaceX, Epsilon)
		|| Anchor.Y < Projection.ScreenLocalMin.Y - Epsilon || Anchor.Y > Projection.ScreenLocalMax.Y + Epsilon
		|| Anchor.Z < Projection.ScreenLocalMin.Z - Epsilon || Anchor.Z > Projection.ScreenLocalMax.Z + Epsilon)
	{
		return Result;
	}
	Result.bIsValid = true;
	Result.WorldAnchor = WorldAnchor;
	Result.ScreenLocalZ = Anchor.Z;
	return Result;
}

bool UDYStaffContactLibrary::IsStaffAOnNarrativeGround(const FDYStaffProjectionCapture& Projection,
	const FDYNarrativeGroundLineSnapshot& GroundLine)
{
	if (!Projection.bHasGeometry || !Projection.Staff.bIsValid || !GroundLine.bIsValid
		|| Projection.EndA.Status != EDYStaffProjectionStatus::OnScreen
		|| Projection.EndA.WorldPosition.ContainsNaN() || Projection.EndA.ScreenLocalPosition.ContainsNaN()
		|| !FMath::IsFinite(GroundLine.ScreenLocalZ)) { return false; }
	// Revalidate the saved line against the actual current receiver frame.
	const auto Rechecked = CaptureNarrativeGroundLine(Projection, GroundLine.WorldAnchor);
	return Rechecked.bIsValid
		&& FMath::IsNearlyEqual(Rechecked.ScreenLocalZ, GroundLine.ScreenLocalZ, UE_DOUBLE_SMALL_NUMBER)
		&& FMath::IsNearlyEqual(Projection.EndA.ScreenLocalPosition.Z, GroundLine.ScreenLocalZ, UE_DOUBLE_SMALL_NUMBER);
}
