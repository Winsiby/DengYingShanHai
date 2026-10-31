#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Components/StaticMeshComponent.h"
#include "Engine/BlueprintGeneratedClass.h"
#include "Engine/Engine.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Puzzles/DYPuzzleDefinition.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Stage/DYForestPresentationActor.h"
#include "Stage/DYStagePresentation.h"
#include "Materials/MaterialInterface.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include <limits>

#if WITH_EDITOR
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphNode.h"
#include "EdGraph/EdGraphPin.h"
#include "Engine/Blueprint.h"
#endif

namespace DYForestPresentationTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter;
	const TCHAR* const ForestAssetClassPath = TEXT("/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev.BP_DYForestPresentation_Dev_C");
	template<class T> void ObjectProperty(UObject* Object, const TCHAR* Name, T* Value)
	{
		FindFProperty<FObjectPropertyBase>(Object->GetClass(), Name)->SetObjectPropertyValue_InContainer(Object, Value);
	}
	void ConfigureMesh(ADYForestPresentationActor* Actor)
	{
		ObjectProperty(Actor, TEXT("BranchMesh"), LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
		FDYForestBranchDefinition Root;
		Root.EndScreenOffset = FVector2D(0, 2);
		Root.DiameterWorld = 1;
		Root.GrowthEnd = .5;
		FDYForestBranchDefinition Child;
		Child.ParentIndex = 0;
		Child.StartScreenOffset = Root.EndScreenOffset;
		Child.EndScreenOffset = FVector2D(2, 4);
		Child.DiameterWorld = .7;
		Child.GrowthBegin = .5;
		const FArrayProperty* Property = FindFProperty<FArrayProperty>(Actor->GetClass(), TEXT("BranchLayout"));
		*Property->ContainerPtrToValuePtr<TArray<FDYForestBranchDefinition>>(Actor) = {Root, Child};
	}

	/** Only reference/authoring setup; all tokens/contact are actual gameplay events. */
	struct FFixture
	{
		explicit FFixture(bool bBeginPresentation = true, bool bEnabled = true, UClass* ForestClass = nullptr)
		{
			if (!GEngine) { return; }
			World = UWorld::CreateWorld(EWorldType::Game, false,
				MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYForestPresentationWorld")), GetTransientPackage());
			StrongWorld.Reset(World);
			if (!World) { return; }
			GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
			Light = World->SpawnActor<ADYLightRigActor>(FVector(-460, -20, 310), FRotator::ZeroRotator);
			Puppet = World->SpawnActor<ADYPuppetActor>(FVector(600, -80, 210), FRotator::ZeroRotator);
			Director = World->SpawnActor<ADYPuzzleDirector>();
			Environment = World->SpawnActor<ADYStageEnvironment>();
			Presentation = World->SpawnActor<ADYStagePresentation>();
			Forest = ForestClass ? World->SpawnActor<ADYForestPresentationActor>(ForestClass)
				: World->SpawnActor<ADYForestPresentationActor>();
			Receiver = World->SpawnActor<AStaticMeshActor>();
			Ground = World->SpawnActor<AStaticMeshActor>();
			if (!Ready()) { return; }
			Receiver->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
			Receiver->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
			Receiver->SetActorTransform(FTransform(FRotator::ZeroRotator, FVector(950, 0, 350), FVector(.5, 9, 8)));
			Ground->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
			Definition = NewObject<UDYPuzzleDefinition>(Director);
			Definition->PuzzleId = TEXT("ForestPresentationContractTest");
			Definition->LightPosition.bEnabled = true;
			Definition->LightPosition.Target = .72;
			Definition->LightPosition.EnterTolerance = .05;
			Definition->LightPosition.ExitTolerance = .09;
			Definition->PuppetPosition.bEnabled = true;
			Definition->PuppetPosition.Target = .80;
			Definition->PuppetPosition.EnterTolerance = .05;
			Definition->PuppetPosition.ExitTolerance = .09;
			Definition->RequiredPuppetPoseId = TEXT("P02_StrideReach");
			Definition->RequiredHoldSeconds = 0; // Test fixture only; no P03 authoring.
			ObjectProperty(Director, TEXT("LightRig"), Light);
			ObjectProperty(Director, TEXT("PuppetActor"), Puppet);
			ObjectProperty(Director, TEXT("PuzzleDefinition"), Definition);
			ObjectProperty(Presentation, TEXT("PuzzleDirector"), Director);
			ObjectProperty(Presentation, TEXT("StageEnvironment"), Environment);
			ObjectProperty(Presentation, TEXT("StaffProjectionScreen"), Receiver);
			ObjectProperty(Presentation, TEXT("NarrativeGroundLine"), Ground);
			ObjectProperty(Presentation, TEXT("ForestPresentationActor"), Forest);
			FindFProperty<FBoolProperty>(Presentation->GetClass(), TEXT("bEnableStaffContactPresentation"))->SetPropertyValue_InContainer(Presentation, bEnabled);
			if (!ForestClass) { ConfigureMesh(Forest); } // Saved Blueprint tests use its authored defaults untouched.
			Forest->DispatchBeginPlay();
			if (bBeginPresentation) { Presentation->DispatchBeginPlay(); }
			Director->DispatchBeginPlay(); // Real EndPlay on Destroy, unlike non-begun test doubles.
		}
		~FFixture()
		{
			if (World && GEngine) { World->EndPlay(EEndPlayReason::Quit); GEngine->DestroyWorldContext(World); World->DestroyWorld(false); }
			StrongWorld.Reset();
		}
		bool Ready() const { return World && Light && Puppet && Director && Environment && Presentation && Forest && Receiver && Ground; }
		FDYStaffProjectionCapture Capture() const
		{
			return UDYStaffProjectionLibrary::CaptureStaffProjection(Light, Puppet, Receiver->GetStaticMeshComponent());
		}
		FGuid Resolve()
		{
			Light->GetLightControlComponent()->SetNormalizedValue(.755);
			Puppet->GetPuppetControlComponent()->SetNormalizedValue(.825);
			auto C = Capture();
			FVector Anchor = C.EndA.ScreenLocalPosition;
			Anchor.Z -= 5;
			Ground->SetActorLocation(C.ScreenTransform.TransformPosition(Anchor));
			Director->EvaluatePuzzleNow();
			return Director->GetResolvedPuzzleSnapshot().Token;
		}
		bool Contact()
		{
			const auto C = Capture();
			const auto S = Presentation->GetResolvedStaffPresentationSnapshot();
			FVector End = C.EndA.ScreenLocalPosition;
			End.Z = S.GroundLine.ScreenLocalZ;
			const FVector NewA = C.EmitterWorld + (C.ScreenTransform.TransformPosition(End) - C.EmitterWorld) / C.EndA.RayParameter;
			for (UStaticMeshComponent* Mesh : TInlineComponentArray<UStaticMeshComponent*>(Puppet))
			{
				if (Mesh->GetFName() == TEXT("Staff")) { Mesh->AddWorldOffset(NewA - C.Staff.EndAWorld); }
			}
			return Presentation->TryAcceptStaffContact(S.Token);
		}
		FGuid Grow(double Progress = 1)
		{
			const FGuid Token = Resolve();
			Contact();
			Presentation->BeginForestPresentation(Token);
			Presentation->SetForestNormalizedGrowth(Token, Progress);
			return Token;
		}
		bool VisibleForest() const
		{
			const auto Components = Forest->GetBranchMeshComponents();
			return Forest->HasForestSession() && Components.Num() == 2
				&& IsValid(Components[0]) && Components[0]->IsVisible() && Components[0]->CastShadow;
		}
		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> StrongWorld;
		ADYLightRigActor* Light = nullptr;
		ADYPuppetActor* Puppet = nullptr;
		ADYPuzzleDirector* Director = nullptr;
		UDYPuzzleDefinition* Definition = nullptr;
		ADYStageEnvironment* Environment = nullptr;
		ADYStagePresentation* Presentation = nullptr;
		ADYForestPresentationActor* Forest = nullptr;
		AStaticMeshActor* Receiver = nullptr;
		AStaticMeshActor* Ground = nullptr;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestAuthorizationTest,
	"DengYingShanHai.P03.ForestPresentation.AuthorizationAndContact", DYForestPresentationTests::Flags)
bool FDYForestAuthorizationTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture F, Off(true, false), Other;
	if (!TestTrue(TEXT("Fixtures ready"), F.Ready() && Off.Ready() && Other.Ready())) { return false; }
	TestFalse(TEXT("Before Resolve rejected"), F.Presentation->BeginForestPresentation(FGuid::NewGuid()));
	const FGuid Token = F.Resolve();
	TestFalse(TEXT("Resolved but not contacted rejected"), F.Presentation->BeginForestPresentation(Token));
	TestTrue(TEXT("Actual A contact accepted"), F.Contact());
	TestFalse(TEXT("Random token rejected"), F.Presentation->BeginForestPresentation(FGuid::NewGuid()));
	TestTrue(TEXT("Current contact starts resource session"), F.Presentation->BeginForestPresentation(Token));
	const auto Components = F.Forest->GetBranchMeshComponents();
	TestEqual(TEXT("Two authored components created"), Components.Num(), 2);
	TestTrue(TEXT("Zero growth stays hidden"), Components.Num() == 2 && !Components[0]->IsVisible() && !Components[0]->CastShadow);
	TestTrue(TEXT("Owner applies progress"), F.Presentation->SetForestNormalizedGrowth(Token, .8));
	const auto Before = F.Forest->GetForestGeometrySample();
	TestFalse(TEXT("Active duplicate Begin rejected"), F.Presentation->BeginForestPresentation(Token));
	TestTrue(TEXT("Duplicate did not recreate component"), Components == F.Forest->GetBranchMeshComponents());
	TestTrue(TEXT("Duplicate did not rewind geometry"), Before.Branches[1].EndWorld.Equals(F.Forest->GetForestGeometrySample().Branches[1].EndWorld));
	TestFalse(TEXT("Foreign update cannot erase current session"), F.Presentation->SetForestNormalizedGrowth(FGuid::NewGuid(), 0));
	TestFalse(TEXT("Foreign clear cannot erase current session"), F.Presentation->ClearForestPresentation(FGuid::NewGuid()));
	TestTrue(TEXT("Foreign rejection left current session alive"), F.Forest->HasForestSession());
	const auto OffToken = Off.Resolve();
	TestFalse(TEXT("Default off blocks resource creation"), Off.Presentation->BeginForestPresentation(OffToken));
	TestTrue(TEXT("Default off preserves puzzle success"), Off.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	const auto OtherToken = Other.Resolve(); Other.Contact();
	DYForestPresentationTests::ObjectProperty(Other.Presentation, TEXT("ForestPresentationActor"), F.Forest);
	TestFalse(TEXT("Cross-world actor rejected"), Other.Presentation->BeginForestPresentation(OtherToken));
	TestTrue(TEXT("Cross-world attempt preserves existing owner"), F.Forest->HasForestSession());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestMeshApplicationTest,
	"DengYingShanHai.P03.ForestPresentation.ActualMeshWorldTransforms", DYForestPresentationTests::Flags)
bool FDYForestMeshApplicationTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	F.Forest->SetActorTransform(FTransform(FRotator(15, 35, 7), FVector(125, 333, -62), FVector(2, 3, 4)));
	const FGuid Token = F.Grow(1e-6);
	TestTrue(TEXT("Tiny emergence creates valid visible axis"), F.Forest->HasForestSession() && F.Forest->GetForestGeometrySample().Branches[0].bVisible);
	TestTrue(TEXT("Full progress applied"), F.Presentation->SetForestNormalizedGrowth(Token, 1));
	const auto Sample = F.Forest->GetForestGeometrySample();
	TestEqual(TEXT("Native sample valid"), Sample.Status, EDYForestGeometryStatus::Valid);
	TestTrue(TEXT("Root is actual A, not screen contact"), Sample.PhysicalRoot.Equals(F.Capture().Staff.EndAWorld, UE_DOUBLE_SMALL_NUMBER));
	const auto Components = F.Forest->GetBranchMeshComponents();
	for (int32 I = 0; I < Components.Num(); ++I)
	{
		const UStaticMeshComponent* C = Components[I];
		FVector Min, Max; C->GetLocalBounds(Min, Max);
		const FVector CenterXY((Min.X + Max.X) * .5, (Min.Y + Max.Y) * .5, 0);
		TestTrue(TEXT("Actual mesh component world transform, no Actor double-transform"), C->GetComponentTransform().Equals(Sample.Branches[I].MeshWorldTransform, UE_DOUBLE_SMALL_NUMBER));
		TestTrue(TEXT("Actual mesh A endpoint matches calculated start"), C->GetComponentTransform().TransformPosition(CenterXY + FVector(0, 0, Min.Z)).Equals(Sample.Branches[I].StartWorld, UE_DOUBLE_SMALL_NUMBER));
		TestTrue(TEXT("Actual mesh B endpoint matches calculated end"), C->GetComponentTransform().TransformPosition(CenterXY + FVector(0, 0, Max.Z)).Equals(Sample.Branches[I].EndWorld, UE_DOUBLE_SMALL_NUMBER));
		TestTrue(TEXT("Movable, collision-free and really casts when visible"), C->Mobility == EComponentMobility::Movable && C->GetCollisionEnabled() == ECollisionEnabled::NoCollision && C->IsVisible() && !C->bHiddenInGame && C->CastShadow);
	}
	TestFalse(TEXT("Actor adds no Tick"), F.Forest->PrimaryActorTick.bCanEverTick);
	TestEqual(TEXT("Puzzle resolves exactly once, no finale authority"), F.Director->GetLastEvaluation().ResolveCount, 1);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestFailClosedTest,
	"DengYingShanHai.P03.ForestPresentation.InvalidSamplesClearAllResources", DYForestPresentationTests::Flags)
bool FDYForestFailClosedTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture F, Tampered;
	if (!TestTrue(TEXT("Fixtures ready"), F.Ready() && Tampered.Ready())) { return false; }
	const FGuid Token = F.Grow();
	if (!TestTrue(TEXT("Visible tree before NaN failure"), F.VisibleForest())) { return false; }
	const auto OldComponents = F.Forest->GetBranchMeshComponents();
	TestFalse(TEXT("NaN progress fails"), F.Presentation->SetForestNormalizedGrowth(Token, std::numeric_limits<double>::quiet_NaN()));
	TestFalse(TEXT("Failed sample clears active session"), F.Forest->HasForestSession());
	TestEqual(TEXT("No partial or previous components retained"), F.Forest->GetBranchMeshComponents().Num(), 0);
	for (const auto* C : OldComponents) { TestTrue(TEXT("Destroyed components cannot leave visible/hidden shadows"), !IsValid(C) || (!C->IsVisible() && !C->CastShadow)); }
	TestTrue(TEXT("Math failure leaves success/contact intact"), F.Director->IsResolvedTokenCurrent(Token) && F.Presentation->GetStaffContactPresentationSnapshot().bHasContact);
	TestTrue(TEXT("Explicit Dev resource rebuild allowed, not gameplay restart"), F.Presentation->BeginForestPresentation(Token));
	TestFalse(TEXT("Inf fails closed too"), F.Presentation->SetForestNormalizedGrowth(Token, std::numeric_limits<double>::infinity()));
	const FGuid T = Tampered.Grow();
	if (!TestTrue(TEXT("Visible tree before mesh tamper"), Tampered.VisibleForest())) { return false; }
	Tampered.Forest->GetBranchMeshComponents()[0]->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
	TestFalse(TEXT("Runtime mesh replacement invalidates frozen resource geometry"), Tampered.Presentation->SetForestNormalizedGrowth(T, .5));
	TestEqual(TEXT("Asset mismatch leaves no resources"), Tampered.Forest->GetBranchMeshComponents().Num(), 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestResetTest,
	"DengYingShanHai.P03.ForestPresentation.ResetAndOldTokenIsolation", DYForestPresentationTests::Flags)
bool FDYForestResetTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	const FGuid Old = F.Grow();
	if (!TestTrue(TEXT("Visible tree before reset"), F.VisibleForest())) { return false; }
	F.Director->ResetCurrentPuzzle();
	TestFalse(TEXT("Reset clears immediately without Tick/progress"), F.Forest->HasForestSession());
	TestEqual(TEXT("Reset releases mesh components"), F.Forest->GetBranchMeshComponents().Num(), 0);
	const FGuid New = F.Grow();
	TestTrue(TEXT("New identity and new session"), New.IsValid() && New != Old && F.Forest->HasForestSession());
	TestFalse(TEXT("Old token cannot clear new session"), F.Presentation->ClearForestPresentation(Old));
	TestFalse(TEXT("Old token cannot update new session"), F.Presentation->SetForestNormalizedGrowth(Old, .1));
	TestTrue(TEXT("New session survives old callbacks"), F.Forest->HasForestSession() && F.Forest->GetForestGeometrySample().ContactToken == New);
	TestTrue(TEXT("Explicit clear succeeds once"), F.Presentation->ClearForestPresentation(New));
	TestFalse(TEXT("Repeated clear is harmless rejection"), F.Presentation->ClearForestPresentation(New));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestMissingReferenceTest,
	"DengYingShanHai.P03.ForestPresentation.InvalidActivationStillClears", DYForestPresentationTests::Flags)
bool FDYForestMissingReferenceTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	const FGuid Old = F.Grow();
	if (!TestTrue(TEXT("Visible forest exists before invalid start"), F.VisibleForest())) { return false; }
	AddExpectedError(TEXT("missing an explicit required reference"), EAutomationExpectedErrorFlags::Contains, 1);
	DYForestPresentationTests::ObjectProperty<UDYPuzzleDefinition>(F.Director, TEXT("PuzzleDefinition"), nullptr);
	F.Director->StartCurrentPuzzle();
	TestFalse(TEXT("Early-return invalid activation clears previous forest"), F.Forest->HasForestSession());
	TestEqual(TEXT("Invalid start retained no visible resources"), F.Forest->GetBranchMeshComponents().Num(), 0);
	TestFalse(TEXT("Invalid start rejects previous callbacks"), F.Presentation->BeginForestPresentation(Old));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestDestroyTest,
	"DengYingShanHai.P03.ForestPresentation.ActorPresentationDirectorTeardown", DYForestPresentationTests::Flags)
bool FDYForestDestroyTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture Actor, Presentation, Director;
	if (!TestTrue(TEXT("Fixtures ready"), Actor.Ready() && Presentation.Ready() && Director.Ready())) { return false; }
	const FGuid A = Actor.Grow();
	Presentation.Grow();
	const FGuid D = Director.Grow();
	if (!TestTrue(TEXT("All three teardown fixtures have real visible trees"), Actor.VisibleForest() && Presentation.VisibleForest() && Director.VisibleForest())) { return false; }
	const auto AComponents = Actor.Forest->GetBranchMeshComponents();
	const auto PComponents = Presentation.Forest->GetBranchMeshComponents();
	const auto DComponents = Director.Forest->GetBranchMeshComponents();
	Actor.Forest->Destroy();
	TestFalse(TEXT("Actor EndPlay releases resources"), Actor.Forest->HasForestSession());
	TestFalse(TEXT("Destroyed resource target update rejected"), Actor.Presentation->SetForestNormalizedGrowth(A, .4));
	Presentation.Presentation->Destroy();
	TestFalse(TEXT("Presentation EndPlay clears owned forest"), Presentation.Forest->HasForestSession());
	Director.Director->Destroy();
	TestFalse(TEXT("Director EndPlay notification clears live forest"), Director.Forest->HasForestSession());
	TestFalse(TEXT("Destroyed Director cannot grant authorization"), Director.Presentation->BeginForestPresentation(D));
	for (const auto& Components : {AComponents, PComponents, DComponents})
	{
		for (const auto* C : Components) { TestTrue(TEXT("Previously visible mesh no longer renders or casts"), !IsValid(C) || (!C->IsVisible() && !C->CastShadow)); }
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestOwnerIsolationTest,
	"DengYingShanHai.P03.ForestPresentation.SharedActorCannotBeHijacked", DYForestPresentationTests::Flags)
bool FDYForestOwnerIsolationTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	ADYStagePresentation* Second = F.World->SpawnActor<ADYStagePresentation>();
	for (const TCHAR* Name : {TEXT("PuzzleDirector"), TEXT("StageEnvironment"), TEXT("StaffProjectionScreen"), TEXT("NarrativeGroundLine"), TEXT("ForestPresentationActor")})
	{
		const auto* Property = FindFProperty<FObjectPropertyBase>(F.Presentation->GetClass(), Name);
		Property->SetObjectPropertyValue_InContainer(Second, Property->GetObjectPropertyValue_InContainer(F.Presentation));
	}
	FindFProperty<FBoolProperty>(Second->GetClass(), TEXT("bEnableStaffContactPresentation"))->SetPropertyValue_InContainer(Second, true);
	Second->DispatchBeginPlay();
	const FGuid T = F.Grow(.8);
	TestTrue(TEXT("Second actual contact accepted, same resolved fact"), Second->TryAcceptStaffContact(T));
	TestFalse(TEXT("Second presentation cannot replace first owner's mesh session"), Second->BeginForestPresentation(T));
	Second->Destroy();
	TestTrue(TEXT("Foreign owner teardown cannot clear first forest"), F.Forest->HasForestSession());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestInvalidationReentryTest,
	"DengYingShanHai.P03.ForestPresentation.InvalidationReentryPreservesNewSession", DYForestPresentationTests::Flags)
