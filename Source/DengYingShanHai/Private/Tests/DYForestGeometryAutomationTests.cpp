#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Engine/StaticMesh.h"
#include "Stage/DYForestGeometryLibrary.h"
#include <limits>

namespace DYForestGeometryTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;
	const FVector MeshMin(-2, -3, -5), MeshMax(2, 3, 5);

	FDYStaffContactPresentationSnapshot Contact(const FTransform& Screen = FTransform::Identity)
	{
		FDYStaffContactPresentationSnapshot C;
		C.bHasContact = true;
		C.Token = FGuid::NewGuid(); // Math fixture identity, NOT an accepted gameplay token.
		C.PuzzleId = TEXT("ForestGeometryFixture");
		auto& P = C.Projection;
		P.bHasGeometry = true;
		P.ScreenTransform = Screen;
		P.ScreenLocalMin = FVector(-50);
		P.ScreenLocalMax = FVector(50);
		P.EmitterWorld = Screen.TransformPosition(FVector(-300, 0, 0));
		P.Staff.bIsValid = true;
		P.Staff.LocalMin = FVector(-1);
		P.Staff.LocalMax = FVector(1);
		P.Staff.EndAWorld = Screen.TransformPosition(FVector(-175, 0, -15));
		P.Staff.ComponentTransform = FTransform(FQuat::Identity, P.Staff.EndAWorld + FVector(0, 0, 1));
		P.Staff.EndBWorld = P.Staff.EndAWorld + FVector(0, 0, 2);
		P.EndA = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, P.Staff.EndAWorld,
			Screen, P.ScreenLocalMin, P.ScreenLocalMax);
		P.EndB = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, P.Staff.EndBWorld,
			Screen, P.ScreenLocalMin, P.ScreenLocalMax);
		C.ContactWorldPosition = P.EndA.WorldPosition;
		return C;
	}

	TArray<FDYForestBranchDefinition> Layout()
	{
		FDYForestBranchDefinition Root;
		Root.EndScreenOffset = FVector2D(0, 10);
		Root.DiameterWorld = 1;
		Root.GrowthEnd = .3;
		FDYForestBranchDefinition Left;
		Left.ParentIndex = 0;
		Left.StartScreenOffset = Root.EndScreenOffset;
		Left.EndScreenOffset = FVector2D(-8, 20);
		Left.DiameterWorld = .5;
		Left.GrowthBegin = .3;
		FDYForestBranchDefinition Right = Left;
		Right.EndScreenOffset = FVector2D(8, 20);
		return {Root, Left, Right};
	}

	FDYForestGeometrySample Sample(double Progress = 1)
	{
		return UDYForestGeometryLibrary::SampleForestGeometry(Contact(), Layout(), Progress, MeshMin, MeshMax);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestRootTest,
	"DengYingShanHai.P03.ForestGeometry.PhysicalRootAndInverseProjection", DYForestGeometryTests::Flags)
bool FDYForestRootTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	const auto C = Contact();
	const auto D = Layout();
	const auto S = UDYForestGeometryLibrary::SampleForestGeometry(C, D, 1, MeshMin, MeshMax);
	if (!TestEqual(TEXT("Geometry sample valid"), S.Status, EDYForestGeometryStatus::Valid)) { return false; }
	TestTrue(TEXT("Root is actual physical A"), S.PhysicalRoot.Equals(C.Projection.Staff.EndAWorld));
	TestTrue(TEXT("Screen root equals given contact"), S.ShadowRoot.Equals(C.ContactWorldPosition));
	TestFalse(TEXT("Never place physical root on curtain"), S.PhysicalRoot.Equals(S.ShadowRoot));
	TestTrue(TEXT("Diagnostic token copied, not authorized"), S.ContactToken == C.Token);
	for (int32 I = 0; I < D.Num(); ++I)
	{
		const auto& P = C.Projection;
		const auto End = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, S.Branches[I].EndWorld,
			P.ScreenTransform, P.ScreenLocalMin, P.ScreenLocalMax);
		const FVector Expected = P.EndA.ScreenLocalPosition + FVector(0, D[I].EndScreenOffset.X, D[I].EndScreenOffset.Y);
		TestTrue(TEXT("Each source inverse-projects to authored receiver offset"), End.ScreenLocalPosition.Equals(Expected, UE_DOUBLE_SMALL_NUMBER));
		TestTrue(TEXT("Every source remains at root ray depth"), FMath::IsNearlyEqual(End.RayParameter, P.EndA.RayParameter, UE_DOUBLE_SMALL_NUMBER));
		if (I) { TestTrue(TEXT("Child physically joins completed parent"), S.Branches[I].StartWorld.Equals(S.Branches[D[I].ParentIndex].EndWorld)); }
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestReceiverTest,
	"DengYingShanHai.P03.ForestGeometry.RotatedScaledReceiver", DYForestGeometryTests::Flags)
