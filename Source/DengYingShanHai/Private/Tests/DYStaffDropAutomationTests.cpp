#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Stage/DYStaffDropLibrary.h"
#include "Stage/DYStaffContactLibrary.h"
#include "UObject/UnrealType.h"
#include <limits>

namespace DYStaffDropTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;

	void RefreshStaff(FDYStageResolvedPresentationSnapshot& S)
	{
		auto& P = S.Projection;
		const FVector Center = (P.Staff.LocalMin + P.Staff.LocalMax) * .5;
		P.Staff.EndAWorld = P.Staff.ComponentTransform.TransformPosition(FVector(Center.X, Center.Y, P.Staff.LocalMin.Z));
		P.Staff.EndBWorld = P.Staff.ComponentTransform.TransformPosition(FVector(Center.X, Center.Y, P.Staff.LocalMax.Z));
		P.EndA = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, P.Staff.EndAWorld,
			P.ScreenTransform, P.ScreenLocalMin, P.ScreenLocalMax);
		P.EndB = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, P.Staff.EndBWorld,
			P.ScreenTransform, P.ScreenLocalMin, P.ScreenLocalMax);
	}

	// Value fixture only: this GUID is never registered as an accepted gameplay token.
	FDYStageResolvedPresentationSnapshot Snapshot(const FTransform& Screen = FTransform::Identity,
		const FQuat& StaffRotation = FQuat::Identity, double LocalCenterZ = 15.0)
	{
		FDYStageResolvedPresentationSnapshot S;
		S.bHasSnapshot = true;
		S.Token = FGuid(1, 2, 3, 4);
		S.PuzzleId = TEXT("StaffDropMathFixture");
		S.Light.bIsValid = S.Puppet.bIsValid = true;
		auto& P = S.Projection;
		P.bHasGeometry = true;
		P.EmitterWorld = Screen.TransformPosition(FVector(-300, 0, 0));
		P.ScreenTransform = Screen;
		P.ScreenLocalMin = FVector(-50);
		P.ScreenLocalMax = FVector(50);
		P.Staff.bIsValid = true;
		P.Staff.LocalMin = FVector(-2, -3, -5);
		P.Staff.LocalMax = FVector(2, 3, 5);
		P.Staff.ComponentTransform = FTransform(Screen.GetRotation() * StaffRotation,
			Screen.TransformPosition(FVector(-175, 10, LocalCenterZ)), FVector(1, .75, 1.3));
		P.Staff.EndAWorld = P.Staff.ComponentTransform.TransformPosition(FVector(0, 0, -5));
		P.Staff.EndBWorld = P.Staff.ComponentTransform.TransformPosition(FVector(0, 0, 5));
		P.EndA = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, P.Staff.EndAWorld,
			Screen, P.ScreenLocalMin, P.ScreenLocalMax);
		P.EndB = UDYStaffProjectionLibrary::ProjectPointToScreen(P.EmitterWorld, P.Staff.EndBWorld,
			Screen, P.ScreenLocalMin, P.ScreenLocalMax);
		S.GroundLine = UDYStaffContactLibrary::CaptureNarrativeGroundLine(P,
			Screen.TransformPosition(FVector(-50, -30, -35)));
		return S;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffDropCauseTest,
	"DengYingShanHai.P03.StaffDrop.CausalEndpoints", DYStaffDropTests::Flags)
