#include "Stage/DYForestGeometryLibrary.h"

#include "Math/RotationMatrix.h"

namespace DYForestGeometry
{
	// Round-trip arithmetic only. This is not a contact band or gameplay tolerance.
	constexpr double Epsilon = UE_DOUBLE_SMALL_NUMBER;

	bool HasUsableBounds(const FVector& Min, const FVector& Max)
	{
		return !Min.ContainsNaN() && !Max.ContainsNaN()
			&& Max.X > Min.X && Max.Y > Min.Y && Max.Z > Min.Z
			&& !(Max - Min).ContainsNaN();
	}

	FDYForestGeometrySample Failure(EDYForestGeometryStatus Status)
	{
		FDYForestGeometrySample Result;
		Result.Status = Status;
		return Result;
	}

	FDYStaffProjectionPoint Project(const FDYStaffProjectionCapture& P, const FVector& Source)
	{
		return UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, Source,
			P.ScreenTransform, P.ScreenLocalMin, P.ScreenLocalMax);
	}

	bool CheckContact(const FDYStaffContactPresentationSnapshot& C, FDYStaffProjectionPoint& Root)
	{
		const auto& P = C.Projection;
		const auto& S = P.Staff;
		if (!C.bHasContact || !C.Token.IsValid() || !P.bHasGeometry || !S.bIsValid
			|| P.ScreenTransform.ContainsNaN() || !P.ScreenTransform.IsRotationNormalized()
			|| S.ComponentTransform.ContainsNaN() || !S.ComponentTransform.IsRotationNormalized()
			|| !HasUsableBounds(S.LocalMin, S.LocalMax) || C.ContactWorldPosition.ContainsNaN()
			|| P.EndA.Status != EDYStaffProjectionStatus::OnScreen
			|| S.EndAWorld.ContainsNaN() || S.EndBWorld.ContainsNaN()) { return false; }
		const FVector StaffScale = S.ComponentTransform.GetScale3D();
		if (FMath::Abs(StaffScale.X) <= UE_SMALL_NUMBER || FMath::Abs(StaffScale.Y) <= UE_SMALL_NUMBER
			|| FMath::Abs(StaffScale.Z) <= UE_SMALL_NUMBER) { return false; }
		const FVector Center = (S.LocalMin + S.LocalMax) * .5;
		const FVector ActualA = S.ComponentTransform.TransformPosition(FVector(Center.X, Center.Y, S.LocalMin.Z));
		const FVector ActualB = S.ComponentTransform.TransformPosition(FVector(Center.X, Center.Y, S.LocalMax.Z));
		if (!ActualA.Equals(S.EndAWorld, Epsilon) || !ActualB.Equals(S.EndBWorld, Epsilon)) { return false; }
		Root = Project(P, ActualA);
		return Root.Status == EDYStaffProjectionStatus::OnScreen
			&& Root.WorldPosition.Equals(C.ContactWorldPosition, Epsilon)
			&& Root.WorldPosition.Equals(P.EndA.WorldPosition, Epsilon)
			&& Root.ScreenLocalPosition.Equals(P.EndA.ScreenLocalPosition, Epsilon)
			&& FMath::IsNearlyEqual(Root.RayParameter, P.EndA.RayParameter, Epsilon);
	}

	bool Lift(const FDYStaffProjectionCapture& P, const FDYStaffProjectionPoint& Root,
		const FVector2D& Offset, FVector& Source)
	{
		const FVector Local = Root.ScreenLocalPosition + FVector(0, Offset.X, Offset.Y);
		const FVector Target = P.ScreenTransform.TransformPosition(Local);
		Source = P.EmitterWorld + (Target - P.EmitterWorld) / Root.RayParameter;
		const auto Check = Project(P, Source);
		return Check.Status == EDYStaffProjectionStatus::OnScreen
			&& Check.WorldPosition.Equals(Target, Epsilon);
	}
}

bool UDYForestGeometryLibrary::IsForestLayoutValid(const TArray<FDYForestBranchDefinition>& Definition)
{
	if (Definition.IsEmpty()) { return false; }
	for (int32 Index = 0; Index < Definition.Num(); ++Index)
	{
		const auto& B = Definition[Index];
		const FVector2D Delta = B.EndScreenOffset - B.StartScreenOffset;
		if (B.StartScreenOffset.ContainsNaN() || B.EndScreenOffset.ContainsNaN() || Delta.ContainsNaN()
			|| !FMath::IsFinite(Delta.Size()) || Delta.Size() <= DYForestGeometry::Epsilon
			|| !FMath::IsFinite(B.DiameterWorld) || B.DiameterWorld <= 0.0
			|| !FMath::IsFinite(B.GrowthBegin) || !FMath::IsFinite(B.GrowthEnd)
			|| B.GrowthBegin < 0.0 || B.GrowthEnd > 1.0 || B.GrowthEnd <= B.GrowthBegin) { return false; }
		if (Index == 0)
		{
			if (B.ParentIndex != INDEX_NONE || !B.StartScreenOffset.Equals(FVector2D::ZeroVector, DYForestGeometry::Epsilon)) { return false; }
		}
		else
		{
			if (B.ParentIndex < 0 || B.ParentIndex >= Index) { return false; }
			const auto& Parent = Definition[B.ParentIndex];
			if (!B.StartScreenOffset.Equals(Parent.EndScreenOffset, DYForestGeometry::Epsilon)
				|| B.GrowthBegin < Parent.GrowthEnd || B.DiameterWorld > Parent.DiameterWorld) { return false; }
			// Two branches must not claim the same outgoing node (one tree, not a DAG).
			for (int32 Previous = 0; Previous < Index; ++Previous)
			{
				if (B.EndScreenOffset.Equals(Definition[Previous].EndScreenOffset, DYForestGeometry::Epsilon)) { return false; }
			}
		}
		if (B.EndScreenOffset.Equals(FVector2D::ZeroVector, DYForestGeometry::Epsilon)) { return false; }
	}
	return true;
}

