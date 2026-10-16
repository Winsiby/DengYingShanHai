#include "Stage/DYForestPreflightLibrary.h"

namespace DYForestPreflight
{
	FDYForestPreflightResult Failure(EDYForestPreflightStatus Status)
	{
		FDYForestPreflightResult Result;
		Result.Status = Status;
		return Result;
	}

	bool HasUsableBounds(const FVector& Min, const FVector& Max)
	{
		return !Min.ContainsNaN() && !Max.ContainsNaN()
			&& Max.X > Min.X && Max.Y > Min.Y && Max.Z > Min.Z
			&& !(Max - Min).ContainsNaN();
	}

	bool HasUsableTransform(const FTransform& Transform)
	{
		const FVector Scale = Transform.GetScale3D();
		return !Transform.ContainsNaN() && Transform.IsRotationNormalized()
			&& FMath::Abs(Scale.X) > UE_SMALL_NUMBER
			&& FMath::Abs(Scale.Y) > UE_SMALL_NUMBER
			&& FMath::Abs(Scale.Z) > UE_SMALL_NUMBER;
	}
}

FDYForestPreflightResult UDYForestPreflightLibrary::CheckForestSilhouette(
	const FDYStaffContactPresentationSnapshot& Contact,
	const TArray<FDYForestBranchDefinition>& BranchDefinitions,
	const FVector& MeshMin, const FVector& MeshMax,
	const FVector& TorsoMin, const FVector& TorsoMax, const FTransform& TorsoTransform,
	const FVector& HeadMin, const FVector& HeadMax, const FTransform& HeadTransform,
	double PaddingFraction)
{
	using namespace DYForestPreflight;
	if (!FMath::IsFinite(PaddingFraction) || PaddingFraction < 0.0
		|| !HasUsableBounds(TorsoMin, TorsoMax) || !HasUsableBounds(HeadMin, HeadMax)
		|| !HasUsableTransform(TorsoTransform) || !HasUsableTransform(HeadTransform))
	{
		return Failure(EDYForestPreflightStatus::InvalidSilhouette);
	}

	const FDYForestGeometrySample Final = UDYForestGeometryLibrary::SampleForestGeometry(
		Contact, BranchDefinitions, 1.0, MeshMin, MeshMax);
	if (Final.Status != EDYForestGeometryStatus::Valid)
	{
		return Failure(Final.Status == EDYForestGeometryStatus::OutsideScreen
			? EDYForestPreflightStatus::OutsideScreen : EDYForestPreflightStatus::InvalidGeometry);
	}
	if (Final.Branches.IsEmpty() || Final.Branches.Num() != BranchDefinitions.Num())
	{
		return Failure(EDYForestPreflightStatus::InvalidGeometry);
	}

	const FDYStaffProjectionCapture& Projection = Contact.Projection;
	double MinY = 0.0, MaxY = 0.0, MinZ = 0.0;
	bool bFirstCorner = true;
	for (int32 Body = 0; Body < 2; ++Body)
	{
		const FVector& LocalMin = Body == 0 ? TorsoMin : HeadMin;
		const FVector& LocalMax = Body == 0 ? TorsoMax : HeadMax;
		const FTransform& Transform = Body == 0 ? TorsoTransform : HeadTransform;
		for (int32 Corner = 0; Corner < 8; ++Corner)
		{
			const FVector Local((Corner & 1) ? LocalMax.X : LocalMin.X,
				(Corner & 2) ? LocalMax.Y : LocalMin.Y,
				(Corner & 4) ? LocalMax.Z : LocalMin.Z);
			const FDYStaffProjectionPoint Point = UDYStaffProjectionLibrary::ProjectPointToScreen(
				Projection.EmitterWorld, Transform.TransformPosition(Local), Projection.ScreenTransform,
				Projection.ScreenLocalMin, Projection.ScreenLocalMax);
			if (Point.Status != EDYStaffProjectionStatus::OnScreen)
			{
				return Failure(Point.Status == EDYStaffProjectionStatus::OutsideScreen
					? EDYForestPreflightStatus::OutsideScreen : EDYForestPreflightStatus::InvalidSilhouette);
			}
			if (bFirstCorner)
			{
				MinY = MaxY = Point.ScreenLocalPosition.Y;
				MinZ = Point.ScreenLocalPosition.Z;
				bFirstCorner = false;
			}
			else
			{
				MinY = FMath::Min(MinY, Point.ScreenLocalPosition.Y);
				MaxY = FMath::Max(MaxY, Point.ScreenLocalPosition.Y);
				MinZ = FMath::Min(MinZ, Point.ScreenLocalPosition.Z);
			}
		}
	}

	const double PaddingY = (Projection.ScreenLocalMax.Y - Projection.ScreenLocalMin.Y) * PaddingFraction;
	const double PaddingZ = (Projection.ScreenLocalMax.Z - Projection.ScreenLocalMin.Z) * PaddingFraction;
	MinY -= PaddingY;
	MaxY += PaddingY;
	MinZ -= PaddingZ;
	if (!FMath::IsFinite(MinY) || !FMath::IsFinite(MaxY) || !FMath::IsFinite(MinZ))
	{
		return Failure(EDYForestPreflightStatus::InvalidSilhouette);
	}
	for (const FDYForestBranchGeometry& Branch : Final.Branches)
	{
		if (!Branch.bVisible) { continue; }
		if (Branch.ProjectedMin.ContainsNaN() || Branch.ProjectedMax.ContainsNaN()
			|| Branch.ProjectedMax.X < Branch.ProjectedMin.X
			|| Branch.ProjectedMax.Y < Branch.ProjectedMin.Y)
		{
			return Failure(EDYForestPreflightStatus::InvalidGeometry);
		}
		// Exact Dev Python rule: touching any protected boundary is an overlap.
		if (!(Branch.ProjectedMax.X < MinY || Branch.ProjectedMin.X > MaxY
			|| Branch.ProjectedMax.Y < MinZ))
		{
			return Failure(EDYForestPreflightStatus::ProtectedOverlap);
		}
	}
	FDYForestPreflightResult Result;
	Result.Status = EDYForestPreflightStatus::Valid;
	Result.FinalGeometry = Final;
	return Result;
}