bool FDYStaffDropCauseTest::RunTest(const FString& Parameters)
{
	const auto S = DYStaffDropTests::Snapshot();
	const auto Start = UDYStaffDropLibrary::SampleStaffDrop(S, 0);
	const auto Half = UDYStaffDropLibrary::SampleStaffDrop(S, .5);
	const auto End = UDYStaffDropLibrary::SampleStaffDrop(S, 1);
	if (!TestEqual(TEXT("End valid"), End.Status, EDYStaffDropStatus::Valid)) { return false; }
	TestEqual(TEXT("Start valid"), Start.Status, EDYStaffDropStatus::Valid);
	TestEqual(TEXT("Half valid"), Half.Status, EDYStaffDropStatus::Valid);
	TestTrue(TEXT("Start uses exact captured Staff pose"), Start.StaffWorldTransform.Equals(S.Projection.Staff.ComponentTransform, 0));
	TestTrue(TEXT("Half translation is half full displacement"),
		(Half.StaffWorldTransform.GetTranslation() - Start.StaffWorldTransform.GetTranslation()).Equals(End.FullTranslationWorld * .5, UE_DOUBLE_SMALL_NUMBER));
	TestTrue(TEXT("Keep receiver-local X/Y of actual A"), FMath::IsNearlyEqual(End.Projection.EndA.ScreenLocalPosition.X, S.Projection.EndA.ScreenLocalPosition.X, UE_DOUBLE_SMALL_NUMBER)
		&& FMath::IsNearlyEqual(End.Projection.EndA.ScreenLocalPosition.Y, S.Projection.EndA.ScreenLocalPosition.Y, UE_DOUBLE_SMALL_NUMBER));
	TestFalse(TEXT("Do not snap horizontal point to ground anchor"), End.Projection.EndA.WorldPosition.Equals(S.GroundLine.WorldAnchor));
	TestTrue(TEXT("Actual A on original line at endpoint"), UDYStaffContactLibrary::IsStaffAOnNarrativeGround(End.Projection, S.GroundLine));
	TestFalse(TEXT("No early contact"), UDYStaffContactLibrary::IsStaffAOnNarrativeGround(Half.Projection, S.GroundLine));
	TestFalse(TEXT("Physical Staff tip is not placed on curtain"), End.Projection.Staff.EndAWorld.Equals(End.ShadowTargetWorld));
	TestTrue(TEXT("Preserve source ray depth"), FMath::IsNearlyEqual(End.Projection.EndA.RayParameter, S.Projection.EndA.RayParameter, UE_DOUBLE_SMALL_NUMBER));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffDropPoseTest,
	"DengYingShanHai.P03.StaffDrop.RotationScaleAndInputPurity", DYStaffDropTests::Flags)