FDYForestGeometrySample UDYForestGeometryLibrary::SampleForestGeometry(
	const FDYStaffContactPresentationSnapshot& Contact, const TArray<FDYForestBranchDefinition>& Definition,
	double NormalizedGrowth, const FVector& MeshLocalMin, const FVector& MeshLocalMax)
{
	using namespace DYForestGeometry;
	FDYStaffProjectionPoint Root;
	if (!CheckContact(Contact, Root)) { return Failure(EDYForestGeometryStatus::InvalidContactGeometry); }
	if (!IsForestLayoutValid(Definition)) { return Failure(EDYForestGeometryStatus::InvalidLayout); }
	if (!HasUsableBounds(MeshLocalMin, MeshLocalMax)) { return Failure(EDYForestGeometryStatus::InvalidMeshBounds); }
	if (!FMath::IsFinite(NormalizedGrowth)) { return Failure(EDYForestGeometryStatus::InvalidProgress); }
	const double Progress = FMath::Clamp(NormalizedGrowth, 0.0, 1.0);
	const FVector Extent = MeshLocalMax - MeshLocalMin;
	const FVector Center = (MeshLocalMax + MeshLocalMin) * .5;
	FDYForestGeometrySample Result;
	Result.ContactToken = Contact.Token;
	Result.PhysicalRoot = Contact.Projection.Staff.EndAWorld;
	Result.ShadowRoot = Root.WorldPosition;
	Result.Branches.Reserve(Definition.Num());
	for (const auto& B : Definition)
	{
		FDYForestBranchGeometry Branch;
		FVector FullEnd;
		if (!Lift(Contact.Projection, Root, B.StartScreenOffset, Branch.StartWorld)
			|| !Lift(Contact.Projection, Root, B.EndScreenOffset, FullEnd))
		{
			return Failure(EDYForestGeometryStatus::OutsideScreen);
		}
		Branch.Portion = FMath::Clamp((Progress - B.GrowthBegin) / (B.GrowthEnd - B.GrowthBegin), 0.0, 1.0);
		Branch.EndWorld = Branch.StartWorld + (FullEnd - Branch.StartWorld) * Branch.Portion;
		const FVector Direction = Branch.EndWorld - Branch.StartWorld;
		const double Length = Direction.Size();
		if (!FMath::IsFinite(Length)) { return Failure(EDYForestGeometryStatus::InvalidComputedGeometry); }
		Branch.bVisible = Length > Epsilon;
		if (Branch.bVisible)
		{
			const FVector Scale(B.DiameterWorld / Extent.X, B.DiameterWorld / Extent.Y, Length / Extent.Z);
			// MakeFromZ safe-normalizes using a squared-length threshold. Pass a
			// unit axis so a newly emerging, very short branch never yields a zero basis.
			const FQuat Rotation = FRotationMatrix::MakeFromZ(Direction / Length).ToQuat();
			const FVector Origin = (Branch.StartWorld + Branch.EndWorld) * .5 - Rotation.RotateVector(Center * Scale);
			Branch.MeshWorldTransform = FTransform(Rotation, Origin, Scale);
			if (Branch.MeshWorldTransform.ContainsNaN() || !Branch.MeshWorldTransform.IsRotationNormalized()
				|| !Branch.MeshWorldTransform.TransformPosition(FVector(Center.X, Center.Y, MeshLocalMin.Z)).Equals(Branch.StartWorld, Epsilon)
				|| !Branch.MeshWorldTransform.TransformPosition(FVector(Center.X, Center.Y, MeshLocalMax.Z)).Equals(Branch.EndWorld, Epsilon))
			{
				return Failure(EDYForestGeometryStatus::InvalidComputedGeometry);
			}
			bool bFirstCorner = true;
			for (int32 Corner = 0; Corner < 8; ++Corner)
			{
				const FVector Local((Corner & 1) ? MeshLocalMax.X : MeshLocalMin.X,
					(Corner & 2) ? MeshLocalMax.Y : MeshLocalMin.Y,
					(Corner & 4) ? MeshLocalMax.Z : MeshLocalMin.Z);
				const auto Projected = Project(Contact.Projection, Branch.MeshWorldTransform.TransformPosition(Local));
				if (Projected.Status != EDYStaffProjectionStatus::OnScreen) { return Failure(EDYForestGeometryStatus::OutsideScreen); }
				const FVector2D Point(Projected.ScreenLocalPosition.Y, Projected.ScreenLocalPosition.Z);
				if (bFirstCorner) { Branch.ProjectedMin = Branch.ProjectedMax = Point; bFirstCorner = false; }
				else
				{
					Branch.ProjectedMin.X = FMath::Min(Branch.ProjectedMin.X, Point.X);
					Branch.ProjectedMin.Y = FMath::Min(Branch.ProjectedMin.Y, Point.Y);
					Branch.ProjectedMax.X = FMath::Max(Branch.ProjectedMax.X, Point.X);
					Branch.ProjectedMax.Y = FMath::Max(Branch.ProjectedMax.Y, Point.Y);
				}
			}
		}
		Result.Branches.Add(Branch);
	}
	Result.Status = EDYForestGeometryStatus::Valid;
	return Result;
}