bool FDYForestReceiverTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	for (const FVector Scale : {FVector(.3, 4, 7), FVector(-.3, 4, -7), FVector(2, .8, 3)})
	{
		const auto C = Contact(FTransform(FRotator(7, 32, 11), FVector(1000, -123, 405), Scale));
		const auto S = UDYForestGeometryLibrary::SampleForestGeometry(C, Layout(), 1, MeshMin, MeshMax);
		if (!TestEqual(TEXT("Rotated/nonuniform/negative-scale frame valid"), S.Status, EDYForestGeometryStatus::Valid)) { return false; }
		TestTrue(TEXT("Actual emitter-facing surface, not curtain centre"), FMath::IsNearlyEqual(C.Projection.EndA.ScreenLocalPosition.X, -50.0, UE_DOUBLE_SMALL_NUMBER));
		const auto End = UDYStaffProjectionLibrary::ProjectPointToScreen(C.Projection.EmitterWorld, S.Branches[1].EndWorld,
			C.Projection.ScreenTransform, C.Projection.ScreenLocalMin, C.Projection.ScreenLocalMax);
		TestTrue(TEXT("Authored local offset preserved"), End.ScreenLocalPosition.Equals(C.Projection.EndA.ScreenLocalPosition + FVector(0, -8, 20), UE_DOUBLE_SMALL_NUMBER));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestBoundsTest,
	"DengYingShanHai.P03.ForestGeometry.ActualAndOffCenterMeshBounds", DYForestGeometryTests::Flags)
bool FDYForestBoundsTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	const UStaticMesh* Cylinder = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (!TestNotNull(TEXT("Installed Engine Cylinder loaded"), Cylinder)) { return false; }
	const FBox Box = Cylinder->GetBoundingBox();
	const FBox OffCenter(FVector(2, -8, 6), FVector(8, -4, 19));
	for (const FBox& Bounds : {Box, OffCenter})
	{
		const auto S = UDYForestGeometryLibrary::SampleForestGeometry(Contact(), Layout(), 1, Bounds.Min, Bounds.Max);
		if (!TestEqual(TEXT("Real and non-centered bounds supported"), S.Status, EDYForestGeometryStatus::Valid)) { return false; }
		const FVector Center = Bounds.GetCenter();
		for (int32 I = 0; I < S.Branches.Num(); ++I)
		{
			const auto& B = S.Branches[I];
			TestTrue(TEXT("Actual local -Z endpoint precisely on branch start"), B.MeshWorldTransform.TransformPosition(FVector(Center.X, Center.Y, Bounds.Min.Z)).Equals(B.StartWorld, UE_DOUBLE_SMALL_NUMBER));
			TestTrue(TEXT("Actual local +Z endpoint precisely on branch end"), B.MeshWorldTransform.TransformPosition(FVector(Center.X, Center.Y, Bounds.Max.Z)).Equals(B.EndWorld, UE_DOUBLE_SMALL_NUMBER));
			const FVector Size = (Bounds.Max - Bounds.Min) * B.MeshWorldTransform.GetScale3D();
			TestTrue(TEXT("Both cross-section extents equal authored physical diameter"), FMath::IsNearlyEqual(Size.X, Layout()[I].DiameterWorld, UE_DOUBLE_SMALL_NUMBER) && FMath::IsNearlyEqual(Size.Y, Size.X, UE_DOUBLE_SMALL_NUMBER));
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestProgressTest,
	"DengYingShanHai.P03.ForestGeometry.NormalizedParentBeforeChild", DYForestGeometryTests::Flags)
bool FDYForestProgressTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	for (double Progress : {-2.0, 0.0, .15, .3, .65, 1.0, 2.0})
	{
		const auto S = Sample(Progress);
		if (!TestEqual(TEXT("Finite progress sampled safely"), S.Status, EDYForestGeometryStatus::Valid)) { return false; }
		TestEqual(TEXT("Stable layout cardinality"), S.Branches.Num(), 3);
		TestEqual(TEXT("Root visible only after beginning"), S.Branches[0].bVisible, Progress > 0);
		TestEqual(TEXT("Children hidden at exact parent-end boundary"), S.Branches[1].bVisible, Progress > .3);
		if (Progress <= 0)
		{
			for (const auto& B : S.Branches) { TestFalse(TEXT("No zero-length visible mesh"), B.bVisible); TestTrue(TEXT("Hidden mesh transform remains nonsingular identity"), B.MeshWorldTransform.Equals(FTransform::Identity)); }
		}
		if (S.Branches[1].bVisible) { TestEqual(TEXT("Visible child never floats off unfinished parent"), S.Branches[0].Portion, 1.0); }
	}
	TestTrue(TEXT("Root midpoint interpolation"), FMath::IsNearlyEqual(Sample(.15).Branches[0].Portion, .5, UE_DOUBLE_SMALL_NUMBER));
	TestTrue(TEXT("Child midpoint interpolation"), FMath::IsNearlyEqual(Sample(.65).Branches[1].Portion, .5, UE_DOUBLE_SMALL_NUMBER));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestTopologyTest,
	"DengYingShanHai.P03.ForestGeometry.InvalidTopologyAndAuthoring", DYForestGeometryTests::Flags)
