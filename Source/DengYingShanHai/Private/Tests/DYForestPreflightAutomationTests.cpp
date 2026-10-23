#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Stage/DYForestPreflightLibrary.h"
#include "UObject/UnrealType.h"
#include <limits>

namespace DYForestPreflightTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;
	const FVector MeshMin(-2, -3, -5), MeshMax(2, 3, 5);
	const FVector BodyMin(-.25, -.25, -.25), BodyMax(.25, .25, .25);

	FDYStaffContactPresentationSnapshot Contact(const FTransform& Screen = FTransform::Identity)
	{
		FDYStaffContactPresentationSnapshot C;
		C.bHasContact = true;
		C.Token = FGuid::NewGuid(); // Math identity only; no runtime authorization is asserted.
		C.PuzzleId = TEXT("ForestPreflightFixture");
		auto& P = C.Projection;
		P.bHasGeometry = true;
		P.ScreenTransform = Screen;
		P.ScreenLocalMin = FVector(-50);
		P.ScreenLocalMax = FVector(50);
		P.EmitterWorld = Screen.TransformPosition(FVector(-300, 0, 0));
		P.Staff.bIsValid = true;
		P.Staff.LocalMin = FVector(-1);
		P.Staff.LocalMax = FVector(1);
		P.Staff.ComponentTransform = FTransform(FQuat::Identity, FVector(-175, 0, -14)) * Screen;
		P.Staff.EndAWorld = P.Staff.ComponentTransform.TransformPosition(FVector(0, 0, -1));
		P.Staff.EndBWorld = P.Staff.ComponentTransform.TransformPosition(FVector(0, 0, 1));
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

	FTransform Torso(const FTransform& Screen = FTransform::Identity)
	{
		return FTransform(FQuat::Identity, FVector(-175, 15, -5)) * Screen;
	}
	FTransform Head(const FTransform& Screen = FTransform::Identity)
	{
		return FTransform(FQuat::Identity, FVector(-175, 18, 8)) * Screen;
	}
	FDYForestPreflightResult Check(const FDYStaffContactPresentationSnapshot& C,
		const TArray<FDYForestBranchDefinition>& D, const FTransform& T, const FTransform& H, double Padding = .02)
	{
		return UDYForestPreflightLibrary::CheckForestSilhouette(C, D, MeshMin, MeshMax,
			BodyMin, BodyMax, T, BodyMin, BodyMax, H, Padding);
	}
	void CheckFailure(FAutomationTestBase& Test, const FDYForestPreflightResult& Result, EDYForestPreflightStatus Status)
	{
		Test.TestEqual(TEXT("Expected failure status"), Result.Status, Status);
		Test.TestTrue(TEXT("Failure has no partial branches"), Result.FinalGeometry.Branches.IsEmpty());
		Test.TestFalse(TEXT("Failure has no usable geometry"), Result.FinalGeometry.Status == EDYForestGeometryStatus::Valid);
		Test.TestFalse(TEXT("Failure has no diagnostic token payload"), Result.FinalGeometry.ContactToken.IsValid());
		Test.TestTrue(TEXT("Failure has no physical root payload"), Result.FinalGeometry.PhysicalRoot.IsZero());
		Test.TestTrue(TEXT("Failure has no shadow root payload"), Result.FinalGeometry.ShadowRoot.IsZero());
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestPreflightValidTest,
	"DengYingShanHai.P03.ForestPreflight.ValidFinalGeometry", DYForestPreflightTests::Flags)
bool FDYForestPreflightValidTest::RunTest(const FString& Parameters)
{
	using namespace DYForestPreflightTests;
	const auto C = Contact();
	const auto D = Layout();
	const auto Result = Check(C, D, Torso(), Head());
	if (!TestEqual(TEXT("Separated silhouette passes"), Result.Status, EDYForestPreflightStatus::Valid)) { return false; }
	const auto Expected = UDYForestGeometryLibrary::SampleForestGeometry(C, D, 1, MeshMin, MeshMax);
	TestEqual(TEXT("Full-growth payload is valid"), Result.FinalGeometry.Status, EDYForestGeometryStatus::Valid);
	TestEqual(TEXT("Final branch count retained"), Result.FinalGeometry.Branches.Num(), D.Num());
	TestTrue(TEXT("Actual physical root retained"), Result.FinalGeometry.PhysicalRoot.Equals(Expected.PhysicalRoot, 0));
	TestTrue(TEXT("Actual shadow root retained"), Result.FinalGeometry.ShadowRoot.Equals(Expected.ShadowRoot, 0));
	TestTrue(TEXT("Token copied as diagnostic value"), Result.FinalGeometry.ContactToken == C.Token);
	for (int32 I = 0; I < Expected.Branches.Num(); ++I)
	{
		const auto& Actual = Result.FinalGeometry.Branches[I];
		TestTrue(TEXT("Full-growth branch is visible"), Actual.bVisible);
		TestEqual(TEXT("Full-growth portion is one"), Actual.Portion, 1.0);
		TestTrue(TEXT("Existing mesh transform retained"), Actual.MeshWorldTransform.Equals(Expected.Branches[I].MeshWorldTransform, 0));
		TestTrue(TEXT("Existing projected envelope retained"), Actual.ProjectedMin.Equals(Expected.Branches[I].ProjectedMin, 0)
			&& Actual.ProjectedMax.Equals(Expected.Branches[I].ProjectedMax, 0));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestPreflightBodiesTest,
	"DengYingShanHai.P03.ForestPreflight.TorsoAndHeadSeparatelyProtect", DYForestPreflightTests::Flags)
bool FDYForestPreflightBodiesTest::RunTest(const FString& Parameters)
{
	using namespace DYForestPreflightTests;
	const FTransform Overlap(FQuat::Identity, FVector(-175, 0, -12));
	CheckFailure(*this, Check(Contact(), Layout(), Overlap, Head()), EDYForestPreflightStatus::ProtectedOverlap);
	CheckFailure(*this, Check(Contact(), Layout(), Torso(), Overlap), EDYForestPreflightStatus::ProtectedOverlap);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestPreflightPaddingTest,
	"DengYingShanHai.P03.ForestPreflight.CallerPaddingAndUpwardEnvelope", DYForestPreflightTests::Flags)
bool FDYForestPreflightPaddingTest::RunTest(const FString& Parameters)
{
	using namespace DYForestPreflightTests;
	const FTransform NearTorso(FQuat::Identity, FVector(-175, 5, -15));
	const FTransform NearHead(FQuat::Identity, FVector(-175, 5, -10));
	TestEqual(TEXT("Unpadded lateral gap is clear"), Check(Contact(), Layout(), NearTorso, NearHead, 0).Status, EDYForestPreflightStatus::Valid);
	CheckFailure(*this, Check(Contact(), Layout(), NearTorso, NearHead, .02), EDYForestPreflightStatus::ProtectedOverlap);
	const FTransform LowBody(FQuat::Identity, FVector(-175, 0, -20));
	CheckFailure(*this, Check(Contact(), Layout(), LowBody, LowBody, 0), EDYForestPreflightStatus::ProtectedOverlap);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestPreflightBoundaryTest,
	"DengYingShanHai.P03.ForestPreflight.TouchingBoundariesAreProtected", DYForestPreflightTests::Flags)
bool FDYForestPreflightBoundaryTest::RunTest(const FString& Parameters)
{
	using namespace DYForestPreflightTests;
	const auto C = Contact();
	const TArray<FDYForestBranchDefinition> D = {Layout()[0]};
	const auto Final = UDYForestGeometryLibrary::SampleForestGeometry(C, D, 1, MeshMin, MeshMax);
	if (!TestEqual(TEXT("Boundary fixture forest valid"), Final.Status, EDYForestGeometryStatus::Valid)) { return false; }
	// Use the actual extremal source corners, avoiding a guessed MakeFromZ basis.
	FVector RightSource = FVector::ZeroVector, UpperSource = FVector::ZeroVector;
	double RightY = -std::numeric_limits<double>::max(), UpperZ = -std::numeric_limits<double>::max();
	for (int32 Corner = 0; Corner < 8; ++Corner)
	{
		const FVector Local((Corner & 1) ? MeshMax.X : MeshMin.X,
			(Corner & 2) ? MeshMax.Y : MeshMin.Y, (Corner & 4) ? MeshMax.Z : MeshMin.Z);
		const FVector Source = Final.Branches[0].MeshWorldTransform.TransformPosition(Local);
		const auto Point = UDYStaffProjectionLibrary::ProjectPointToScreen(C.Projection.EmitterWorld,
			Source, C.Projection.ScreenTransform, C.Projection.ScreenLocalMin, C.Projection.ScreenLocalMax);
		if (Point.ScreenLocalPosition.Y > RightY) { RightY = Point.ScreenLocalPosition.Y; RightSource = Source; }
		if (Point.ScreenLocalPosition.Z > UpperZ) { UpperZ = Point.ScreenLocalPosition.Z; UpperSource = Source; }
	}
	const FVector TouchMin(-.5, 0, -1), TouchMax(0, .5, 1);
	const FTransform Touch(FQuat::Identity, RightSource);
	const auto Edge = UDYStaffProjectionLibrary::ProjectPointToScreen(C.Projection.EmitterWorld,
		Touch.TransformPosition(FVector(TouchMax.X, TouchMin.Y, TouchMin.Z)), C.Projection.ScreenTransform,
		C.Projection.ScreenLocalMin, C.Projection.ScreenLocalMax);
	TestEqual(TEXT("Exact lateral boundary fixture"), Edge.ScreenLocalPosition.Y, Final.Branches[0].ProjectedMax.X);
	CheckFailure(*this, UDYForestPreflightLibrary::CheckForestSilhouette(C, D, MeshMin, MeshMax,
		TouchMin, TouchMax, Touch, TouchMin, TouchMax, Touch, 0), EDYForestPreflightStatus::ProtectedOverlap);
	FVector SeparatedMin = TouchMin;
	SeparatedMin.Y += .001;
	TestEqual(TEXT("Strict lateral separation passes"), UDYForestPreflightLibrary::CheckForestSilhouette(C, D, MeshMin, MeshMax,
		SeparatedMin, TouchMax, Touch, SeparatedMin, TouchMax, Touch, 0).Status, EDYForestPreflightStatus::Valid);
	const FVector LowMin(0, -.5, 0), LowMax(.5, .5, 1);
	const FTransform LowerTouch(FQuat::Identity, UpperSource);
	const auto LowerEdge = UDYStaffProjectionLibrary::ProjectPointToScreen(C.Projection.EmitterWorld,
		LowerTouch.TransformPosition(LowMin), C.Projection.ScreenTransform, C.Projection.ScreenLocalMin, C.Projection.ScreenLocalMax);
	TestEqual(TEXT("Exact lower boundary fixture"), LowerEdge.ScreenLocalPosition.Z, Final.Branches[0].ProjectedMax.Y);
	CheckFailure(*this, UDYForestPreflightLibrary::CheckForestSilhouette(C, D, MeshMin, MeshMax,
		LowMin, LowMax, LowerTouch, LowMin, LowMax, LowerTouch, 0), EDYForestPreflightStatus::ProtectedOverlap);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestPreflightInvalidTest,
	"DengYingShanHai.P03.ForestPreflight.InvalidInputsHaveNoPayload", DYForestPreflightTests::Flags)
bool FDYForestPreflightInvalidTest::RunTest(const FString& Parameters)
{
	using namespace DYForestPreflightTests;
	const double NaN = std::numeric_limits<double>::quiet_NaN();
	const double Inf = std::numeric_limits<double>::infinity();
	for (double Padding : {-1.0, NaN, Inf, -Inf, std::numeric_limits<double>::max()})
	{
		CheckFailure(*this, Check(Contact(), Layout(), Torso(), Head(), Padding), EDYForestPreflightStatus::InvalidSilhouette);
	}
	for (const FBox& Box : {FBox(FVector::ZeroVector, FVector::ZeroVector), FBox(FVector(1), FVector(-1)),
		FBox(FVector(NaN, 0, 0), FVector(1)), FBox(FVector(-1), FVector(Inf, 1, 1))})
	{
		CheckFailure(*this, UDYForestPreflightLibrary::CheckForestSilhouette(Contact(), Layout(), MeshMin, MeshMax,
			Box.Min, Box.Max, Torso(), BodyMin, BodyMax, Head(), .02), EDYForestPreflightStatus::InvalidSilhouette);
		CheckFailure(*this, UDYForestPreflightLibrary::CheckForestSilhouette(Contact(), Layout(), MeshMin, MeshMax,
			BodyMin, BodyMax, Torso(), Box.Min, Box.Max, Head(), .02), EDYForestPreflightStatus::InvalidSilhouette);
	}
	FTransform ZeroScale = Torso();
	ZeroScale.SetScale3D(FVector(0, 1, 1));
	CheckFailure(*this, Check(Contact(), Layout(), ZeroScale, Head()), EDYForestPreflightStatus::InvalidSilhouette);
	FTransform BadRotation = Head();
	BadRotation.SetRotation(FQuat(0, 0, 0, 2));
	CheckFailure(*this, Check(Contact(), Layout(), Torso(), BadRotation), EDYForestPreflightStatus::InvalidSilhouette);
	auto BadContact = Contact();
	BadContact.Projection.Staff.EndBWorld.Z += 1;
	CheckFailure(*this, Check(BadContact, Layout(), Torso(), Head()), EDYForestPreflightStatus::InvalidGeometry);
	BadContact = Contact();
	BadContact.Projection.EmitterWorld.X = Inf;
	CheckFailure(*this, Check(BadContact, Layout(), Torso(), Head()), EDYForestPreflightStatus::InvalidGeometry);
	CheckFailure(*this, Check(Contact(), {}, Torso(), Head()), EDYForestPreflightStatus::InvalidGeometry);
	auto BadLayout = Layout();
	BadLayout[0].DiameterWorld = NaN;
	CheckFailure(*this, Check(Contact(), BadLayout, Torso(), Head()), EDYForestPreflightStatus::InvalidGeometry);
	CheckFailure(*this, UDYForestPreflightLibrary::CheckForestSilhouette(Contact(), Layout(), MeshMin, MeshMin,
		BodyMin, BodyMax, Torso(), BodyMin, BodyMax, Head(), .02), EDYForestPreflightStatus::InvalidGeometry);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestPreflightScreenTest,
	"DengYingShanHai.P03.ForestPreflight.AllSixteenCornersStayOnScreen", DYForestPreflightTests::Flags)
bool FDYForestPreflightScreenTest::RunTest(const FString& Parameters)
{
	using namespace DYForestPreflightTests;
	const auto C = Contact();
	const FVector WideMin(-.25, -1, -.25), WideMax(.25, 1, .25);
	const FTransform OffscreenCorner(FQuat::Identity, FVector(-175, 24.8, 0));
	TestEqual(TEXT("Body centre is on screen; corners still matter"), UDYStaffProjectionLibrary::ProjectPointToScreen(
		C.Projection.EmitterWorld, OffscreenCorner.GetTranslation(), C.Projection.ScreenTransform,
		C.Projection.ScreenLocalMin, C.Projection.ScreenLocalMax).Status, EDYStaffProjectionStatus::OnScreen);
	CheckFailure(*this, UDYForestPreflightLibrary::CheckForestSilhouette(C, Layout(), MeshMin, MeshMax,
		WideMin, WideMax, OffscreenCorner, BodyMin, BodyMax, Head(), .02), EDYForestPreflightStatus::OutsideScreen);
	CheckFailure(*this, UDYForestPreflightLibrary::CheckForestSilhouette(C, Layout(), MeshMin, MeshMax,
		BodyMin, BodyMax, Torso(), WideMin, WideMax, OffscreenCorner, .02), EDYForestPreflightStatus::OutsideScreen);
	auto OutsideLayout = Layout();
	OutsideLayout[1].EndScreenOffset.X = -80;
	CheckFailure(*this, Check(C, OutsideLayout, Torso(), Head()), EDYForestPreflightStatus::OutsideScreen);
	const FTransform BeyondReceiver(FQuat::Identity, FVector(100, 0, 0));
	CheckFailure(*this, Check(C, Layout(), Torso(), BeyondReceiver), EDYForestPreflightStatus::InvalidSilhouette);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestPreflightFrameTest,
	"DengYingShanHai.P03.ForestPreflight.RotatedReceiverAndValuePurity", DYForestPreflightTests::Flags)
bool FDYForestPreflightFrameTest::RunTest(const FString& Parameters)
{
	using namespace DYForestPreflightTests;
	for (const FVector Scale : {FVector(.3, 4, 7), FVector(-.3, 4, -7), FVector(2, .8, 3)})
	{
		const FTransform Screen(FRotator(7, 32, 11), FVector(1000, -123, 405), Scale);
		const auto C = Contact(Screen);
		const auto Original = C;
		const auto D = Layout();
		const auto BeforeD = D;
		const FTransform T = Torso(Screen), H = Head(Screen);
		auto Result = Check(C, D, T, H);
		if (!TestEqual(TEXT("Rotated, nonuniform and mirrored receiver passes"), Result.Status, EDYForestPreflightStatus::Valid)) { return false; }
		const auto Repeated = Check(C, D, T, H);
		for (int32 I = 0; I < D.Num(); ++I)
		{
			TestTrue(TEXT("Repeat input gives same mesh values"), Result.FinalGeometry.Branches[I].MeshWorldTransform.Equals(Repeated.FinalGeometry.Branches[I].MeshWorldTransform, 0));
			TestTrue(TEXT("Authoring start/end inputs unchanged"), D[I].StartScreenOffset.Equals(BeforeD[I].StartScreenOffset, 0)
				&& D[I].EndScreenOffset.Equals(BeforeD[I].EndScreenOffset, 0));
			TestEqual(TEXT("Authoring diameter unchanged"), D[I].DiameterWorld, BeforeD[I].DiameterWorld);
		}
		TestTrue(TEXT("Contact and transforms unchanged"), C.Token == Original.Token
			&& C.ContactWorldPosition.Equals(Original.ContactWorldPosition, 0)
			&& C.Projection.Staff.ComponentTransform.Equals(Original.Projection.Staff.ComponentTransform, 0)
			&& C.Projection.ScreenTransform.Equals(Original.Projection.ScreenTransform, 0)
			&& T.Equals(Torso(Screen), 0) && H.Equals(Head(Screen), 0));
		Result.FinalGeometry.Branches[0].MeshWorldTransform.SetTranslation(FVector(999));
		TestFalse(TEXT("Returned geometry is an independent value copy"), Result.FinalGeometry.Branches[0].MeshWorldTransform.Equals(Repeated.FinalGeometry.Branches[0].MeshWorldTransform));
		auto Unauthenticated = C;
		Unauthenticated.Token = FGuid::NewGuid();
		TestEqual(TEXT("Math does not authenticate a nonempty identity"), Check(Unauthenticated, D, T, H).Status, EDYForestPreflightStatus::Valid);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestPreflightReflectionTest,
	"DengYingShanHai.P03.ForestPreflight.RuntimeBlueprintValueContract", DYForestPreflightTests::Flags)
bool FDYForestPreflightReflectionTest::RunTest(const FString& Parameters)
{
	const UFunction* Fn = UDYForestPreflightLibrary::StaticClass()->FindFunctionByName(TEXT("CheckForestSilhouette"));
	if (!TestNotNull(TEXT("Pure function is reflected"), Fn)) { return false; }
	TestTrue(TEXT("Static BlueprintPure function"), Fn->HasAllFunctionFlags(FUNC_BlueprintPure | FUNC_Static));
	TestFalse(TEXT("Available in runtime"), Fn->HasAnyFunctionFlags(FUNC_EditorOnly));
#if WITH_EDITOR
	TestFalse(TEXT("No WorldContext"), Fn->HasMetaData(TEXT("WorldContext")));
	TestFalse(TEXT("No latent time owner"), Fn->HasMetaData(TEXT("Latent")));
	TestFalse(TEXT("No DevelopmentOnly removal"), Fn->HasMetaData(TEXT("DevelopmentOnly")));
#endif
	for (TFieldIterator<FProperty> It(Fn); It; ++It)
	{
		if (It->HasAnyPropertyFlags(CPF_Parm))
		{
			TestNull(TEXT("No UObject or Actor parameter"), CastField<FObjectPropertyBase>(*It));
		}
	}
	for (const FName Name : {FName(TEXT("Status")), FName(TEXT("FinalGeometry"))})
	{
		const FProperty* Output = FindFProperty<FProperty>(FDYForestPreflightResult::StaticStruct(), Name);
		TestTrue(TEXT("Output is a Blueprint readonly value"), Output && Output->HasAllPropertyFlags(CPF_BlueprintVisible | CPF_BlueprintReadOnly));
	}
	TestEqual(TEXT("Callable without a World or Actor"), DYForestPreflightTests::Check(DYForestPreflightTests::Contact(),
		DYForestPreflightTests::Layout(), DYForestPreflightTests::Torso(), DYForestPreflightTests::Head()).Status, EDYForestPreflightStatus::Valid);
	return true;
}

#endif
