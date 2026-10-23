#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "GameFramework/WorldSettings.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Stage/DYStaffProjectionLibrary.h"
#include "Stage/DYStaffProjectionProbe.h"
#include "TimerManager.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include <limits>

namespace DYStaffProjectionTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;
	const FVector Min(-50.0), Max(50.0);
	const FTransform Screen(FRotator::ZeroRotator, FVector(950.0, 0.0, 350.0), FVector(0.5, 9.0, 8.0));

	struct FFixture
	{
		FFixture()
		{
			if (!GEngine) { return; }
			World = UWorld::CreateWorld(EWorldType::Game, false,
				MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYStaffGeometryWorld")), GetTransientPackage());
			StrongWorld.Reset(World);
			if (!World) { return; }
			GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
			Light = World->SpawnActor<ADYLightRigActor>(FVector(-460.0, -20.0, 310.0), FRotator::ZeroRotator);
			Puppet = World->SpawnActor<ADYPuppetActor>(FVector(600.0, -80.0, 210.0), FRotator::ZeroRotator);
			Receiver = World->SpawnActor<AStaticMeshActor>();
			if (Receiver)
			{
				Receiver->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
				Receiver->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
				Receiver->SetActorTransform(Screen);
			}
			Probe = World->SpawnActor<ADYStaffProjectionProbe>();
			if (Probe) { Probe->Light = Light; Probe->Puppet = Puppet; Probe->ScreenActor = Receiver; }
		}
		~FFixture()
		{
			if (World && GEngine) { World->EndPlay(EEndPlayReason::Quit); GEngine->DestroyWorldContext(World); World->DestroyWorld(false); }
			StrongWorld.Reset();
		}
		bool Ready() const { return World && Light && Puppet && Receiver && Probe; }
		void BeginPlay() { World->GetWorldSettings()->NotifyBeginPlay(); }
		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> StrongWorld;
		ADYLightRigActor* Light = nullptr;
		ADYPuppetActor* Puppet = nullptr;
		AStaticMeshActor* Receiver = nullptr;
		ADYStaffProjectionProbe* Probe = nullptr;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYProjectionFaceTest,
	"DengYingShanHai.P03.Geometry.ReceiverFaceAndRay", DYStaffProjectionTests::Flags)
bool FDYProjectionFaceTest::RunTest(const FString& Parameters)
{
	using namespace DYStaffProjectionTests;
	const auto P = UDYStaffProjectionLibrary::ProjectPointToScreen(FVector(0, 0, 350), FVector(500, 100, 350), Screen, Min, Max);
	TestEqual(TEXT("Ray intersects receiver"), P.Status, EDYStaffProjectionStatus::OnScreen);
	TestTrue(TEXT("Near face is X925, not Actor X950"), P.WorldPosition.Equals(FVector(925, 185, 350), 1.e-6));
	TestTrue(TEXT("Ray continues beyond source"), FMath::IsNearlyEqual(P.RayParameter, 1.85, 1.e-9));
	TestTrue(TEXT("UV is explicit +Y/+Z"), P.ScreenUV.Equals(FVector2D(635.0 / 900.0, 0.5), 1.e-9));
	const auto Back = UDYStaffProjectionLibrary::ProjectPointToScreen(FVector(1500, 0, 350), FVector(1200, 0, 350), Screen, Min, Max);
	TestTrue(TEXT("Opposite emitter uses opposite receiver face X975"), Back.WorldPosition.Equals(FVector(975, 0, 350), 1.e-6));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYProjectionTransformTest,
	"DengYingShanHai.P03.Geometry.RotationScaleAndBoundary", DYStaffProjectionTests::Flags)
bool FDYProjectionTransformTest::RunTest(const FString& Parameters)
{
	using namespace DYStaffProjectionTests;
	const FTransform T(FRotator(7, 32, 11), FVector(1000, -123, 405), FVector(0.3, 4, 7));
	const FVector L(-300, 0, 0), S(-175, 25, 25);
	const auto Edge = UDYStaffProjectionLibrary::ProjectPointToScreen(T.TransformPosition(L), T.TransformPosition(S), T, Min, Max);
	TestEqual(TEXT("Inclusive finite rectangle edge accepted"), Edge.Status, EDYStaffProjectionStatus::OnScreen);
	TestTrue(TEXT("Nonuniform scale and rotation preserve correct intersection"), Edge.WorldPosition.Equals(T.TransformPosition(FVector(-50, 50, 50)), 1.e-6));
	const auto Outside = UDYStaffProjectionLibrary::ProjectPointToScreen(T.TransformPosition(L), T.TransformPosition(FVector(-175, 26, 25)), T, Min, Max);
	TestEqual(TEXT("Outside rectangle is not a contact candidate"), Outside.Status, EDYStaffProjectionStatus::OutsideScreen);
	TestTrue(TEXT("Outside position retained for debugging"), Outside.ScreenUV.X > 1.0);
	const auto NearOutside = UDYStaffProjectionLibrary::ProjectPointToScreen(T.TransformPosition(L),
		T.TransformPosition(FVector(-175, 25.0001, 25)), T, Min, Max);
	TestEqual(TEXT("Numerical edge epsilon does not become a gameplay tolerance"), NearOutside.Status, EDYStaffProjectionStatus::OutsideScreen);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYProjectionInvalidTest,
	"DengYingShanHai.P03.Geometry.InvalidInputsFailClosed", DYStaffProjectionTests::Flags)
bool FDYProjectionInvalidTest::RunTest(const FString& Parameters)
{
	using namespace DYStaffProjectionTests;
	auto Project = [&](FVector Light, FVector Source) { return UDYStaffProjectionLibrary::ProjectPointToScreen(Light, Source, Screen, Min, Max); };
	TestEqual(TEXT("Parallel ray rejected"), Project(FVector(0, 0, 350), FVector(0, 20, 350)).Status, EDYStaffProjectionStatus::ParallelRay);
	TestEqual(TEXT("Coincident points rejected"), Project(FVector(0, 0, 350), FVector(0, 0, 350)).Status, EDYStaffProjectionStatus::ParallelRay);
	TestEqual(TEXT("Source behind screen rejected"), Project(FVector(0, 0, 350), FVector(1000, 0, 350)).Status, EDYStaffProjectionStatus::ScreenNotBeyondSource);
	TestEqual(TEXT("Backward ray rejected"), Project(FVector(0, 0, 350), FVector(-100, 0, 350)).Status, EDYStaffProjectionStatus::ScreenNotBeyondSource);
	TestEqual(TEXT("Emitter inside receiver rejected"), Project(FVector(950, 0, 350), FVector(500, 0, 350)).Status, EDYStaffProjectionStatus::InvalidGeometry);
	const double Infinity = std::numeric_limits<double>::infinity();
	TestEqual(TEXT("Infinite emitter rejected"), Project(FVector(Infinity, 0, 0), FVector(500, 0, 350)).Status, EDYStaffProjectionStatus::InvalidGeometry);
	TestEqual(TEXT("NaN source rejected"), Project(FVector(0, 0, 350), FVector(std::numeric_limits<double>::quiet_NaN(), 0, 0)).Status, EDYStaffProjectionStatus::InvalidGeometry);
	const FTransform Degenerate(FRotator::ZeroRotator, FVector::ZeroVector, FVector(0, 1, 1));
	TestEqual(TEXT("Collapsed screen rejected before inverse transform"), UDYStaffProjectionLibrary::ProjectPointToScreen(FVector(-100, 0, 0), FVector(-75, 0, 0), Degenerate, Min, Max).Status, EDYStaffProjectionStatus::InvalidGeometry);
	TestFalse(TEXT("Null references do not invent geometry"), UDYStaffProjectionLibrary::CaptureStaffProjection(nullptr, nullptr, nullptr).bHasGeometry);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffActualComponentsTest,
	"DengYingShanHai.P03.Geometry.ActualComponentsAndCopy", DYStaffProjectionTests::Flags)
bool FDYStaffActualComponentsTest::RunTest(const FString& Parameters)
{
	DYStaffProjectionTests::FFixture F;
	if (!TestTrue(TEXT("Actual fixture exists"), F.Ready())) { return false; }
	F.BeginPlay();
	const auto Original = F.Puppet->GetStaffGeometrySnapshot();
	TestTrue(TEXT("Actual Staff has geometry"), Original.bIsValid);
	const auto Capture = UDYStaffProjectionLibrary::CaptureStaffProjection(F.Light, F.Puppet, F.Receiver->GetStaticMeshComponent());
	TestTrue(TEXT("Emitter is actual SpotLight location"), Capture.EmitterWorld.Equals(F.Light->GetKeyLightComponent()->GetComponentLocation()));
	TestFalse(TEXT("Emitter is not actor pivot"), Capture.EmitterWorld.Equals(F.Light->GetActorLocation()));
	F.Puppet->SetActorTransform(FTransform(FRotator(10, 37, 8), FVector(605, -32, 226), FVector(1.2, 0.7, 1.5)));
	const auto Changed = F.Puppet->GetStaffGeometrySnapshot();
	const FVector LocalA((Changed.LocalMin.X + Changed.LocalMax.X) * .5, (Changed.LocalMin.Y + Changed.LocalMax.Y) * .5, Changed.LocalMin.Z);
	TestTrue(TEXT("Endpoint uses full component transform and actual mesh bounds"), Changed.EndAWorld.Equals(Changed.ComponentTransform.TransformPosition(LocalA)));
	TestFalse(TEXT("Parent rotation and scale change actual endpoint"), Original.EndAWorld.Equals(Changed.EndAWorld));
	auto Copy = Changed;
	Copy.EndAWorld = FVector(999);
	TestTrue(TEXT("Getter returns independent value evidence"), F.Puppet->GetStaffGeometrySnapshot().EndAWorld.Equals(Changed.EndAWorld));
	for (UStaticMeshComponent* Mesh : TInlineComponentArray<UStaticMeshComponent*>(F.Puppet))
	{
		if (Mesh->GetFName() == TEXT("Staff")) { Mesh->SetStaticMesh(nullptr); }
	}
	TestFalse(TEXT("Missing Staff mesh rejected"), F.Puppet->GetStaffGeometrySnapshot().bIsValid);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYProjectionProbeEventTest,
	"DengYingShanHai.P03.Geometry.EventOrderingAndLifecycle", DYStaffProjectionTests::Flags)
bool FDYProjectionProbeEventTest::RunTest(const FString& Parameters)
{
	DYStaffProjectionTests::FFixture F;
	if (!TestTrue(TEXT("Fixture exists"), F.Ready())) { return false; }
	// Register observer before puppet pose listener to exercise the dangerous order.
	for (UTextRenderComponent* Text : TInlineComponentArray<UTextRenderComponent*>(F.Probe))
	{
		Text->SetVisibility(true); // Simulate the Editor-saved visible debug state.
	}
	F.Probe->DispatchBeginPlay();
	for (UTextRenderComponent* Text : TInlineComponentArray<UTextRenderComponent*>(F.Probe))
	{
		TestFalse(TEXT("BeginPlay clears persisted visible debug state before any refresh"), Text->IsVisible());
	}
	F.BeginPlay();
	F.Probe->RefreshProjection();
	const auto Before = F.Probe->GetLastCapture();
	F.Puppet->GetPuppetControlComponent()->SetNormalizedValue(1.0);
	F.Light->GetLightControlComponent()->SetNormalizedValue(1.0);
	TestTrue(TEXT("Event does not prematurely capture old pose"), F.Probe->GetLastCapture().Staff.EndAWorld.Equals(Before.Staff.EndAWorld));
	F.World->GetTimerManager().Tick(0.016f);
	const auto After = F.Probe->GetLastCapture();
	TestTrue(TEXT("Coalesced callback uses final actual Staff pose"), After.Staff.EndAWorld.Equals(F.Puppet->GetStaffGeometrySnapshot().EndAWorld));
	TestTrue(TEXT("Coalesced callback uses final actual emitter"), After.EmitterWorld.Equals(F.Light->GetKeyLightComponent()->GetComponentLocation()));
	TestFalse(TEXT("Actual Staff endpoint moved"), Before.Staff.EndAWorld.Equals(After.Staff.EndAWorld));
	TestFalse(TEXT("Probe never has Tick"), F.Probe->PrimaryActorTick.bCanEverTick);
	F.Probe->Destroy();
	TestFalse(TEXT("EndPlay clears evidence and pending work"), F.Probe->GetLastCapture().bHasGeometry);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYProjectionActualSweepTest,
	"DengYingShanHai.P03.Geometry.ActualControlSweep", DYStaffProjectionTests::Flags)
bool FDYProjectionActualSweepTest::RunTest(const FString& Parameters)
{
	DYStaffProjectionTests::FFixture F;
	if (!TestTrue(TEXT("Fixture exists"), F.Ready())) { return false; }
	F.BeginPlay();
	FVector PreviousA = FVector::ZeroVector;
	for (double Value : { 0.0, 0.5, 1.0 })
	{
		F.Puppet->GetPuppetControlComponent()->SetNormalizedValue(Value);
		F.Light->GetLightControlComponent()->SetNormalizedValue(Value);
		const auto Capture = UDYStaffProjectionLibrary::CaptureStaffProjection(F.Light, F.Puppet, F.Receiver->GetStaticMeshComponent());
		TestTrue(TEXT("Actual sweep has geometry"), Capture.bHasGeometry);
		TestTrue(TEXT("Actual endpoint changes across control range"), !PreviousA.Equals(Capture.Staff.EndAWorld));
		PreviousA = Capture.Staff.EndAWorld;
		AddInfo(FString::Printf(TEXT("GEOMETRY_SAMPLE axis=%.2f pose=%s emitter=%s staffA=%s projectionA=%s Astatus=%d projectionB=%s Bstatus=%d"),
			Value, *F.Puppet->GetPoseId().ToString(), *Capture.EmitterWorld.ToString(), *Capture.Staff.EndAWorld.ToString(),
			*Capture.EndA.WorldPosition.ToString(), static_cast<int32>(Capture.EndA.Status),
			*Capture.EndB.WorldPosition.ToString(), static_cast<int32>(Capture.EndB.Status)));
	}
	return true;
}

#endif