bool FDYForestTopologyTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	TestTrue(TEXT("Fixture layout valid"), UDYForestGeometryLibrary::IsForestLayoutValid(Layout()));
	TestFalse(TEXT("Empty layout rejected"), UDYForestGeometryLibrary::IsForestLayoutValid({}));
	TArray<TArray<FDYForestBranchDefinition>> Invalid; // Plain native test data, not UPROPERTY.
	auto AddBad = [&Invalid](const auto& Mutation) { auto D = Layout(); Mutation(D); Invalid.Add(D); };
	AddBad([](auto& D) { D[0].ParentIndex = 1; });
	AddBad([](auto& D) { D[0].StartScreenOffset.X = 2; });
	AddBad([](auto& D) { D[1].ParentIndex = -1; });
	AddBad([](auto& D) { D[1].ParentIndex = 1; });
	AddBad([](auto& D) { D[1].ParentIndex = 99; });
	AddBad([](auto& D) { D[1].StartScreenOffset.X = 1; });
	AddBad([](auto& D) { D[1].EndScreenOffset = D[1].StartScreenOffset; });
	AddBad([](auto& D) { D[1].EndScreenOffset = FVector2D::ZeroVector; });
	AddBad([](auto& D) { D[2].EndScreenOffset = D[1].EndScreenOffset; });
	AddBad([](auto& D) { D[1].GrowthBegin = .29; });
	AddBad([](auto& D) { D[0].GrowthBegin = -1; });
	AddBad([](auto& D) { D[1].GrowthEnd = 1.1; });
	AddBad([](auto& D) { D[1].GrowthEnd = D[1].GrowthBegin; });
	AddBad([](auto& D) { D[1].DiameterWorld = 0; });
	AddBad([](auto& D) { D[1].DiameterWorld = -1; });
	AddBad([](auto& D) { D[1].DiameterWorld = 2; });
	AddBad([](auto& D) { D[1].DiameterWorld = std::numeric_limits<double>::infinity(); });
	AddBad([](auto& D) { D[1].GrowthBegin = std::numeric_limits<double>::quiet_NaN(); });
	AddBad([](auto& D) { D[1].EndScreenOffset.X = std::numeric_limits<double>::infinity(); });
	for (const auto& D : Invalid)
	{
		TestFalse(TEXT("Malformed tree rejected"), UDYForestGeometryLibrary::IsForestLayoutValid(D));
		const auto S = UDYForestGeometryLibrary::SampleForestGeometry(Contact(), D, 1, MeshMin, MeshMax);
		TestEqual(TEXT("Failure reason is layout"), S.Status, EDYForestGeometryStatus::InvalidLayout);
		TestTrue(TEXT("No partially generated tree leaked"), S.Branches.IsEmpty());
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestTinyGrowthTest,
	"DengYingShanHai.P03.ForestGeometry.TinyEmergenceKeepsValidAxis", DYForestGeometryTests::Flags)
bool FDYForestTinyGrowthTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	for (double Progress : {1e-6, 1e-8, .30000001, .300001})
	{
		const auto S = Sample(Progress);
		if (!TestEqual(TEXT("Tiny positive emergence still valid"), S.Status, EDYForestGeometryStatus::Valid)) { return false; }
		const int32 Emerging = Progress < .3 ? 0 : 1;
		const auto& B = S.Branches[Emerging];
		TestTrue(TEXT("Positive length above numerical epsilon visible"), B.bVisible);
		TestTrue(TEXT("Tiny geometry keeps normalized rotation"), B.MeshWorldTransform.IsRotationNormalized());
		const FVector Center = (MeshMin + MeshMax) * .5;
		TestTrue(TEXT("Tiny branch endpoint remains precise"), B.MeshWorldTransform.TransformPosition(FVector(Center.X, Center.Y, MeshMax.Z)).Equals(B.EndWorld, UE_DOUBLE_SMALL_NUMBER));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestFailureTest,
	"DengYingShanHai.P03.ForestGeometry.InvalidInputFailsClosed", DYForestGeometryTests::Flags)
bool FDYForestFailureTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	const double NaN = std::numeric_limits<double>::quiet_NaN();
	for (double Progress : {NaN, std::numeric_limits<double>::infinity(), -std::numeric_limits<double>::infinity()})
	{
		const auto S = UDYForestGeometryLibrary::SampleForestGeometry(Contact(), Layout(), Progress, MeshMin, MeshMax);
		TestEqual(TEXT("Non-finite progress refused"), S.Status, EDYForestGeometryStatus::InvalidProgress);
		TestTrue(TEXT("No partial output"), S.Branches.IsEmpty());
	}
	for (const FBox& Box : {FBox(FVector::ZeroVector, FVector::ZeroVector), FBox(FVector(-2), FVector(2, 2, -3)), FBox(FVector(NaN, -2, -2), FVector(2))})
	{
		TestEqual(TEXT("Degenerate/reversed/NaN mesh refused"), UDYForestGeometryLibrary::SampleForestGeometry(Contact(), Layout(), 1, Box.Min, Box.Max).Status, EDYForestGeometryStatus::InvalidMeshBounds);
	}
	TArray<FDYStaffContactPresentationSnapshot> Invalid;
	auto AddBad = [&Invalid](const auto& Mutation) { auto C = Contact(); Mutation(C); Invalid.Add(C); };
	AddBad([](auto& C) { C.bHasContact = false; });
	AddBad([](auto& C) { C.Token.Invalidate(); });
	AddBad([](auto& C) { C.ContactWorldPosition = C.Projection.Staff.EndAWorld; });
	AddBad([](auto& C) { C.Projection.Staff.EndAWorld.Z += 1; });
	AddBad([](auto& C) { C.Projection.EndA.RayParameter = 99; });
	AddBad([](auto& C) { C.Projection.EndA.Status = EDYStaffProjectionStatus::OutsideScreen; });
	AddBad([](auto& C) { C.Projection.ScreenTransform.SetScale3D(FVector(0, 1, 1)); });
	AddBad([](auto& C) { C.Projection.ScreenTransform.SetRotation(FQuat(0, 0, 0, 2)); });
	AddBad([](auto& C) { C.Projection.EmitterWorld.X = std::numeric_limits<double>::infinity(); });
	for (const auto& C : Invalid)
	{
		const auto S = UDYForestGeometryLibrary::SampleForestGeometry(C, Layout(), 1, MeshMin, MeshMax);
		TestEqual(TEXT("Inconsistent/invalid contact geometry refused"), S.Status, EDYForestGeometryStatus::InvalidContactGeometry);
		TestTrue(TEXT("No contact failure geometry"), S.Branches.IsEmpty());
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestVolumeTest,
	"DengYingShanHai.P03.ForestGeometry.EightCornerEnvelopeAndReceiverLimits", DYForestGeometryTests::Flags)