bool FDYStaffDropPoseTest::RunTest(const FString& Parameters)
{
	const auto S = DYStaffDropTests::Snapshot(FTransform::Identity, FRotator(8, 16, 12).Quaternion());
	const FTransform Original = S.Projection.Staff.ComponentTransform;
	for (const double Alpha : {0.0, .1, .5, .9, 1.0})
	{
		const auto R = UDYStaffDropLibrary::SampleStaffDrop(S, Alpha);
		TestEqual(TEXT("Sample valid"), R.Status, EDYStaffDropStatus::Valid);
		TestTrue(TEXT("Exact rotation unchanged"), R.StaffWorldTransform.GetRotation() == Original.GetRotation());
		TestTrue(TEXT("Exact scale unchanged"), R.StaffWorldTransform.GetScale3D() == Original.GetScale3D());
		TestTrue(TEXT("Only copy identity, never issue a GUID"), R.Token == S.Token);
		TestEqual(TEXT("Puzzle ID copy"), R.PuzzleId, S.PuzzleId);
	}
	TestTrue(TEXT("Input transform unchanged"), S.Projection.Staff.ComponentTransform.Equals(Original, 0));
	const auto First = UDYStaffDropLibrary::SampleStaffDrop(S, .3);
	const auto Again = UDYStaffDropLibrary::SampleStaffDrop(S, .3);
	TestTrue(TEXT("Deterministic, no session state"), First.StaffWorldTransform.Equals(Again.StaffWorldTransform, 0));
	for (const FVector Scale : {FVector(-1, .75, 1.3), FVector(1, -.75, 1.3), FVector(1, .75, -1.3)})
	{
		auto OffsetBounds = DYStaffDropTests::Snapshot();
		OffsetBounds.Projection.Staff.LocalMin = FVector(-1, 1, -4);
		OffsetBounds.Projection.Staff.LocalMax = FVector(5, 7, 8);
		OffsetBounds.Projection.Staff.ComponentTransform.SetScale3D(Scale);
		DYStaffDropTests::RefreshStaff(OffsetBounds);
		const auto R = UDYStaffDropLibrary::SampleStaffDrop(OffsetBounds, 1);
		if (!TestEqual(TEXT("Offset bounds and mirrored staff valid"), R.Status, EDYStaffDropStatus::Valid)) { continue; }
		TestTrue(TEXT("Signed staff scale unchanged"), R.StaffWorldTransform.GetScale3D() == Scale);
		TestTrue(TEXT("Output A exactly rebuilt from transformed actual bounds"),
			R.Projection.Staff.EndAWorld.Equals(R.StaffWorldTransform.TransformPosition(FVector(2, 4, -4)), 0));
		TestTrue(TEXT("Offset-bounds actual A reaches line"), UDYStaffContactLibrary::IsStaffAOnNarrativeGround(R.Projection, OffsetBounds.GroundLine));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffDropFrameTest,
	"DengYingShanHai.P03.StaffDrop.RotatedScaledReceiver", DYStaffDropTests::Flags)
bool FDYStaffDropFrameTest::RunTest(const FString& Parameters)
{
	for (const FVector Scale : {FVector(.5, 9, 8), FVector(.5, -9, 8), FVector(-.5, 9, 8), FVector(.5, 9, -8)})
	{
		const FTransform Screen(FRotator(0, 31, 17), FVector(900, -40, 100), Scale);
		const auto S = DYStaffDropTests::Snapshot(Screen, FRotator(4, 9, 3).Quaternion());
		const auto R = UDYStaffDropLibrary::SampleStaffDrop(S, 1);
		if (!TestEqual(TEXT("Receiver frame valid"), R.Status, EDYStaffDropStatus::Valid)) { continue; }
		TestTrue(TEXT("Contact follows receiver-local line"), UDYStaffContactLibrary::IsStaffAOnNarrativeGround(R.Projection, S.GroundLine));
		TestTrue(TEXT("Receiver Y retained"), FMath::IsNearlyEqual(R.Projection.EndA.ScreenLocalPosition.Y, S.Projection.EndA.ScreenLocalPosition.Y, UE_DOUBLE_SMALL_NUMBER));
		TestTrue(TEXT("No world-Z assumption"), !FMath::IsNearlyZero(R.FullTranslationWorld.Y, UE_DOUBLE_SMALL_NUMBER));
	}
	for (const double Offset : {100000.0, 1000000.0, 1000000000.0})
	{
		const auto S = DYStaffDropTests::Snapshot(FTransform(FRotator(0, 31, 17), FVector(Offset), FVector(.5, 9, 8)));
		const auto R = UDYStaffDropLibrary::SampleStaffDrop(S, 1);
		if (R.Status == EDYStaffDropStatus::Valid)
		{
			TestTrue(TEXT("Large-world valid endpoint agrees exactly with mesh transform"),
				R.Projection.Staff.EndAWorld.Equals(R.StaffWorldTransform.TransformPosition(FVector(0, 0, -5)), 0));
			TestTrue(TEXT("Large-world valid endpoint round-trips onto line"), UDYStaffContactLibrary::IsStaffAOnNarrativeGround(R.Projection, S.GroundLine));
			TestTrue(TEXT("Large-world horizontal shadow position retained"),
				FMath::IsNearlyEqual(R.Projection.EndA.ScreenLocalPosition.Y, S.Projection.EndA.ScreenLocalPosition.Y, UE_DOUBLE_SMALL_NUMBER));
		}
		else
		{
			TestEqual(TEXT("Unrepresentable endpoint fails closed"), R.Status, EDYStaffDropStatus::InvalidGeometry);
			TestFalse(TEXT("Failed endpoint has no token"), R.Token.IsValid());
			TestFalse(TEXT("Failed endpoint has no valid geometry"), R.Projection.bHasGeometry);
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffDropProgressTest,
	"DengYingShanHai.P03.StaffDrop.ProgressBoundary", DYStaffDropTests::Flags)
bool FDYStaffDropProgressTest::RunTest(const FString& Parameters)
{
	const auto S = DYStaffDropTests::Snapshot();
	const auto Below = UDYStaffDropLibrary::SampleStaffDrop(S, -2);
	const auto Above = UDYStaffDropLibrary::SampleStaffDrop(S, 2);
	TestEqual(TEXT("Finite below zero remains valid"), Below.Status, EDYStaffDropStatus::Valid);
	TestEqual(TEXT("Finite above one remains valid"), Above.Status, EDYStaffDropStatus::Valid);
	TestEqual(TEXT("Finite below zero clamps"), Below.NormalizedProgress, 0.0);
	TestEqual(TEXT("Finite above one clamps"), Above.NormalizedProgress, 1.0);
	TestTrue(TEXT("Clamped start is original transform"), Below.StaffWorldTransform.Equals(S.Projection.Staff.ComponentTransform, 0));
	TestTrue(TEXT("Clamped end equals endpoint sample"), Above.StaffWorldTransform.Equals(UDYStaffDropLibrary::SampleStaffDrop(S, 1).StaffWorldTransform, 0));
	TestEqual(TEXT("NaN rejected"), UDYStaffDropLibrary::SampleStaffDrop(S, std::numeric_limits<double>::quiet_NaN()).Status, EDYStaffDropStatus::InvalidProgress);
	TestEqual(TEXT("Infinity rejected"), UDYStaffDropLibrary::SampleStaffDrop(S, std::numeric_limits<double>::infinity()).Status, EDYStaffDropStatus::InvalidProgress);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffDropSnapshotTest,
	"DengYingShanHai.P03.StaffDrop.InvalidSnapshot", DYStaffDropTests::Flags)
bool FDYStaffDropSnapshotTest::RunTest(const FString& Parameters)
{
	auto S = DYStaffDropTests::Snapshot(); S.bHasSnapshot = false;
	TestEqual(TEXT("Missing resolved snapshot"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidSnapshot);
	S = DYStaffDropTests::Snapshot(); S.Token.Invalidate();
	TestEqual(TEXT("Missing correlation identity"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidSnapshot);
	S = DYStaffDropTests::Snapshot(); S.Light.bIsValid = false;
	TestEqual(TEXT("Missing light evidence"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidSnapshot);
	S = DYStaffDropTests::Snapshot(); S.Puppet.bIsValid = false;
	TestEqual(TEXT("Missing puppet evidence"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidSnapshot);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffDropGeometryTest,
	"DengYingShanHai.P03.StaffDrop.CachedGeometryNotTrusted", DYStaffDropTests::Flags)
bool FDYStaffDropGeometryTest::RunTest(const FString& Parameters)
{
	auto S = DYStaffDropTests::Snapshot(); S.Projection.EndA.RayParameter += .1;
	TestEqual(TEXT("Forged ray depth rejected"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidGeometry);
	S = DYStaffDropTests::Snapshot(); S.Projection.Staff.EndAWorld.Z += 1;
	TestEqual(TEXT("Tip/mesh disagreement rejected"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidGeometry);
	S = DYStaffDropTests::Snapshot(); S.Projection.ScreenTransform.SetScale3D(FVector(0, 1, 1));
	TestEqual(TEXT("Degenerate screen rejected"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidGeometry);
	S = DYStaffDropTests::Snapshot(); S.Projection.EmitterWorld.X = std::numeric_limits<double>::infinity();
	TestEqual(TEXT("Nonfinite source rejected"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidGeometry);
	S = DYStaffDropTests::Snapshot(); S.Projection.Staff.LocalMax.Z = S.Projection.Staff.LocalMin.Z;
	const auto Failed = UDYStaffDropLibrary::SampleStaffDrop(S, .5);
	TestEqual(TEXT("Zero-length Staff rejected"), Failed.Status, EDYStaffDropStatus::InvalidGeometry);
	TestFalse(TEXT("Failed sample does not export a token"), Failed.Token.IsValid());
	TestFalse(TEXT("Failed sample does not export geometry"), Failed.Projection.bHasGeometry);
	TestTrue(TEXT("Failed sample has no displacement"), Failed.FullTranslationWorld.IsZero());
	// A on-screen while B is above the receiver remains legitimate, as in the existing player adapter.
	S = DYStaffDropTests::Snapshot(FTransform::Identity, FQuat::Identity, 25);
	TestEqual(TEXT("Fixture B outside receiver"), S.Projection.EndB.Status, EDYStaffProjectionStatus::OutsideScreen);
	TestEqual(TEXT("B is not a second contact requirement"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::Valid);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffDropGroundTest,
	"DengYingShanHai.P03.StaffDrop.GroundAndInitialHeight", DYStaffDropTests::Flags)
bool FDYStaffDropGroundTest::RunTest(const FString& Parameters)
{
	auto S = DYStaffDropTests::Snapshot(); S.GroundLine.ScreenLocalZ += 1;
	TestEqual(TEXT("Ground cache disagreement rejected"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidGroundLine);
	S = DYStaffDropTests::Snapshot(); S.GroundLine.WorldAnchor.X += 1;
	TestEqual(TEXT("Ground off receiver rejected"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::InvalidGroundLine);
	S = DYStaffDropTests::Snapshot(); S.GroundLine = UDYStaffContactLibrary::CaptureNarrativeGroundLine(S.Projection, S.Projection.EndA.WorldPosition);
	TestEqual(TEXT("At-ground start is not a new drop"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::NotAboveGround);
	S = DYStaffDropTests::Snapshot(); FVector Above = S.Projection.EndA.ScreenLocalPosition; Above.Z += 1;
	S.GroundLine = UDYStaffContactLibrary::CaptureNarrativeGroundLine(S.Projection, S.Projection.ScreenTransform.TransformPosition(Above));
	TestEqual(TEXT("Below-ground start rejected"), UDYStaffDropLibrary::SampleStaffDrop(S, .5).Status, EDYStaffDropStatus::NotAboveGround);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffDropReflectionTest,
	"DengYingShanHai.P03.StaffDrop.RuntimeBlueprintContract", DYStaffDropTests::Flags)
bool FDYStaffDropReflectionTest::RunTest(const FString& Parameters)
{
	const UFunction* Fn = UDYStaffDropLibrary::StaticClass()->FindFunctionByName(TEXT("SampleStaffDrop"));
	if (!TestNotNull(TEXT("Reflected sample function exists"), Fn)) { return false; }
	TestTrue(TEXT("BlueprintPure and static"), Fn->HasAllFunctionFlags(FUNC_BlueprintPure | FUNC_Static));
	TestFalse(TEXT("Not editor-only"), Fn->HasAnyFunctionFlags(FUNC_EditorOnly));
	const FProperty* RotationOutput = FindFProperty<FProperty>(FDYStaffDropSample::StaticStruct(), TEXT("StaffWorldTransform"));
	TestTrue(TEXT("Blueprint readonly value output"), RotationOutput && RotationOutput->HasAllPropertyFlags(CPF_BlueprintVisible | CPF_BlueprintReadOnly));
	const auto R = UDYStaffDropLibrary::SampleStaffDrop(DYStaffDropTests::Snapshot(), 1);
	TestEqual(TEXT("Function can run without a World or Actor fixture"), R.Status, EDYStaffDropStatus::Valid);
	return true;
}

#endif
