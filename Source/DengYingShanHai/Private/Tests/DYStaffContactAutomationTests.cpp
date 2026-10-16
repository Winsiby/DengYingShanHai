#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "GameFramework/WorldSettings.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Puzzles/DYPuzzleDefinition.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Stage/DYStaffContactLibrary.h"
#include "Stage/DYStagePresentation.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include <limits>

/** Configures references only. Success must come from actual Director/Evaluator events. */
struct FDYStaffContactTestSeam
{
	static void Configure(ADYStagePresentation& P, ADYPuzzleDirector* Director,
		ADYStageEnvironment* Environment, AStaticMeshActor* Screen, AActor* Ground, bool bEnabled = true)
	{
		P.PuzzleDirector = Director;
		P.StageEnvironment = Environment;
		P.StaffProjectionScreen = Screen;
		P.NarrativeGroundLine = Ground;
		P.bEnableStaffContactPresentation = bEnabled;
	}
};

namespace DYStaffContactTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;

	struct FFixture
	{
		explicit FFixture(bool bEnabled = true, bool bBeginPresentation = true)
		{
			if (!GEngine) { return; }
			World = UWorld::CreateWorld(EWorldType::Game, false,
				MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYStaffContactWorld")), GetTransientPackage());
			StrongWorld.Reset(World);
			if (!World) { return; }
			GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
			Light = World->SpawnActor<ADYLightRigActor>(FVector(-460, -20, 310), FRotator::ZeroRotator);
			Puppet = World->SpawnActor<ADYPuppetActor>(FVector(600, -80, 210), FRotator::ZeroRotator);
			Director = World->SpawnActor<ADYPuzzleDirector>();
			Environment = World->SpawnActor<ADYStageEnvironment>();
			Presentation = World->SpawnActor<ADYStagePresentation>();
			Receiver = World->SpawnActor<AStaticMeshActor>();
			Ground = World->SpawnActor<AStaticMeshActor>();
			if (!Light || !Puppet || !Director || !Environment || !Presentation || !Receiver || !Ground) { return; }
			Receiver->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
			Receiver->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
			Receiver->SetActorTransform(FTransform(FRotator::ZeroRotator, FVector(950, 0, 350), FVector(.5, 9, 8)));
			Ground->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
			Definition = NewObject<UDYPuzzleDefinition>(Director);
			Definition->PuzzleId = TEXT("StaffContactContractTest");
			Definition->LightPosition.bEnabled = true;
			Definition->LightPosition.Target = .72;
			Definition->LightPosition.EnterTolerance = .05;
			Definition->LightPosition.ExitTolerance = .09;
			Definition->PuppetPosition.bEnabled = true;
			Definition->PuppetPosition.Target = .80;
			Definition->PuppetPosition.EnterTolerance = .05;
			Definition->PuppetPosition.ExitTolerance = .09;
			Definition->RequiredPuppetPoseId = TEXT("P02_StrideReach");
			// Fixture numbers only; no P03 live Definition or tuning is created.
			Definition->RequiredHoldSeconds = 0;
			FindFProperty<FObjectPropertyBase>(Director->GetClass(), TEXT("LightRig"))->SetObjectPropertyValue_InContainer(Director, Light);
			FindFProperty<FObjectPropertyBase>(Director->GetClass(), TEXT("PuppetActor"))->SetObjectPropertyValue_InContainer(Director, Puppet);
			FindFProperty<FObjectPropertyBase>(Director->GetClass(), TEXT("PuzzleDefinition"))->SetObjectPropertyValue_InContainer(Director, Definition);
			FDYStaffContactTestSeam::Configure(*Presentation, Director, Environment, Receiver, Ground, bEnabled);
			if (bBeginPresentation) { Presentation->DispatchBeginPlay(); }
			Director->StartCurrentPuzzle();
		}

		~FFixture()
		{
			if (World && GEngine) { World->EndPlay(EEndPlayReason::Quit); GEngine->DestroyWorldContext(World); World->DestroyWorld(false); }
			StrongWorld.Reset();
		}
		bool Ready() const { return World && Light && Puppet && Director && Definition && Presentation && Receiver && Ground; }
		FDYStaffProjectionCapture Capture() const
		{
			return UDYStaffProjectionLibrary::CaptureStaffProjection(Light, Puppet, Receiver->GetStaticMeshComponent());
		}
		void Prepare(bool bGroundAtB = false)
		{
			// Explicitly different from answer centres, same as foundation fixture.
			Light->GetLightControlComponent()->SetNormalizedValue(.755);
			Puppet->GetPuppetControlComponent()->SetNormalizedValue(.825);
			const auto C = Capture();
			FVector Line = (bGroundAtB ? C.EndB : C.EndA).ScreenLocalPosition;
			if (!bGroundAtB) { Line.Z -= 5; } // Test-only line below A, not a live authoring choice.
			Ground->SetActorLocation(C.ScreenTransform.TransformPosition(Line));
		}
		void Resolve(bool bGroundAtB = false) { Prepare(bGroundAtB); Director->EvaluatePuzzleNow(); }
		void MoveAIntoContact()
		{
			const auto C = Capture();
			const auto Line = Presentation->GetResolvedStaffPresentationSnapshot().GroundLine;
			FVector ScreenPoint = C.EndA.ScreenLocalPosition;
			ScreenPoint.Z = Line.ScreenLocalZ;
			const FVector NewA = C.EmitterWorld + (C.ScreenTransform.TransformPosition(ScreenPoint) - C.EmitterWorld) / C.EndA.RayParameter;
			for (UStaticMeshComponent* Mesh : TInlineComponentArray<UStaticMeshComponent*>(Puppet))
			{
				if (Mesh->GetFName() == TEXT("Staff")) { Mesh->AddWorldOffset(NewA - C.Staff.EndAWorld); }
			}
		}
		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> StrongWorld;
		ADYLightRigActor* Light = nullptr;
		ADYPuppetActor* Puppet = nullptr;
		ADYPuzzleDirector* Director = nullptr;
		UDYPuzzleDefinition* Definition = nullptr;
		ADYStageEnvironment* Environment = nullptr;
		ADYStagePresentation* Presentation = nullptr;
		AStaticMeshActor* Receiver = nullptr;
		AStaticMeshActor* Ground = nullptr;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffResolvedCaptureTest,
	"DengYingShanHai.P03.Contact.ActualResolveAndCopy", DYStaffContactTests::Flags)
bool FDYStaffResolvedCaptureTest::RunTest(const FString& Parameters)
{
	DYStaffContactTests::FFixture F;
	if (!TestTrue(TEXT("Real world/actors ready"), F.Ready())) { return false; }
	TestFalse(TEXT("No presentation capture before success"), F.Presentation->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	F.Resolve();
	auto S = F.Presentation->GetResolvedStaffPresentationSnapshot();
	TestTrue(TEXT("Actual success event captured"), S.bHasSnapshot && S.Projection.bHasGeometry && S.GroundLine.bIsValid);
	TestTrue(TEXT("Exact authoritative token"), S.Token == F.Director->GetResolvedPuzzleSnapshot().Token);
	TestEqual(TEXT("Actual light value retained"), S.Light.PrimaryNormalized, .755);
	TestEqual(TEXT("Actual puppet value retained"), S.Puppet.PrimaryNormalized, .825);
	TestTrue(TEXT("Actual private Staff endpoints captured"), S.Projection.Staff.EndAWorld.Equals(F.Puppet->GetStaffGeometrySnapshot().EndAWorld));
	const FVector OriginalA = S.Projection.Staff.EndAWorld;
	S.Projection.Staff.EndAWorld = FVector(999);
	TestTrue(TEXT("Getter is independent value copy"), F.Presentation->GetResolvedStaffPresentationSnapshot().Projection.Staff.EndAWorld.Equals(OriginalA));
	F.MoveAIntoContact();
	F.Presentation->SynchronizeFromDirector();
	TestTrue(TEXT("Late sync does not recapture animated pose"), F.Presentation->GetResolvedStaffPresentationSnapshot().Projection.Staff.EndAWorld.Equals(OriginalA));
	F.Director->OnPuzzleResolved.Broadcast(F.Definition->PuzzleId, F.Director->GetLastEvaluation());
	TestTrue(TEXT("Duplicate resolved event does not overwrite starting evidence"), F.Presentation->GetResolvedStaffPresentationSnapshot().Projection.Staff.EndAWorld.Equals(OriginalA));
	TestFalse(TEXT("Snapshot capture does not automatically create contact"), F.Presentation->GetStaffContactPresentationSnapshot().bHasContact);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffNotContactTest,
	"DengYingShanHai.P03.Contact.OnScreenIsNotContact", DYStaffContactTests::Flags)
bool FDYStaffNotContactTest::RunTest(const FString& Parameters)
{
	DYStaffContactTests::FFixture F, B;
	if (!TestTrue(TEXT("Both fixtures ready"), F.Ready() && B.Ready())) { return false; }
	F.Resolve();
	const auto S = F.Presentation->GetResolvedStaffPresentationSnapshot();
	TestEqual(TEXT("A really is OnScreen"), S.Projection.EndA.Status, EDYStaffProjectionStatus::OnScreen);
	TestFalse(TEXT("OnScreen alone cannot accept a contact"), F.Presentation->TryAcceptStaffContact(S.Token));
	B.Resolve(true);
	const auto BS = B.Presentation->GetResolvedStaffPresentationSnapshot();
	TestTrue(TEXT("Fixture B end is exactly on authored line"), FMath::IsNearlyEqual(BS.Projection.EndB.ScreenLocalPosition.Z, BS.GroundLine.ScreenLocalZ, UE_DOUBLE_SMALL_NUMBER));
	TestFalse(TEXT("B contact is not accepted as A contact"), B.Presentation->TryAcceptStaffContact(BS.Token));
	TestTrue(TEXT("Presentation failure never revokes success"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved && B.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffContactOnceTest,
	"DengYingShanHai.P03.Contact.ActualAExactlyOnce", DYStaffContactTests::Flags)
bool FDYStaffContactOnceTest::RunTest(const FString& Parameters)
{
	DYStaffContactTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	F.Resolve();
	const auto S = F.Presentation->GetResolvedStaffPresentationSnapshot();
	F.MoveAIntoContact();
	int32 Count = 0;
	const FDelegateHandle Handle = F.Presentation->OnStaffContactAccepted().AddLambda([&](const FDYStaffContactPresentationSnapshot& C)
	{
		++Count;
		TestTrue(TEXT("Contact already consumed before observers"), F.Presentation->GetStaffContactPresentationSnapshot().bHasContact);
		TestTrue(TEXT("Actual A contact payload, not initial A"), C.ContactWorldPosition.Equals(F.Capture().EndA.WorldPosition));
		TestFalse(TEXT("Reentrant same-token callback rejected"), F.Presentation->TryAcceptStaffContact(C.Token));
	});
	TestFalse(TEXT("Invalid token rejected"), F.Presentation->TryAcceptStaffContact(FGuid()));
	TestFalse(TEXT("Foreign token rejected"), F.Presentation->TryAcceptStaffContact(FGuid::NewGuid()));
	TestTrue(TEXT("Current actual A contact accepted"), F.Presentation->TryAcceptStaffContact(S.Token));
	TestFalse(TEXT("Duplicate contact rejected"), F.Presentation->TryAcceptStaffContact(S.Token));
	TestEqual(TEXT("Only one contact notification"), Count, 1);
	TestEqual(TEXT("Puzzle truth still resolved exactly once"), F.Director->GetLastEvaluation().ResolveCount, 1);
	auto C = F.Presentation->GetStaffContactPresentationSnapshot();
	const FVector Point = C.ContactWorldPosition;
	C.ContactWorldPosition = FVector(999);
	TestTrue(TEXT("Contact getter returns value copy"), F.Presentation->GetStaffContactPresentationSnapshot().ContactWorldPosition.Equals(Point));
	F.Presentation->OnStaffContactAccepted().Remove(Handle);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffContactTokenTest,
	"DengYingShanHai.P03.Contact.TokenLifetimeAndTeardown", DYStaffContactTests::Flags)
bool FDYStaffContactTokenTest::RunTest(const FString& Parameters)
{
	DYStaffContactTests::FFixture F, Other;
	if (!TestTrue(TEXT("Both fixtures ready"), F.Ready() && Other.Ready())) { return false; }
	F.Resolve(); Other.Resolve();
	const FGuid Old = F.Presentation->GetResolvedStaffPresentationSnapshot().Token;
	F.MoveAIntoContact();
	TestFalse(TEXT("Another Director's actual token is rejected"), F.Presentation->TryAcceptStaffContact(Other.Director->GetResolvedPuzzleSnapshot().Token));
	F.Director->ResetCurrentPuzzle();
	TestFalse(TEXT("Old token rejected after reset"), F.Presentation->TryAcceptStaffContact(Old));
	TestFalse(TEXT("Reset clears capture"), F.Presentation->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	F.Resolve();
	const FGuid New = F.Presentation->GetResolvedStaffPresentationSnapshot().Token;
	TestTrue(TEXT("New activation identity"), New.IsValid() && New != Old);
	F.MoveAIntoContact();
	TestTrue(TEXT("New identity accepts a new contact"), F.Presentation->TryAcceptStaffContact(New));
	F.Presentation->Destroy();
	TestFalse(TEXT("EndPlay clears resolved evidence"), F.Presentation->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	TestFalse(TEXT("EndPlay clears contact evidence"), F.Presentation->GetStaffContactPresentationSnapshot().bHasContact);
	TestFalse(TEXT("EndPlay callback rejected"), F.Presentation->TryAcceptStaffContact(New));
	F.Director->ResetCurrentPuzzle();
	TestFalse(TEXT("Destroy unsubscribed from Director"), F.Presentation->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	Other.MoveAIntoContact();
	const FGuid OtherToken = Other.Director->GetResolvedPuzzleSnapshot().Token;
	Other.Director->Destroy();
	TestFalse(TEXT("Destroyed Director rejects callbacks even with live Presentation"), Other.Presentation->TryAcceptStaffContact(OtherToken));
	TestFalse(TEXT("Destroyed Director hides old evidence"), Other.Presentation->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffMissingGeometryTest,
	"DengYingShanHai.P03.Contact.DefaultOffAndMissingGeometry", DYStaffContactTests::Flags)
bool FDYStaffMissingGeometryTest::RunTest(const FString& Parameters)
{
	DYStaffContactTests::FFixture Off(false), Missing;
	if (!TestTrue(TEXT("Fixtures ready"), Off.Ready() && Missing.Ready())) { return false; }
	TestFalse(TEXT("Class default leaves existing assets opted out"), GetDefault<ADYStagePresentation>()->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	const FBoolProperty* OptIn = FindFProperty<FBoolProperty>(ADYStagePresentation::StaticClass(), TEXT("bEnableStaffContactPresentation"));
	TestTrue(TEXT("Serialized opt-in property actually defaults false"), OptIn && !OptIn->GetPropertyValue_InContainer(GetDefault<ADYStagePresentation>()));
	Off.Resolve();
	TestTrue(TEXT("Default-off path still resolves"), Off.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	TestFalse(TEXT("Default-off path captures nothing"), Off.Presentation->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	TestFalse(TEXT("Default-off path rejects callbacks"), Off.Presentation->TryAcceptStaffContact(Off.Director->GetResolvedPuzzleSnapshot().Token));
	FDYStaffContactTestSeam::Configure(*Missing.Presentation, Missing.Director, Missing.Environment, nullptr, nullptr);
	Missing.Resolve();
	const auto S = Missing.Presentation->GetResolvedStaffPresentationSnapshot();
	TestTrue(TEXT("Missing cosmetic refs do not discard success identity"), S.bHasSnapshot && Missing.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	TestFalse(TEXT("Missing refs do not invent projection"), S.Projection.bHasGeometry);
	TestFalse(TEXT("Missing refs reject contact"), Missing.Presentation->TryAcceptStaffContact(S.Token));
	FDYStaffContactTestSeam::Configure(*Missing.Presentation, Missing.Director, Missing.Environment, Missing.Receiver, Missing.Ground);
	Missing.Presentation->SynchronizeFromDirector();
	TestFalse(TEXT("Late repair cannot invent initial evidence"), Missing.Presentation->GetResolvedStaffPresentationSnapshot().Projection.bHasGeometry);
	Missing.Director->ResetCurrentPuzzle();
	FDYStaffContactTestSeam::Configure(*Missing.Presentation, Missing.Director, Missing.Environment, Off.Receiver, Off.Ground);
	Missing.Resolve();
	const auto CrossWorld = Missing.Presentation->GetResolvedStaffPresentationSnapshot();
	TestTrue(TEXT("Cross-world cosmetic refs do not revoke logic success"), Missing.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	TestFalse(TEXT("Another world's receiver is not accepted"), CrossWorld.Projection.bHasGeometry);
	TestFalse(TEXT("Cross-world contact cannot leak through"), Missing.Presentation->TryAcceptStaffContact(CrossWorld.Token));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffFrozenFrameTest,
	"DengYingShanHai.P03.Contact.FrozenReceiverEmitterAndLine", DYStaffContactTests::Flags)
bool FDYStaffFrozenFrameTest::RunTest(const FString& Parameters)
{
	DYStaffContactTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	F.Resolve(); F.MoveAIntoContact();
	const auto S = F.Presentation->GetResolvedStaffPresentationSnapshot();
	const FTransform LightTransform = F.Light->GetActorTransform();
	F.Light->AddActorWorldOffset(FVector(0, 10, 0));
	TestFalse(TEXT("Changed actual emitter rejects contact"), F.Presentation->TryAcceptStaffContact(S.Token));
	F.Light->SetActorTransform(LightTransform);
	const FTransform ScreenTransform = F.Receiver->GetActorTransform();
	F.Receiver->AddActorWorldOffset(FVector(0, 10, 0));
	TestFalse(TEXT("Changed receiver frame rejects contact"), F.Presentation->TryAcceptStaffContact(S.Token));
	F.Receiver->SetActorTransform(ScreenTransform);
	const FVector GroundPosition = F.Ground->GetActorLocation();
	F.Ground->AddActorWorldOffset(FVector(0, 10, 0));
	TestFalse(TEXT("Changed line rejects contact"), F.Presentation->TryAcceptStaffContact(S.Token));
	F.Ground->SetActorLocation(GroundPosition);
	TestTrue(TEXT("Failed callbacks did not consume token"), F.Presentation->TryAcceptStaffContact(S.Token));
	TestFalse(TEXT("Presentation adds no Tick"), F.Presentation->PrimaryActorTick.bCanEverTick);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffLateAndReentrantTest,
	"DengYingShanHai.P03.Contact.LateSyncAndReentrantReset", DYStaffContactTests::Flags)
bool FDYStaffLateAndReentrantTest::RunTest(const FString& Parameters)
{
	DYStaffContactTests::FFixture Late(true, false), F;
	if (!TestTrue(TEXT("Fixtures ready"), Late.Ready() && F.Ready())) { return false; }
	Late.Resolve();
	Late.Presentation->DispatchBeginPlay();
	Late.Presentation->SynchronizeFromDirector();
	TestFalse(TEXT("Late BeginPlay never synthesizes historical capture"), Late.Presentation->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	TestFalse(TEXT("Late listener cannot replay a contact"), Late.Presentation->TryAcceptStaffContact(Late.Director->GetResolvedPuzzleSnapshot().Token));
	F.Resolve(); F.MoveAIntoContact();
	const FGuid Token = F.Presentation->GetResolvedStaffPresentationSnapshot().Token;
	FGuid Observed;
	const FDelegateHandle Handle = F.Presentation->OnStaffContactAccepted().AddLambda([&](const FDYStaffContactPresentationSnapshot& C)
	{
		F.Director->ResetCurrentPuzzle();
		Observed = C.Token; // Payload must be a stable copy, not the now-reset member.
	});
	TestTrue(TEXT("Contact accepted before listener reset"), F.Presentation->TryAcceptStaffContact(Token));
	TestTrue(TEXT("Payload copy survives reentrant reset"), Observed == Token);
	TestFalse(TEXT("Outer callback cannot resurrect cleared capture"), F.Presentation->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	TestFalse(TEXT("Outer callback cannot resurrect cleared contact"), F.Presentation->GetStaffContactPresentationSnapshot().bHasContact);
	TestFalse(TEXT("Reset invalidates callback immediately"), F.Presentation->TryAcceptStaffContact(Token));
	F.Presentation->OnStaffContactAccepted().Remove(Handle);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYStaffGroundMathTest,
	"DengYingShanHai.P03.Contact.TransformedGroundAndInvalidData", DYStaffContactTests::Flags)
bool FDYStaffGroundMathTest::RunTest(const FString& Parameters)
{
	FDYStaffProjectionCapture C;
	C.bHasGeometry = true;
	C.Staff.bIsValid = true;
	C.ScreenTransform = FTransform(FRotator(7, 32, 11), FVector(1000, -123, 405), FVector(.3, 4, 7));
	C.ScreenLocalMin = FVector(-50);
	C.ScreenLocalMax = FVector(50);
	C.EmitterWorld = C.ScreenTransform.TransformPosition(FVector(-300, 0, 0));
	C.EndA = UDYStaffProjectionLibrary::ProjectPointToScreen(C.EmitterWorld,
		C.ScreenTransform.TransformPosition(FVector(-175, 10, 5)), C.ScreenTransform, C.ScreenLocalMin, C.ScreenLocalMax);
	const FVector Anchor = C.ScreenTransform.TransformPosition(FVector(-50, 0, 10));
	const auto Line = UDYStaffContactLibrary::CaptureNarrativeGroundLine(C, Anchor);
	TestTrue(TEXT("Rotated nonuniform screen line is valid"), Line.bIsValid);
	TestTrue(TEXT("Actual A on local +Z line accepted"), UDYStaffContactLibrary::IsStaffAOnNarrativeGround(C, Line));
	TestFalse(TEXT("Centre-plane anchor rejected; must be actual receiver face"), UDYStaffContactLibrary::CaptureNarrativeGroundLine(C, C.ScreenTransform.TransformPosition(FVector(0, 0, 10))).bIsValid);
	TestFalse(TEXT("Outside line rejected"), UDYStaffContactLibrary::CaptureNarrativeGroundLine(C, C.ScreenTransform.TransformPosition(FVector(-50, 0, 51))).bIsValid);
	TestTrue(TEXT("Exact receiver edge anchor accepted"), UDYStaffContactLibrary::CaptureNarrativeGroundLine(C, C.ScreenTransform.TransformPosition(FVector(-50, 50, 50))).bIsValid);
	auto Near = Line;
	Near.WorldAnchor = C.ScreenTransform.TransformPosition(FVector(-50, 0, 10.0001));
	Near.ScreenLocalZ = 10.0001;
	TestFalse(TEXT("Numerical epsilon is not a gameplay contact band"), UDYStaffContactLibrary::IsStaffAOnNarrativeGround(C, Near));
	const double NaN = std::numeric_limits<double>::quiet_NaN();
	TestFalse(TEXT("NaN anchor rejected"), UDYStaffContactLibrary::CaptureNarrativeGroundLine(C, FVector(NaN, 0, 0)).bIsValid);
	Near = Line; Near.ScreenLocalZ = NaN;
	TestFalse(TEXT("NaN line rejected"), UDYStaffContactLibrary::IsStaffAOnNarrativeGround(C, Near));
	C.EndA.Status = EDYStaffProjectionStatus::OutsideScreen;
	TestFalse(TEXT("Off-screen A rejected"), UDYStaffContactLibrary::IsStaffAOnNarrativeGround(C, Line));
	C.ScreenTransform.SetScale3D(FVector(0, 1, 1));
	TestFalse(TEXT("Degenerate transform rejected"), UDYStaffContactLibrary::CaptureNarrativeGroundLine(C, Anchor).bIsValid);
	return true;
}

#endif