bool FDYForestVolumeTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	const auto C = Contact();
	const auto S = Sample();
	if (!TestEqual(TEXT("Valid volume sample"), S.Status, EDYForestGeometryStatus::Valid)) { return false; }
	for (const auto& B : S.Branches)
	{
		for (int32 Corner = 0; Corner < 8; ++Corner)
		{
			const FVector Local((Corner & 1) ? MeshMax.X : MeshMin.X, (Corner & 2) ? MeshMax.Y : MeshMin.Y, (Corner & 4) ? MeshMax.Z : MeshMin.Z);
			const auto P = UDYStaffProjectionLibrary::ProjectPointToScreen(C.Projection.EmitterWorld, B.MeshWorldTransform.TransformPosition(Local),
				C.Projection.ScreenTransform, C.Projection.ScreenLocalMin, C.Projection.ScreenLocalMax);
			TestEqual(TEXT("Actual transformed corner remains on receiver"), P.Status, EDYStaffProjectionStatus::OnScreen);
			TestTrue(TEXT("Envelope contains actual projected corner"), P.ScreenLocalPosition.Y >= B.ProjectedMin.X && P.ScreenLocalPosition.Y <= B.ProjectedMax.X
				&& P.ScreenLocalPosition.Z >= B.ProjectedMin.Y && P.ScreenLocalPosition.Z <= B.ProjectedMax.Y);
		}
	}
	auto D = Layout(); D[1].EndScreenOffset.X = -80;
	TestEqual(TEXT("Full centerline offscreen rejected even before growth"), UDYForestGeometryLibrary::SampleForestGeometry(C, D, 0, MeshMin, MeshMax).Status, EDYForestGeometryStatus::OutsideScreen);
	D = Layout(); for (auto& B : D) { B.DiameterWorld = 300; }
	const auto Wide = UDYForestGeometryLibrary::SampleForestGeometry(C, D, 1, MeshMin, MeshMax);
	TestEqual(TEXT("Volume failure found even with on-screen centerline"), Wide.Status, EDYForestGeometryStatus::OutsideScreen);
	TestTrue(TEXT("Failing first volume returns no geometry"), Wide.Branches.IsEmpty());
	D = Layout(); D[1].EndScreenOffset.X = 49.99;
	const TArray<FDYForestBranchDefinition> RootOnly = {D[0]};
	TestEqual(TEXT("Identical first branch succeeds by itself"), UDYForestGeometryLibrary::SampleForestGeometry(C, RootOnly, 1, MeshMin, MeshMax).Status, EDYForestGeometryStatus::Valid);
	const FVector SecondLocal = C.Projection.EndA.ScreenLocalPosition + FVector(0, D[1].EndScreenOffset.X, D[1].EndScreenOffset.Y);
	const FVector SecondSource = C.Projection.EmitterWorld + (C.Projection.ScreenTransform.TransformPosition(SecondLocal) - C.Projection.EmitterWorld) / C.Projection.EndA.RayParameter;
	TestEqual(TEXT("Second branch center endpoint is on screen"), UDYStaffProjectionLibrary::ProjectPointToScreen(C.Projection.EmitterWorld, SecondSource,
		C.Projection.ScreenTransform, C.Projection.ScreenLocalMin, C.Projection.ScreenLocalMax).Status, EDYStaffProjectionStatus::OnScreen);
	const auto LaterFailure = UDYForestGeometryLibrary::SampleForestGeometry(C, D, 1, MeshMin, MeshMax);
	TestEqual(TEXT("Later branch corner, not its centerline, fails"), LaterFailure.Status, EDYForestGeometryStatus::OutsideScreen);
	TestTrue(TEXT("Later failure discards earlier valid branch"), LaterFailure.Branches.IsEmpty());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestStaffFrameTest,
	"DengYingShanHai.P03.ForestGeometry.TransformedStaffAndOppositeReceiverFace", DYForestGeometryTests::Flags)