bool FDYForestInvalidationReentryTest::RunTest(const FString& Parameters)
{
	// Register listener BEFORE Presentation: old notification reaches it after a new Resolve.
	DYForestPresentationTests::FFixture F(false);
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	FGuid New;
	int32 ActivationCount = 0;
	const FDelegateHandle H = F.Director->OnResolvedSnapshotInvalidated().AddLambda([&](const FGuid& Old)
	{
		TestFalse(TEXT("Fact invalid before listener"), F.Director->IsResolvedTokenCurrent(Old));
		++ActivationCount;
		F.Director->ResetCurrentPuzzle();
		New = F.Grow(.8);
	});
	F.Presentation->DispatchBeginPlay();
	const FGuid Old = F.Grow();
	F.Director->StartCurrentPuzzle();
	TestEqual(TEXT("Exactly one old resolved notification"), ActivationCount, 1);
	TestTrue(TEXT("Listener's new activation not overwritten by outer Start"), New.IsValid() && New != Old && F.Director->IsResolvedTokenCurrent(New));
	TestTrue(TEXT("Delayed old notification did not clear new capture"), F.Presentation->GetResolvedStaffPresentationSnapshot().Token == New);
	TestTrue(TEXT("Delayed old notification did not clear new forest"), F.Forest->HasForestSession() && F.Forest->GetForestGeometrySample().ContactToken == New);
	F.Director->OnResolvedSnapshotInvalidated().Remove(H);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestInvalidationDestroyTest,
	"DengYingShanHai.P03.ForestPresentation.InvalidationDestroyCannotResurrect", DYForestPresentationTests::Flags)
bool FDYForestInvalidationDestroyTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	const FGuid Old = F.Grow();
	if (!TestTrue(TEXT("Visible forest exists before destructive callback"), F.VisibleForest())) { return false; }
	const FDelegateHandle H = F.Director->OnResolvedSnapshotInvalidated().AddLambda([&](const FGuid&)
	{
		F.Director->Destroy();
		F.Director->StartCurrentPuzzle();
		F.Director->ResetCurrentPuzzle();
		F.Director->EvaluatePuzzleNow();
	});
	F.Director->ResetCurrentPuzzle();
	TestFalse(TEXT("Destroyed invalidation listener cannot resurrect facts"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	TestFalse(TEXT("Destroyed Director cannot leave visible session"), F.Forest->HasForestSession());
	TestFalse(TEXT("Old callback remains invalid"), F.Presentation->BeginForestPresentation(Old));
	F.Director->OnResolvedSnapshotInvalidated().Remove(H);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestFrozenContactTest,
	"DengYingShanHai.P03.ForestPresentation.CurrentSceneMustMatchAcceptedContact", DYForestPresentationTests::Flags)
bool FDYForestFrozenContactTest::RunTest(const FString& Parameters)
{
	for (int32 Case = 0; Case < 4; ++Case)
	{
		DYForestPresentationTests::FFixture F;
		if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
		const FGuid T = F.Grow();
		if (!TestTrue(TEXT("Tree really visible before geometry change"), F.VisibleForest())) { return false; }
		if (Case == 0) { F.Light->AddActorWorldOffset(FVector(0, 1, 0)); }
		if (Case == 1) { F.Receiver->AddActorWorldOffset(FVector(0, 1, 0)); }
		if (Case == 2) { F.Ground->AddActorWorldOffset(FVector(0, 1, 0)); }
		if (Case == 3)
		{
			for (UStaticMeshComponent* C : TInlineComponentArray<UStaticMeshComponent*>(F.Puppet))
			{
				if (C->GetFName() == TEXT("Staff")) { C->AddWorldOffset(FVector(0, 1, 0)); }
			}
		}
		TestFalse(TEXT("Changed emitter/receiver/line/Staff rejects update"), F.Presentation->SetForestNormalizedGrowth(T, .5));
		TestFalse(TEXT("Current geometry mismatch clears prior tree"), F.Forest->HasForestSession());
		TestFalse(TEXT("Changed scene cannot rebuild from old contact"), F.Presentation->BeginForestPresentation(T));
		TestEqual(TEXT("No lingering mesh components"), F.Forest->GetBranchMeshComponents().Num(), 0);
		TestTrue(TEXT("Cosmetic failure never revokes success fact"), F.Director->IsResolvedTokenCurrent(T));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestSavedAssetRuntimeTest,
	"DengYingShanHai.P03.ForestAsset.SavedBlueprintDefaultsAndRuntimeGeometry", DYForestPresentationTests::Flags)
bool FDYForestSavedAssetRuntimeTest::RunTest(const FString& Parameters)
{
	using namespace DYForestPresentationTests;
	TStrongObjectPtr<UClass> LoadedClass(LoadClass<ADYForestPresentationActor>(nullptr, ForestAssetClassPath));
	if (!TestNotNull(TEXT("Saved Forest Blueprint class loads from its asset path"), LoadedClass.Get())) { return false; }
	if (!TestNotNull(TEXT("Loaded class is an actual BlueprintGeneratedClass"), Cast<UBlueprintGeneratedClass>(LoadedClass.Get()))) { return false; }
	TestTrue(TEXT("Saved class directly inherits the native cosmetic resource owner"), LoadedClass->GetSuperClass() == ADYForestPresentationActor::StaticClass());
	const ADYForestPresentationActor* Defaults = LoadedClass->GetDefaultObject<ADYForestPresentationActor>();
	if (!TestNotNull(TEXT("Saved Blueprint CDO exists"), Defaults)) { return false; }
	TestTrue(TEXT("Defaults are the loaded Blueprint CDO"), Defaults->HasAnyFlags(RF_ClassDefaultObject) && Defaults->GetClass() == LoadedClass.Get());
	const FObjectPropertyBase* MeshProperty = FindFProperty<FObjectPropertyBase>(LoadedClass.Get(), TEXT("BranchMesh"));
	const FObjectPropertyBase* MaterialProperty = FindFProperty<FObjectPropertyBase>(LoadedClass.Get(), TEXT("BranchMaterial"));
	const FArrayProperty* LayoutProperty = FindFProperty<FArrayProperty>(LoadedClass.Get(), TEXT("BranchLayout"));
	if (!TestNotNull(TEXT("Authored mesh property exists"), MeshProperty)
		|| !TestNotNull(TEXT("Authored material property exists"), MaterialProperty)
		|| !TestNotNull(TEXT("Authored layout property exists"), LayoutProperty)) { return false; }
	const UStaticMesh* Cylinder = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (!TestNotNull(TEXT("Engine Cylinder dependency loads"), Cylinder)) { return false; }
	const UObject* AuthoredMesh = MeshProperty->GetObjectPropertyValue_InContainer(Defaults);
	const UObject* AuthoredMaterial = MaterialProperty->GetObjectPropertyValue_InContainer(Defaults);
	const TArray<FDYForestBranchDefinition> AuthoredLayout = *LayoutProperty->ContainerPtrToValuePtr<TArray<FDYForestBranchDefinition>>(Defaults);
	if (!TestTrue(TEXT("Saved mesh is the actual Engine Cylinder"), AuthoredMesh == Cylinder)
		|| !TestEqual(TEXT("Saved Blueprint contains all fifteen authored branches"), AuthoredLayout.Num(), 15)
		|| !TestTrue(TEXT("Saved authored topology is valid"), UDYForestGeometryLibrary::IsForestLayoutValid(AuthoredLayout))) { return false; }
	TestNull(TEXT("Saved Blueprint keeps the material override unset"), AuthoredMaterial);
	const UMaterialInterface* MeshMaterial = Cylinder->GetMaterial(0);
	if (!TestNotNull(TEXT("Cylinder has a fallback material"), MeshMaterial)) { return false; }
	TestTrue(TEXT("Fallback material is an Engine resource"), MeshMaterial->GetPathName().StartsWith(TEXT("/Engine/")));

	auto CheckDefaults = [&]()
	{
		TestTrue(TEXT("Runtime never changes the saved CDO mesh"), MeshProperty->GetObjectPropertyValue_InContainer(Defaults) == AuthoredMesh);
		TestTrue(TEXT("Runtime never changes the saved CDO material"), MaterialProperty->GetObjectPropertyValue_InContainer(Defaults) == AuthoredMaterial);
		TestTrue(TEXT("Runtime never changes any saved CDO layout field"), LayoutProperty->Identical(&AuthoredLayout, LayoutProperty->ContainerPtrToValuePtr<TArray<FDYForestBranchDefinition>>(Defaults), 0));
		TestFalse(TEXT("CDO has no Tick authority"), Defaults->PrimaryActorTick.bCanEverTick);
		TestFalse(TEXT("CDO has no runtime session"), Defaults->HasForestSession());
		TestEqual(TEXT("CDO has no dynamic branch components"), Defaults->GetBranchMeshComponents().Num(), 0);
		TestEqual(TEXT("CDO has no instance components"), Defaults->GetInstanceComponents().Num(), 0);
		const auto CdoSample = Defaults->GetForestGeometrySample();
		TestFalse(TEXT("CDO has no accepted runtime token"), CdoSample.ContactToken.IsValid());
		TestEqual(TEXT("CDO has no runtime geometry"), CdoSample.Branches.Num(), 0);
	};
	CheckDefaults();
	FFixture F(true, true, LoadedClass.Get()); // No ConfigureMesh: the asset supplies mesh/material/layout.
	if (!TestTrue(TEXT("Saved Blueprint fixture is ready"), F.Ready())) { return false; }
	TestTrue(TEXT("Spawned resource owner uses the loaded Blueprint class"), F.Forest->GetClass() == LoadedClass.Get());
	TestFalse(TEXT("Spawned Blueprint has no Tick"), F.Forest->PrimaryActorTick.bCanEverTick);
	TestFalse(TEXT("Spawned Blueprint never enables Actor Tick"), F.Forest->IsActorTickEnabled());
	TestFalse(TEXT("Spawned Blueprint has no session before real contact"), F.Forest->HasForestSession());
	TestEqual(TEXT("Spawned Blueprint has no dynamic branches before real contact"), F.Forest->GetBranchMeshComponents().Num(), 0);
	TestEqual(TEXT("Spawned Blueprint has no dynamic instance components before contact"), F.Forest->GetInstanceComponents().Num(), 0);
	TestEqual(TEXT("Spawned Blueprint contains only its inherited native root"), TInlineComponentArray<UActorComponent*>(F.Forest).Num(), 1);
	TestTrue(TEXT("Spawn retains the saved fifteen-branch layout"), LayoutProperty->Identical(&AuthoredLayout, LayoutProperty->ContainerPtrToValuePtr<TArray<FDYForestBranchDefinition>>(F.Forest), 0));
	const FGuid Token = F.Resolve();
	if (!TestTrue(TEXT("Fixture obtained an actual current Resolve token"), Token.IsValid() && F.Director->IsResolvedTokenCurrent(Token))) { return false; }
	TestFalse(TEXT("Saved Blueprint cannot begin before actual A contact"), F.Presentation->BeginForestPresentation(Token));
	if (!TestTrue(TEXT("Actual Staff A contact is accepted"), F.Contact())) { return false; }
	const auto Contact = F.Presentation->GetStaffContactPresentationSnapshot();
	if (!TestTrue(TEXT("Accepted contact belongs to this real Resolve"), Contact.bHasContact && Contact.Token == Token)) { return false; }
	F.Forest->SetActorTransform(FTransform(FRotator(15, 35, 7), FVector(125, 333, -62), FVector(2, 3, 4)));
	if (!TestTrue(TEXT("Presentation starts saved Blueprint resource session"), F.Presentation->BeginForestPresentation(Token))) { return false; }
	const auto Components = F.Forest->GetBranchMeshComponents();
	if (!TestEqual(TEXT("Saved defaults create fifteen actual mesh components"), Components.Num(), 15)) { return false; }
	const FBox MeshBounds = Cylinder->GetBoundingBox();
	for (const double Progress : {0.0, .5, 1.0})
	{
		if (!TestTrue(TEXT("Presentation applies requested normalized progress"), F.Presentation->SetForestNormalizedGrowth(Token, Progress))) { return false; }
		const auto Sample = F.Forest->GetForestGeometrySample();
		const auto Expected = UDYForestGeometryLibrary::SampleForestGeometry(Contact, AuthoredLayout, Progress, MeshBounds.Min, MeshBounds.Max);
		if (!TestEqual(TEXT("Saved authoring remains inside the fixture receiver"), Sample.Status, EDYForestGeometryStatus::Valid)
			|| !TestEqual(TEXT("Independent saved-layout sample is valid"), Expected.Status, EDYForestGeometryStatus::Valid)
			|| !TestEqual(TEXT("Every progress retains fifteen branch samples"), Sample.Branches.Num(), 15)) { return false; }
		TestTrue(TEXT("Progress reuses actual components"), Components == F.Forest->GetBranchMeshComponents());
		TestTrue(TEXT("Physical root is the actual accepted Staff A"), Sample.PhysicalRoot.Equals(Contact.Projection.Staff.EndAWorld, UE_DOUBLE_SMALL_NUMBER));
		TestTrue(TEXT("Shadow root is the actual accepted screen contact"), Sample.ShadowRoot.Equals(Contact.ContactWorldPosition, UE_DOUBLE_SMALL_NUMBER));
		TestTrue(TEXT("Geometry retains the authorized contact identity"), Sample.ContactToken == Token);
		int32 VisibleCount = 0;
		for (int32 Index = 0; Index < Components.Num(); ++Index)
		{
			const UStaticMeshComponent* Component = Components[Index];
			if (!TestTrue(TEXT("Branch is a registered component owned by the saved Blueprint instance"), IsValid(Component) && Component->IsRegistered() && Component->GetOwner() == F.Forest && Component->GetWorld() == F.World)) { return false; }
			const auto& Branch = Sample.Branches[Index];
			const auto& ExpectedBranch = Expected.Branches[Index];
			TestTrue(TEXT("Actual mesh remains the saved Cylinder"), Component->GetStaticMesh() == Cylinder);
			TestTrue(TEXT("Actual material uses the saved mesh fallback"), Component->GetMaterial(0) == MeshMaterial);
			TestEqual(TEXT("No material override was introduced at runtime"), Component->GetNumOverrideMaterials(), 0);
			TestTrue(TEXT("Actual component remains movable and collision-free"), Component->Mobility == EComponentMobility::Movable && Component->GetCollisionEnabled() == ECollisionEnabled::NoCollision && !Component->GetGenerateOverlapEvents());
			TestTrue(TEXT("Visibility, hidden state and shadow follow the sample"), Component->IsVisible() == Branch.bVisible && Component->bHiddenInGame == !Branch.bVisible && Component->CastShadow == Branch.bVisible);
			TestEqual(TEXT("Visible state matches the saved-layout sample"), Branch.bVisible, ExpectedBranch.bVisible);
			TestEqual(TEXT("Growth portion matches the saved-layout sample"), Branch.Portion, ExpectedBranch.Portion);
			FVector Min, Max; Component->GetLocalBounds(Min, Max);
			TestTrue(TEXT("Actual component bounds match saved mesh bounds"), Min.Equals(MeshBounds.Min, UE_DOUBLE_SMALL_NUMBER) && Max.Equals(MeshBounds.Max, UE_DOUBLE_SMALL_NUMBER));
			if (!Branch.bVisible) { continue; } // Hidden branch transforms are intentionally undefined.
			++VisibleCount;
			const FTransform Transform = Component->GetComponentTransform();
			TestTrue(TEXT("Actual world transform matches sample without an Actor multiplier"), Transform.Equals(Branch.MeshWorldTransform, UE_DOUBLE_SMALL_NUMBER) && Transform.Equals(ExpectedBranch.MeshWorldTransform, UE_DOUBLE_SMALL_NUMBER));
			const FVector CenterXY((Min.X + Max.X) * .5, (Min.Y + Max.Y) * .5, 0);
			const FVector Start = Transform.TransformPosition(CenterXY + FVector(0, 0, Min.Z));
			const FVector End = Transform.TransformPosition(CenterXY + FVector(0, 0, Max.Z));
			TestTrue(TEXT("Actual mesh endpoints match geometry sample"), Start.Equals(Branch.StartWorld, UE_DOUBLE_SMALL_NUMBER) && End.Equals(Branch.EndWorld, UE_DOUBLE_SMALL_NUMBER));
			const auto& Projection = Contact.Projection;
			const auto ProjectStart = UDYStaffProjectionLibrary::ProjectPointToScreen(Projection.EmitterWorld, Start, Projection.ScreenTransform, Projection.ScreenLocalMin, Projection.ScreenLocalMax);
			const auto ProjectEnd = UDYStaffProjectionLibrary::ProjectPointToScreen(Projection.EmitterWorld, End, Projection.ScreenTransform, Projection.ScreenLocalMin, Projection.ScreenLocalMax);
			TestEqual(TEXT("Actual branch start projects onto the receiver"), ProjectStart.Status, EDYStaffProjectionStatus::OnScreen);
			TestEqual(TEXT("Actual branch end projects onto the receiver"), ProjectEnd.Status, EDYStaffProjectionStatus::OnScreen);
			const auto& Definition = AuthoredLayout[Index];
			const FVector2D EndOffset = FMath::Lerp(Definition.StartScreenOffset, Definition.EndScreenOffset, Branch.Portion);
			TestTrue(TEXT("Actual start projects to saved screen offset"), ProjectStart.ScreenLocalPosition.Equals(Projection.EndA.ScreenLocalPosition + FVector(0, Definition.StartScreenOffset.X, Definition.StartScreenOffset.Y), UE_DOUBLE_SMALL_NUMBER));
			TestTrue(TEXT("Actual end projects to saved interpolated screen offset"), ProjectEnd.ScreenLocalPosition.Equals(Projection.EndA.ScreenLocalPosition + FVector(0, EndOffset.X, EndOffset.Y), UE_DOUBLE_SMALL_NUMBER));
			FVector2D ProjectedMin(std::numeric_limits<double>::max(), std::numeric_limits<double>::max());
			FVector2D ProjectedMax(std::numeric_limits<double>::lowest(), std::numeric_limits<double>::lowest());
			for (int32 Corner = 0; Corner < 8; ++Corner)
			{
				const FVector Local((Corner & 1) ? Max.X : Min.X, (Corner & 2) ? Max.Y : Min.Y, (Corner & 4) ? Max.Z : Min.Z);
				const auto Point = UDYStaffProjectionLibrary::ProjectPointToScreen(Projection.EmitterWorld, Transform.TransformPosition(Local), Projection.ScreenTransform, Projection.ScreenLocalMin, Projection.ScreenLocalMax);
				TestEqual(TEXT("Actual mesh bounds corner projects inside the receiver"), Point.Status, EDYStaffProjectionStatus::OnScreen);
				ProjectedMin.X = FMath::Min(ProjectedMin.X, Point.ScreenLocalPosition.Y);
				ProjectedMin.Y = FMath::Min(ProjectedMin.Y, Point.ScreenLocalPosition.Z);
				ProjectedMax.X = FMath::Max(ProjectedMax.X, Point.ScreenLocalPosition.Y);
				ProjectedMax.Y = FMath::Max(ProjectedMax.Y, Point.ScreenLocalPosition.Z);
			}
			TestTrue(TEXT("Actual eight-corner envelope matches sample projection"), ProjectedMin.Equals(Branch.ProjectedMin, UE_DOUBLE_SMALL_NUMBER) && ProjectedMax.Equals(Branch.ProjectedMax, UE_DOUBLE_SMALL_NUMBER));
		}
		if (Progress == 0) { TestEqual(TEXT("Zero growth hides all fifteen branches"), VisibleCount, 0); }
		if (Progress == .5) { TestTrue(TEXT("Mid-growth has visible and still-hidden authored branches"), VisibleCount > 0 && VisibleCount < 15); }
		if (Progress == 1) { TestEqual(TEXT("Full growth shows all fifteen branches"), VisibleCount, 15); }
		CheckDefaults();
	}
	TestEqual(TEXT("Cosmetic saved Blueprint does not resolve the puzzle again"), F.Director->GetLastEvaluation().ResolveCount, 1);
	TestTrue(TEXT("Explicit clear releases the saved Blueprint session"), F.Presentation->ClearForestPresentation(Token));
	TestFalse(TEXT("Cleared saved Blueprint has no session"), F.Forest->HasForestSession());
	TestEqual(TEXT("Clear releases all actual branch components"), F.Forest->GetBranchMeshComponents().Num(), 0);
	TestEqual(TEXT("Clear removes all dynamic instance components"), F.Forest->GetInstanceComponents().Num(), 0);
	for (const auto* Component : Components) { TestTrue(TEXT("Cleared actual meshes no longer render or cast"), !IsValid(Component) || (!Component->IsVisible() && !Component->CastShadow)); }
	if (!TestTrue(TEXT("Current real contact can explicitly rebuild saved Dev resources"), F.Presentation->BeginForestPresentation(Token))
		|| !TestTrue(TEXT("Rebuilt saved resources reach visible full growth"), F.Presentation->SetForestNormalizedGrowth(Token, 1))) { return false; }
	const auto ResetComponents = F.Forest->GetBranchMeshComponents();
	if (!TestEqual(TEXT("Reset precondition has fifteen actual rebuilt branches"), ResetComponents.Num(), 15)) { return false; }
	for (const auto* Component : ResetComponents)
	{
		if (!TestTrue(TEXT("Every rebuilt branch is visible and casting before Reset"), IsValid(Component) && Component->IsVisible() && !Component->bHiddenInGame && Component->CastShadow)) { return false; }
	}
	F.Director->ResetCurrentPuzzle();
	TestFalse(TEXT("Director Reset clears saved Blueprint immediately"), F.Forest->HasForestSession());
	TestEqual(TEXT("Reset releases all saved Blueprint branch resources"), F.Forest->GetBranchMeshComponents().Num(), 0);
	TestEqual(TEXT("Reset removes all dynamic instance components"), F.Forest->GetInstanceComponents().Num(), 0);
	TestEqual(TEXT("After clear and Reset only the native root remains"), TInlineComponentArray<UActorComponent*>(F.Forest).Num(), 1);
	for (const auto* Component : ResetComponents) { TestTrue(TEXT("Reset actual meshes no longer render or cast"), !IsValid(Component) || (!Component->IsVisible() && !Component->CastShadow)); }
	TestFalse(TEXT("Old saved-asset callback is rejected after Reset"), F.Presentation->SetForestNormalizedGrowth(Token, .5));
	TestTrue(TEXT("Runtime clear and Reset preserve instance authoring"), LayoutProperty->Identical(&AuthoredLayout, LayoutProperty->ContainerPtrToValuePtr<TArray<FDYForestBranchDefinition>>(F.Forest), 0));
	CheckDefaults();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestCanopyAnchorTest,
	"DengYingShanHai.P03.ForestPresentation.CanopyAnchorsApplyWorldOffsetOnce", DYForestPresentationTests::Flags)
bool FDYForestCanopyAnchorTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	UStaticMesh* CrownMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	DYForestPresentationTests::ObjectProperty(F.Forest, TEXT("CanopyMesh"), CrownMesh);
	const FArrayProperty* CrownIndices = FindFProperty<FArrayProperty>(F.Forest->GetClass(), TEXT("CanopyBranches"));
	*CrownIndices->ContainerPtrToValuePtr<TArray<int32>>(F.Forest) = {1};
	const FStructProperty* Offset = FindFProperty<FStructProperty>(F.Forest->GetClass(), TEXT("WorldOffset"));
	*Offset->ContainerPtrToValuePtr<FVector>(F.Forest) = FVector(-40, 17, 5);
	const FGuid Token = F.Grow(.55);
	const auto Branches = F.Forest->GetBranchMeshComponents();
	const auto Crowns = F.Forest->GetCanopyMeshComponents();
	if (!TestEqual(TEXT("Original authored branches unchanged"), Branches.Num(), 2)
		|| !TestEqual(TEXT("One separate crown created"), Crowns.Num(), 1)) { return false; }
	TestFalse(TEXT("Crown stays hidden until its growth phase"), Crowns[0]->IsVisible());
	for (const double Progress : {.8, 1.0})
	{
		TestTrue(TEXT("Actual contact token drives growth"), F.Presentation->SetForestNormalizedGrowth(Token, Progress));
		const FVector Tip = Branches[1]->GetComponentTransform().TransformPosition(
			FVector(0, 0, Branches[1]->GetStaticMesh()->GetBoundingBox().Max.Z));
		const FVector CrownBase = Crowns[0]->GetComponentTransform().TransformPosition(
			FVector(0, 0, CrownMesh->GetBoundingBox().Min.Z));
		TestTrue(TEXT("Crown root meets the actual branch tip with nonzero XYZ world offset"), CrownBase.Equals(Tip, 1e-6));
		TestTrue(TEXT("Growing crown is visible and casts shadow"), Crowns[0]->IsVisible() && Crowns[0]->CastShadow);
	}
	F.Director->ResetCurrentPuzzle();
	TestEqual(TEXT("Reset removes all crowns"), F.Forest->GetCanopyMeshComponents().Num(), 0);
	TestEqual(TEXT("Reset removes all branches"), F.Forest->GetBranchMeshComponents().Num(), 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestCanopyHeightRevealTest,
	"DengYingShanHai.P03.ForestPresentation.CanopyHeightRevealFreezesScaleAndSession", DYForestPresentationTests::Flags)
bool FDYForestCanopyHeightRevealTest::RunTest(const FString& Parameters)
{
	DYForestPresentationTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	const FBoolProperty* HeightReveal = FindFProperty<FBoolProperty>(F.Forest->GetClass(), TEXT("bCanopyHeightReveal"));
	if (!TestNotNull(TEXT("Height reveal is an authored property"), HeightReveal)) { return false; }
	TestFalse(TEXT("Existing canopy growth stays the default"), HeightReveal->GetPropertyValue_InContainer(F.Forest));
	HeightReveal->SetPropertyValue_InContainer(F.Forest, true);
	UStaticMesh* CrownMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (!TestNotNull(TEXT("Crown test mesh loads"), CrownMesh)) { return false; }
	DYForestPresentationTests::ObjectProperty(F.Forest, TEXT("CanopyMesh"), CrownMesh);
	const FArrayProperty* CrownIndices = FindFProperty<FArrayProperty>(F.Forest->GetClass(), TEXT("CanopyBranches"));
	*CrownIndices->ContainerPtrToValuePtr<TArray<int32>>(F.Forest) = {1};
	const FArrayProperty* CrownScales = FindFProperty<FArrayProperty>(F.Forest->GetClass(), TEXT("CanopyScales"));
	constexpr double ClusterScale = 1.25;
	*CrownScales->ContainerPtrToValuePtr<TArray<double>>(F.Forest) = {ClusterScale};
	const FStructProperty* Offset = FindFProperty<FStructProperty>(F.Forest->GetClass(), TEXT("WorldOffset"));
	*Offset->ContainerPtrToValuePtr<FVector>(F.Forest) = FVector(-40, 17, 5);
	const FGuid Token = F.Grow(.5);
	const auto Branches = F.Forest->GetBranchMeshComponents();
	const auto Crowns = F.Forest->GetCanopyMeshComponents();
	if (!TestTrue(TEXT("Actual contact starts the session"), Token.IsValid() && F.Forest->HasForestSession())
		|| !TestEqual(TEXT("Original authored branches remain"), Branches.Num(), 2)
		|| !TestEqual(TEXT("One separate crown created"), Crowns.Num(), 1)) { return false; }
	HeightReveal->SetPropertyValue_InContainer(F.Forest, false);
	for (const double Progress : {.5, .55, .8, 1.0})
	{
		if (!TestTrue(TEXT("Actual contact token drives height reveal"), F.Presentation->SetForestNormalizedGrowth(Token, Progress))) { return false; }
		const double Growth = FMath::Clamp((Progress - .55) / .45, 0.0, 1.0);
		TestTrue(TEXT("Session keeps full authored scale despite a mid-session option edit"), Crowns[0]->GetComponentScale().Equals(FVector(ClusterScale), 1e-6));
		const FVector Tip = Branches[1]->GetComponentTransform().TransformPosition(
			FVector(0, 0, Branches[1]->GetStaticMesh()->GetBoundingBox().Max.Z));
		const FVector CrownBase = Crowns[0]->GetComponentTransform().TransformPosition(
			FVector(0, 0, CrownMesh->GetBoundingBox().Min.Z));
		TestTrue(TEXT("Fixed-scale root stays on the moving branch tip with XYZ world offset"), CrownBase.Equals(Tip, 1e-6));
		const auto& Data = Crowns[0]->GetCustomPrimitiveData().Data;
		if (TestTrue(TEXT("Height reveal supplies Custom Primitive Data 0"), Data.IsValidIndex(0)))
		{
			TestTrue(TEXT("Custom Primitive Data 0 retains the original normalized growth window"), FMath::IsNearlyEqual(Data[0], static_cast<float>(Growth), 1e-6f));
		}
		const bool bVisible = Progress > .55;
		TestTrue(TEXT("Original visibility and shadow threshold is preserved"), Crowns[0]->IsVisible() == bVisible
			&& Crowns[0]->bHiddenInGame == !bVisible && Crowns[0]->CastShadow == bVisible);
	}
	F.Director->ResetCurrentPuzzle();
	TestFalse(TEXT("Reset ends the height-reveal session"), F.Forest->HasForestSession());
	TestEqual(TEXT("Reset removes all crowns"), F.Forest->GetCanopyMeshComponents().Num(), 0);
	TestEqual(TEXT("Reset removes all branches"), F.Forest->GetBranchMeshComponents().Num(), 0);
	const FGuid NewToken = F.Grow(.8);
	const auto NewCrowns = F.Forest->GetCanopyMeshComponents();
	if (!TestTrue(TEXT("Reset accepts a fresh contact session"), NewToken.IsValid() && NewToken != Token && F.Forest->HasForestSession())
		|| !TestEqual(TEXT("Fresh session creates one crown"), NewCrowns.Num(), 1)) { return false; }
	const double OriginalScale = ClusterScale * ((.8 - .55) / .45);
	TestTrue(TEXT("Fresh false-option session restores original scaled growth"), NewCrowns[0]->GetComponentScale().Equals(FVector(OriginalScale), 1e-6));
	TestTrue(TEXT("Original path leaves Custom Primitive Data untouched"), NewCrowns[0]->GetCustomPrimitiveData().Data.IsEmpty());
	return true;
}

#if WITH_EDITOR
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYForestSavedAssetGraphTest,
	"DengYingShanHai.P03.ForestAsset.SavedBlueprintHasNoExecutableGraphLogic", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDYForestSavedAssetGraphTest::RunTest(const FString& Parameters)
{
	TStrongObjectPtr<UBlueprint> Blueprint(LoadObject<UBlueprint>(nullptr,
		TEXT("/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev.BP_DYForestPresentation_Dev")));
	if (!TestNotNull(TEXT("Actual saved Blueprint source asset loads"), Blueprint.Get())) { return false; }
	TestTrue(TEXT("Saved source asset has the expected native parent"), Blueprint->ParentClass == ADYForestPresentationActor::StaticClass());
	TestTrue(TEXT("Saved Blueprint compiled successfully"), Blueprint->Status == BS_UpToDate || Blueprint->Status == BS_UpToDateWithWarnings);
	TestTrue(TEXT("Saved source and loaded generated class agree"), Blueprint->GeneratedClass == LoadClass<ADYForestPresentationActor>(nullptr, DYForestPresentationTests::ForestAssetClassPath));
	TestEqual(TEXT("Saved data-only Blueprint adds no variables"), Blueprint->NewVariables.Num(), 0);
	TestEqual(TEXT("Saved data-only Blueprint adds no timelines"), Blueprint->Timelines.Num(), 0);
	TestEqual(TEXT("Saved data-only Blueprint adds no component templates"), Blueprint->ComponentTemplates.Num(), 0);
	TestEqual(TEXT("Saved data-only Blueprint adds no macro graphs"), Blueprint->MacroGraphs.Num(), 0);
	TestEqual(TEXT("Saved data-only Blueprint adds no delegate graphs"), Blueprint->DelegateSignatureGraphs.Num(), 0);
	TArray<UEdGraph*> Graphs;
	auto AddPages = [&](const auto& Pages) { for (UEdGraph* Graph : Pages) { Graphs.AddUnique(Graph); } };
	AddPages(Blueprint->UbergraphPages);
	AddPages(Blueprint->FunctionGraphs);
	AddPages(Blueprint->MacroGraphs);
	AddPages(Blueprint->DelegateSignatureGraphs);
	for (const UEdGraph* Graph : Blueprint->FunctionGraphs)
	{
		if (TestNotNull(TEXT("Function graph exists"), Graph))
		{
			TestEqual(TEXT("Only the factory construction graph may be present"), Graph->GetFName(), FName(TEXT("UserConstructionScript")));
		}
	}
	int32 NodeCount = 0, ExecPinCount = 0, ExecLinkCount = 0;
	for (int32 GraphIndex = 0; GraphIndex < Graphs.Num(); ++GraphIndex)
	{
		const UEdGraph* Graph = Graphs[GraphIndex];
		if (!TestNotNull(TEXT("Authored graph exists"), Graph)) { continue; }
		AddPages(Graph->SubGraphs);
		for (const UEdGraphNode* Node : Graph->Nodes)
		{
			if (!TestNotNull(TEXT("Authored graph node exists"), Node)) { continue; }
			++NodeCount;
			AddPages(Node->GetSubGraphs());
			for (const UEdGraphPin* Pin : Node->Pins)
			{
				if (Pin && Pin->PinType.PinCategory == FName(TEXT("exec")))
				{
					++ExecPinCount;
					ExecLinkCount += Pin->LinkedTo.Num();
					TestEqual(FString::Printf(TEXT("No executable link on %s.%s"), *Node->GetPathName(), *Pin->PinName.ToString()), Pin->LinkedTo.Num(), 0);
				}
			}
		}
	}
	AddInfo(FString::Printf(TEXT("Inspected saved Blueprint status=%d, UbergraphPages=%d, FunctionGraphs=%d, recursive graphs=%d, nodes=%d, exec pins=%d, exec pin links=%d; factory nodes are inspected, not assumed absent."),
		static_cast<int32>(Blueprint->Status.GetValue()), Blueprint->UbergraphPages.Num(), Blueprint->FunctionGraphs.Num(), Graphs.Num(), NodeCount, ExecPinCount, ExecLinkCount));
	TestEqual(TEXT("Saved Blueprint contains no connected executable graph logic"), ExecLinkCount, 0);
	return true;
}
#endif

#endif