bool FDYForestStaffFrameTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	auto C = Contact(FTransform(FRotator(7, 32, 11), FVector(1000, -123, 405), FVector(.3, 4, 7)));
	const FVector DesiredA = C.Projection.Staff.EndAWorld;
	auto& Staff = C.Projection.Staff;
	Staff.LocalMin = FVector(-2, -3, -5); Staff.LocalMax = FVector(4, 8, 9);
	const FVector Center = (Staff.LocalMin + Staff.LocalMax) * .5;
	const FQuat Rotation = FRotator(17, -33, 5).Quaternion();
	const FVector Scale(-.4, 1.2, -2);
	const FVector LocalA(Center.X, Center.Y, Staff.LocalMin.Z);
	Staff.ComponentTransform = FTransform(Rotation, DesiredA - Rotation.RotateVector(LocalA * Scale), Scale);
	Staff.EndAWorld = Staff.ComponentTransform.TransformPosition(LocalA);
	Staff.EndBWorld = Staff.ComponentTransform.TransformPosition(FVector(Center.X, Center.Y, Staff.LocalMax.Z));
	TestEqual(TEXT("Rotated/nonuniform/negative Staff bounds reconstructed"), UDYForestGeometryLibrary::SampleForestGeometry(C, Layout(), 1, MeshMin, MeshMax).Status, EDYForestGeometryStatus::Valid);
	Staff.EndBWorld.Z += 1;
	TestEqual(TEXT("Changed B evidence also invalidates staff frame"), UDYForestGeometryLibrary::SampleForestGeometry(C, Layout(), 1, MeshMin, MeshMax).Status, EDYForestGeometryStatus::InvalidContactGeometry);
	C = Contact();
	auto& P = C.Projection;
	P.EmitterWorld = FVector(300, 0, 0);
	P.Staff.EndAWorld.X = 175; P.Staff.EndBWorld.X = 175;
	P.Staff.ComponentTransform.SetTranslation(P.Staff.EndAWorld + FVector(0, 0, 1));
	P.EndA = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, P.Staff.EndAWorld, P.ScreenTransform, P.ScreenLocalMin, P.ScreenLocalMax);
	C.ContactWorldPosition = P.EndA.WorldPosition;
	TestTrue(TEXT("Emitter on opposite side selects +X receiver face"), FMath::IsNearlyEqual(P.EndA.ScreenLocalPosition.X, 50.0, UE_DOUBLE_SMALL_NUMBER));
	TestEqual(TEXT("Opposite-side inverse projection valid"), UDYForestGeometryLibrary::SampleForestGeometry(C, Layout(), 1, MeshMin, MeshMax).Status, EDYForestGeometryStatus::Valid);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestValueTest,
	"DengYingShanHai.P03.ForestGeometry.ValuePurityAndAuthorityBoundary", DYForestGeometryTests::Flags)
bool FDYForestValueTest::RunTest(const FString& Parameters)
{
	using namespace DYForestGeometryTests;
	const auto C = Contact();
	const auto D = Layout();
	auto A = UDYForestGeometryLibrary::SampleForestGeometry(C, D, .65, MeshMin, MeshMax);
	const auto B = UDYForestGeometryLibrary::SampleForestGeometry(C, D, .65, MeshMin, MeshMax);
	if (!TestEqual(TEXT("Pure sample valid"), A.Status, EDYForestGeometryStatus::Valid)) { return false; }
	for (int32 I = 0; I < A.Branches.Num(); ++I) { TestTrue(TEXT("Repeat input produces identical value"), A.Branches[I].MeshWorldTransform.Equals(B.Branches[I].MeshWorldTransform)); }
	A.Branches[0].MeshWorldTransform.SetTranslation(FVector(999));
	TestFalse(TEXT("Output copy mutation never alters another result"), A.Branches[0].MeshWorldTransform.Equals(B.Branches[0].MeshWorldTransform));
	TestTrue(TEXT("Contact input root was not moved"), C.Projection.Staff.EndAWorld.Equals(FVector(-175, 0, -15)));
	TestTrue(TEXT("Authoring input not modified"), D[0].EndScreenOffset.Equals(FVector2D(0, 10)));
	auto UnrelatedIdentity = C; UnrelatedIdentity.Token = FGuid::NewGuid();
	TestEqual(TEXT("Pure math cannot authenticate a nonempty token; caller must"), UDYForestGeometryLibrary::SampleForestGeometry(UnrelatedIdentity, D, .65, MeshMin, MeshMax).Status, EDYForestGeometryStatus::Valid);
	return true;
}

#endif
