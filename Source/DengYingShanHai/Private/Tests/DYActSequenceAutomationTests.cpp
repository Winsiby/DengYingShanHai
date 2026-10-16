#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Puzzles/DYPuzzleDefinition.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Stage/DYForestPresentationActor.h"
#include "Stage/DYStagePresentation.h"
#include "UI/DYInteractionHUDWidget.h"
#include "UI/DYInteractionHUD.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"

/** Authoring/reference setup and protected submission boundary only.
 * Never fabricates a runtime phase, index, identity, contact or completed forest.
 */
struct FDYActSequenceTestSeam
{
	static void ConfigureDirector(ADYPuzzleDirector& Director, ADYLightRigActor* Light,
		ADYPuppetActor* Puppet, const TArray<FDYActSequenceEntry>& Entries, UDYPuzzleDefinition* Legacy)
	{
		Director.LightRig = Light;
		Director.PuppetActor = Puppet;
		Director.ActSequence = Entries;
		Director.PuzzleDefinition = Legacy;
	}
	static void ConfigurePresentation(ADYStagePresentation& Stage, ADYPuzzleDirector* Director,
		ADYStageEnvironment* Environment, AStaticMeshActor* Receiver, AActor* Ground,
		ADYForestPresentationActor* Forest)
	{
		Stage.PuzzleDirector = Director;
		Stage.StageEnvironment = Environment;
		Stage.StaffProjectionScreen = Receiver;
		Stage.NarrativeGroundLine = Ground;
		Stage.ForestPresentationActor = Forest;
		Stage.bEnableStaffContactPresentation = true;
	}
	/** Authoring opt-in only, before Presentation BeginPlay. Never writes a runtime phase. */
	static void SetFiveStateDev(ADYStagePresentation& Stage) { Stage.bEnableFiveStateDevEnvironment = true; }
	static bool Transition(ADYPuzzleDirector& Director, ADYStagePresentation* Stage, const FGuid& Token)
	{
		return Director.AcceptActTransition(Stage, Token);
	}
	/** Negative unauthorized-caller probes only; positive completion uses native geometry proof. */
	static bool UnauthorizedFinale(ADYPuzzleDirector& Director, ADYStagePresentation* Stage, const FGuid& Token)
	{
		return Director.AcceptFinaleCompletion(Stage, Token);
	}
	static void AttachHud(ADYInteractionHUD& Hud, ADYStagePresentation* Stage) { Hud.AttachPresentation(Stage); }
	static FDYActSequenceSnapshot HudAct(const ADYInteractionHUD& Hud) { return Hud.ActDisplay; }
	static EDYStageFeedbackDisplay HudFeedback(const ADYInteractionHUD& Hud) { return Hud.Feedback; }
	static void DeliverEvaluation(ADYStagePresentation& Stage, const FDYEvaluationResult& Result) { Stage.HandleEvaluationUpdated(Result); }
};

namespace DYActSequenceTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext
		| EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter;

	template<class T> void ObjectProperty(UObject* Object, const TCHAR* Name, T* Value)
	{
		FObjectPropertyBase* Property = FindFProperty<FObjectPropertyBase>(Object->GetClass(), Name);
		check(Property);
		Property->SetObjectPropertyValue_InContainer(Object, Value);
	}

	struct FFixture
	{
		explicit FFixture(bool bSequence = true, bool bBeginPresentation = true, bool bBeginDependencies = true)
		{
			if (!GEngine) { return; }
			World = UWorld::CreateWorld(EWorldType::Game, false,
				MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYActSequenceWorld")), GetTransientPackage());
			StrongWorld.Reset(World);
			if (!World) { return; }
			GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
			Light = World->SpawnActor<ADYLightRigActor>(FVector(-460, -20, 310), FRotator::ZeroRotator);
			Puppet = World->SpawnActor<ADYPuppetActor>(FVector(600, -80, 210), FRotator::ZeroRotator);
			Director = World->SpawnActor<ADYPuzzleDirector>();
			Environment = World->SpawnActor<ADYStageEnvironment>();
			Stage = World->SpawnActor<ADYStagePresentation>();
			Forest = World->SpawnActor<ADYForestPresentationActor>();
			Receiver = World->SpawnActor<AStaticMeshActor>();
			Ground = World->SpawnActor<AStaticMeshActor>();
			if (!World || !Light || !Puppet || !Director || !Environment || !Stage || !Forest || !Receiver || !Ground) { return; }
			Receiver->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
			Receiver->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
			Receiver->SetActorTransform(FTransform(FRotator::ZeroRotator, FVector(950, 0, 350), FVector(.5, 9, 8)));
			Ground->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
			for (int32 Index = 0; Index < 3; ++Index)
			{
				UDYPuzzleDefinition* Definition = NewObject<UDYPuzzleDefinition>(Director);
				Definition->PuzzleId = FName(*FString::Printf(TEXT("ActSequenceFixtureP%02d"), Index + 1));
				Definition->LightPosition.bEnabled = true;
				Definition->LightPosition.Target = Index == 0 ? .68 : .72;
				Definition->LightPosition.EnterTolerance = Index == 0 ? .045 : .05;
				Definition->LightPosition.ExitTolerance = Index == 0 ? .085 : .09;
				Definition->PuppetPosition.bEnabled = Index != 0;
				Definition->PuppetPosition.Target = Index == 1 ? .80 : .85;
				Definition->PuppetPosition.EnterTolerance = .05;
				Definition->PuppetPosition.ExitTolerance = .09;
				Definition->RequiredPuppetPoseId = Index == 0 ? NAME_None : FName(TEXT("P02_StrideReach"));
				// Contract fixture only. Saved definitions and real holding-time tuning are untouched.
				Definition->RequiredHoldSeconds = 0;
				Definitions.Add(Definition);
				FDYActSequenceEntry Entry;
				Entry.Definition = Definition;
				Entry.ActTitle = FText::FromString(FString::Printf(TEXT("Fixture act %d"), Index + 1));
				Entries.Add(Entry);
			}
			ObjectProperty(Forest, TEXT("BranchMesh"), LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
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
			FArrayProperty* Layout = FindFProperty<FArrayProperty>(Forest->GetClass(), TEXT("BranchLayout"));
			check(Layout);
			*Layout->ContainerPtrToValuePtr<TArray<FDYForestBranchDefinition>>(Forest) = {Root, Child};
			FDYActSequenceTestSeam::ConfigureDirector(*Director, Light, Puppet,
				bSequence ? Entries : TArray<FDYActSequenceEntry>(), Definitions[2]);
			FDYActSequenceTestSeam::ConfigurePresentation(*Stage, Director, Environment, Receiver, Ground, Forest);
			if (bBeginDependencies)
			{
				Light->DispatchBeginPlay();
				Puppet->DispatchBeginPlay();
			}
			Forest->DispatchBeginPlay();
			if (bBeginPresentation) { Stage->DispatchBeginPlay(); }
			Director->DispatchBeginPlay();
		}
		~FFixture()
		{
			if (World && GEngine)
			{
				World->EndPlay(EEndPlayReason::Quit);
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
			StrongWorld.Reset();
		}
		bool Ready() const
		{
			return World && Light && Puppet && Director && Environment && Stage && Forest && Receiver && Ground
				&& Definitions.Num() == 3;
		}
		int32 Index() const { return Director->GetActSequenceSnapshot().ActIndex; }
		EDYActSequencePhase Phase() const { return Director->GetActSequenceSnapshot().Phase; }
		FGuid Resolve()
		{
			const int32 Act = Director->IsActSequenceEnabled() ? Index() : 2;
			if (!Definitions.IsValidIndex(Act)) { return FGuid(); }
			Light->GetLightControlComponent()->SetNormalizedValue(Definitions[Act]->LightPosition.Target);
			if (Act != 0) { Puppet->GetPuppetControlComponent()->SetNormalizedValue(Definitions[Act]->PuppetPosition.Target); }
			const auto Capture = UDYStaffProjectionLibrary::CaptureStaffProjection(Light, Puppet, Receiver->GetStaticMeshComponent());
			FVector Anchor = Capture.EndA.ScreenLocalPosition;
			Anchor.Z -= 5; // Test-only short drop, not the authored Z70 choice.
			Ground->SetActorLocation(Capture.ScreenTransform.TransformPosition(Anchor));
			Director->EvaluatePuzzleNow();
			return Director->GetResolvedPuzzleSnapshot().Token;
		}
		bool Advance(const FGuid& Token) { return FDYActSequenceTestSeam::Transition(*Director, Stage, Token); }
		bool ReachFinal()
		{
			for (int32 Act = 0; Act < 2; ++Act)
			{
				if (Index() != Act || !Advance(Resolve())) { return false; }
			}
			return Index() == 2 && Phase() == EDYActSequencePhase::Playing;
		}
		bool Contact()
		{
			const auto Capture = UDYStaffProjectionLibrary::CaptureStaffProjection(Light, Puppet, Receiver->GetStaticMeshComponent());
			const auto Snapshot = Stage->GetResolvedStaffPresentationSnapshot();
			if (!Capture.bHasGeometry || !Snapshot.bHasSnapshot || Capture.EndA.RayParameter == 0) { return false; }
			FVector End = Capture.EndA.ScreenLocalPosition;
			End.Z = Snapshot.GroundLine.ScreenLocalZ;
			const FVector NewA = Capture.EmitterWorld
				+ (Capture.ScreenTransform.TransformPosition(End) - Capture.EmitterWorld) / Capture.EndA.RayParameter;
			for (UStaticMeshComponent* Mesh : TInlineComponentArray<UStaticMeshComponent*>(Puppet))
			{
				if (Mesh->GetFName() == TEXT("Staff")) { Mesh->AddWorldOffset(NewA - Capture.Staff.EndAWorld); }
			}
			return Stage->TryAcceptStaffContact(Snapshot.Token);
		}
		bool Grow(const FGuid& Token, const double Progress)
		{
			return Contact() && Stage->BeginForestPresentation(Token) && Stage->SetForestNormalizedGrowth(Token, Progress);
		}
		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> StrongWorld;
		ADYLightRigActor* Light = nullptr;
		ADYPuppetActor* Puppet = nullptr;
		ADYPuzzleDirector* Director = nullptr;
		ADYStageEnvironment* Environment = nullptr;
		ADYStagePresentation* Stage = nullptr;
		ADYForestPresentationActor* Forest = nullptr;
		AStaticMeshActor* Receiver = nullptr;
		AStaticMeshActor* Ground = nullptr;
		TArray<UDYPuzzleDefinition*> Definitions;
		TArray<FDYActSequenceEntry> Entries;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActOrderTest,
	"DengYingShanHai.ThreeAct.OrderedFlowAndLegacyDefault", DYActSequenceTests::Flags)
bool FDYActOrderTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F, Legacy(false);
	if (!TestTrue(TEXT("Real fixtures ready"), F.Ready() && Legacy.Ready())) { return false; }
	TestEqual(TEXT("Sequence begins at first act"), F.Index(), 0);
	TestEqual(TEXT("Three explicit acts"), F.Director->GetActSequenceSnapshot().ActCount, 3);
	TestFalse(TEXT("First act puppet remains disabled"), F.Puppet->GetPuppetControlComponent()->IsControlEnabled());
	TestEqual(TEXT("Sampling baseline retained"), F.Director->GetEvaluationFrequencyHz(), 15.0);
	for (int32 Act = 0; Act < 2; ++Act)
	{
		const FGuid Token = F.Resolve();
		TestTrue(TEXT("Success comes from actual evaluator"), Token.IsValid() && F.Director->IsResolvedTokenCurrent(Token));
		TestEqual(TEXT("Resolve waits, never advances itself"), F.Index(), Act);
		TestEqual(TEXT("Intermediate act awaits transition"), F.Phase(), EDYActSequencePhase::AwaitingTransition);
		TestTrue(TEXT("Registered native callback advances one act"), F.Advance(Token));
		TestEqual(TEXT("Exactly one step"), F.Index(), Act + 1);
		TestEqual(TEXT("Next act playing"), F.Phase(), EDYActSequencePhase::Playing);
		TestEqual(TEXT("Next light baseline"), F.Light->GetLightControlComponent()->GetNormalizedValue(), .15);
		TestEqual(TEXT("Next puppet baseline"), F.Puppet->GetPuppetControlComponent()->GetNormalizedValue(), .15);
		TestFalse(TEXT("Overlapping old answer did not solve next act"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
		TestTrue(TEXT("Combined act puppet enabled"), F.Puppet->GetPuppetControlComponent()->IsControlEnabled());
		TestEqual(TEXT("Prior environmental progress retained"), F.Environment->GetCurrentState(),
			Act == 0 ? EDYStageEnvironmentState::SunAwakened : EDYStageEnvironmentState::ChaseAwakened);
	}
	const FGuid Final = F.Resolve();
	TestEqual(TEXT("Final awaits actual presentation"), F.Phase(), EDYActSequencePhase::AwaitingFinale);
	TestFalse(TEXT("Final is not a normal transition"), F.Advance(Final));
	TestFalse(TEXT("Legacy has no sequence"), Legacy.Director->IsActSequenceEnabled());
	const FGuid LegacyToken = Legacy.Resolve();
	TestTrue(TEXT("Legacy still genuinely resolves"), Legacy.Director->IsResolvedTokenCurrent(LegacyToken));
	TestTrue(TEXT("Legacy staff opt-in still captures"), Legacy.Stage->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
	TestFalse(TEXT("Legacy no whole-experience completion"), Legacy.Stage->SubmitForestFinaleCompletion(LegacyToken));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActIdentityTest,
	"DengYingShanHai.ThreeAct.TransitionIdentityAndSingleConsume", DYActSequenceTests::Flags)
bool FDYActIdentityTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F, Other;
	if (!TestTrue(TEXT("Fixtures ready"), F.Ready() && Other.Ready())) { return false; }
	TestFalse(TEXT("Cannot advance while playing"), F.Advance(FGuid::NewGuid()));
	const FGuid Token = F.Resolve();
	const FGuid OtherToken = Other.Resolve();
	TestFalse(TEXT("Empty identity rejected"), F.Advance(FGuid()));
	TestFalse(TEXT("Random identity rejected"), F.Advance(FGuid::NewGuid()));
	TestFalse(TEXT("Other Director identity rejected"), F.Advance(OtherToken));
	TestFalse(TEXT("Other world's presentation rejected"), FDYActSequenceTestSeam::Transition(*F.Director, Other.Stage, Token));
	ADYStagePresentation* Unregistered = F.World->SpawnActor<ADYStagePresentation>();
	TestFalse(TEXT("Same-world unregistered caller rejected"), FDYActSequenceTestSeam::Transition(*F.Director, Unregistered, Token));
	TestFalse(TEXT("P01 cannot submit finale"), F.Stage->SubmitForestFinaleCompletion(Token));
	TestEqual(TEXT("All rejected callbacks preserve act"), F.Index(), 0);
	TestTrue(TEXT("Valid transition accepted once"), F.Advance(Token));
	TestFalse(TEXT("Duplicate cannot skip act"), F.Advance(Token));
	const FGuid Second = F.Resolve();
	TestFalse(TEXT("Old first identity cannot consume new transition"), F.Advance(Token));
	TestTrue(TEXT("Current second identity accepted"), F.Advance(Second));
	const FGuid Final = F.Resolve();
	TestFalse(TEXT("Private finale boundary rejects null caller"), FDYActSequenceTestSeam::UnauthorizedFinale(*F.Director, nullptr, Final));
	TestFalse(TEXT("Private finale boundary rejects unregistered caller"), FDYActSequenceTestSeam::UnauthorizedFinale(*F.Director, Unregistered, Final));
	TestEqual(TEXT("Unauthorized completion leaves final waiting"), F.Phase(), EDYActSequencePhase::AwaitingFinale);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActResolveStackTest,
	"DengYingShanHai.ThreeAct.ResolveNotificationStackGuard", DYActSequenceTests::Flags)
bool FDYActResolveStackTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	int32 Calls = 0;
	const FDelegateHandle Handle = F.Director->OnActSequenceChanged().AddLambda([&](const FDYActSequenceSnapshot& S)
	{
		if (S.Phase != EDYActSequencePhase::AwaitingTransition) { return; }
		++Calls;
		const FGuid Current = F.Director->GetResolvedPuzzleSnapshot().Token;
		TestTrue(TEXT("Notification already carries actual resolved identity"), Current.IsValid());
		TestFalse(TEXT("Synchronous callback cannot change resolve stack act"), F.Advance(Current));
		TestEqual(TEXT("Same act survives observer"), F.Index(), 0);
	});
	const FGuid Token = F.Resolve();
	F.Director->OnActSequenceChanged().Remove(Handle);
	TestEqual(TEXT("One actual waiting notification"), Calls, 1);
	TestTrue(TEXT("Original success snapshot survives notification"), F.Director->IsResolvedTokenCurrent(Token));
	TestTrue(TEXT("Callback accepted after notification stack returns"), F.Advance(Token));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActResetTest,
	"DengYingShanHai.ThreeAct.CurrentResetAndLateCallbacks", DYActSequenceTests::Flags)
bool FDYActResetTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready() && F.Advance(F.Resolve()))) { return false; }
	const FGuid Old = F.Resolve();
	FDYControlContext Context;
	IDYControllable::Execute_ResetControlState(F.Light, Context); // Real reset request event; not a fabricated Director result.
	TestEqual(TEXT("Reset keeps second act"), F.Index(), 1);
	TestEqual(TEXT("Reset returns to playing"), F.Phase(), EDYActSequencePhase::Playing);
	TestFalse(TEXT("Reset immediately invalidates old identity"), F.Director->IsResolvedTokenCurrent(Old));
	TestFalse(TEXT("Late transition rejected"), F.Advance(Old));
	TestEqual(TEXT("Earlier act environment retained"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::SunAwakened);
	TestEqual(TEXT("Real request resets light baseline"), F.Light->GetLightControlComponent()->GetNormalizedValue(), .15);
	TestEqual(TEXT("Real request resets puppet baseline"), F.Puppet->GetPuppetControlComponent()->GetNormalizedValue(), .15);
	if (!TestTrue(TEXT("Current second act can still advance"), F.Advance(F.Resolve()))) { return false; }
	for (const double Progress : {.0, .75, 1.0})
	{
		const FGuid Final = F.Resolve();
		if (!TestTrue(TEXT("Actual final forest session built"), F.Grow(Final, Progress))) { return false; }
		IDYControllable::Execute_ResetControlState(F.Puppet, Context);
		TestEqual(TEXT("Final reset retains third act"), F.Index(), 2);
		TestEqual(TEXT("Final reset playing"), F.Phase(), EDYActSequencePhase::Playing);
		TestFalse(TEXT("Old forest resources released"), F.Forest->HasForestSession());
		TestFalse(TEXT("Late old finale cannot finish new attempt"), F.Stage->SubmitForestFinaleCompletion(Final));
		TestFalse(TEXT("Old final identity invalid"), F.Director->IsResolvedTokenCurrent(Final));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActReentryTest,
	"DengYingShanHai.ThreeAct.InvalidationReentryAndDestroy", DYActSequenceTests::Flags)
bool FDYActReentryTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F(true, false);
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	FGuid New;
	int32 Calls = 0;
	const FDelegateHandle Handle = F.Director->OnResolvedSnapshotInvalidated().AddLambda([&](const FGuid& Old)
	{
		++Calls;
		TestFalse(TEXT("Old callback permission revoked before listeners"), F.Advance(Old));
		F.Director->ResetCurrentPuzzle();
		New = F.Resolve();
	});
	F.Stage->DispatchBeginPlay(); // Listener precedes Stage; late old notice must not overwrite the new session.
	const FGuid Old = F.Resolve();
	TestFalse(TEXT("Outer transition abandons work after reset reentry"), F.Advance(Old));
	F.Director->OnResolvedSnapshotInvalidated().Remove(Handle);
	TestEqual(TEXT("One genuine old invalidation"), Calls, 1);
	TestEqual(TEXT("Reentry does not silently advance current act"), F.Index(), 0);
	TestTrue(TEXT("New success survives stale outer transition"), New.IsValid() && New != Old && F.Director->IsResolvedTokenCurrent(New));
	TestEqual(TEXT("New display snapshot survives late notice"), F.Stage->GetPlayerActDisplay().Phase, EDYActSequencePhase::AwaitingTransition);
	TestTrue(TEXT("Current identity can subsequently advance"), F.Advance(New));
	const FGuid DestroyedToken = F.Resolve();
	const FDelegateHandle DestroyHandle = F.Director->OnResolvedSnapshotInvalidated().AddLambda([&](const FGuid&)
	{
		F.Director->Destroy();
		F.Director->StartCurrentPuzzle();
		F.Director->ResetCurrentPuzzle();
		F.Director->EvaluatePuzzleNow();
	});
	TestFalse(TEXT("Destroyed callback aborts outer advancement"), F.Advance(DestroyedToken));
	F.Director->OnResolvedSnapshotInvalidated().Remove(DestroyHandle);
	TestFalse(TEXT("Destroyed Director cannot resurrect success"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	TestFalse(TEXT("Destroyed identity cannot advance again"), F.Advance(DestroyedToken));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActStaffGateTest,
	"DengYingShanHai.ThreeAct.NonFinalStaffCaptureGate", DYActSequenceTests::Flags)
bool FDYActStaffGateTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	for (int32 Act = 0; Act < 2; ++Act)
	{
		const FGuid Token = F.Resolve();
		TestTrue(TEXT("Earlier act really resolved"), F.Director->IsResolvedTokenCurrent(Token));
		TestFalse(TEXT("Earlier act never captures staff even with all references"), F.Stage->GetResolvedStaffPresentationSnapshot().bHasSnapshot);
		TestFalse(TEXT("Earlier act has no accepted contact"), F.Stage->GetStaffContactPresentationSnapshot().bHasContact);
		TestFalse(TEXT("Earlier identity cannot accept contact"), F.Stage->TryAcceptStaffContact(Token));
		TestFalse(TEXT("Earlier act cannot start forest"), F.Stage->BeginForestPresentation(Token));
		TestFalse(TEXT("Earlier act has no cosmetic resources"), F.Forest->HasForestSession());
		if (!TestTrue(TEXT("Advance real earlier identity"), F.Advance(Token))) { return false; }
	}
	const FGuid Token = F.Resolve();
	const auto Snapshot = F.Stage->GetResolvedStaffPresentationSnapshot();
	TestTrue(TEXT("Final real event captures staff"), Snapshot.bHasSnapshot && Snapshot.Token == Token);
	TestTrue(TEXT("Actual final geometry captured"), Snapshot.Projection.bHasGeometry && Snapshot.GroundLine.bIsValid);
	TestTrue(TEXT("No invented final contact"), !F.Stage->GetStaffContactPresentationSnapshot().bHasContact);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActDisplayReentryTest,
	"DengYingShanHai.ThreeAct.EarlierPhaseObserverResetPreservesLatestDisplay", DYActSequenceTests::Flags)
bool FDYActDisplayReentryTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F(true, false);
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	bool bResetOnce = false;
	const FDelegateHandle Handle = F.Director->OnActSequenceChanged().AddLambda([&](const FDYActSequenceSnapshot& S)
	{
		if (S.Phase == EDYActSequencePhase::AwaitingTransition && !bResetOnce)
		{
			bResetOnce = true;
			F.Director->ResetCurrentPuzzle();
		}
	});
	F.Stage->DispatchBeginPlay(); // The resetting observer receives the old multicast first.
	F.Resolve();
	F.Director->OnActSequenceChanged().Remove(Handle);
	TestTrue(TEXT("Real waiting notification caused reset"), bResetOnce);
	TestEqual(TEXT("Reentrant Director remains playing"), F.Phase(), EDYActSequencePhase::Playing);
	TestEqual(TEXT("Remaining stale notification cannot overwrite latest Stage display"),
		F.Stage->GetPlayerActDisplay().Phase, EDYActSequencePhase::Playing);
	TestFalse(TEXT("Outer Resolve stack did not recreate old success"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	TestEqual(TEXT("Reentrant entry baseline preserved"), F.Light->GetLightControlComponent()->GetNormalizedValue(), .15);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActSourceDestroyTest,
	"DengYingShanHai.ThreeAct.TransitionSourceDestroyedDuringInvalidation", DYActSequenceTests::Flags)
bool FDYActSourceDestroyTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.Ready())) { return false; }
	const FGuid Token = F.Resolve();
	const FDelegateHandle Handle = F.Director->OnResolvedSnapshotInvalidated().AddLambda([&](const FGuid&)
	{
		F.Stage->Destroy();
	});
	TestFalse(TEXT("Callback source destroyed during notification cannot advance"), F.Advance(Token));
	F.Director->OnResolvedSnapshotInvalidated().Remove(Handle);
	TestEqual(TEXT("Destroyed source cannot increment act index"), F.Index(), 0);
	TestFalse(TEXT("Consumed previous identity stays invalid"), F.Director->IsResolvedTokenCurrent(Token));
	TestFalse(TEXT("Dead source cannot submit old callback again"), F.Advance(Token));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActFinaleProofTest,
	"DengYingShanHai.ThreeAct.FinaleRequiresActualFullUntamperedForest", DYActSequenceTests::Flags)
bool FDYActFinaleProofTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F;
	if (!TestTrue(TEXT("Final fixture reachable through real successes"), F.Ready() && F.ReachFinal())) { return false; }
	const FGuid Token = F.Resolve();
	TestFalse(TEXT("Resolved identity without contact cannot finish"), F.Stage->SubmitForestFinaleCompletion(Token));
	if (!TestTrue(TEXT("Actual A contact accepted"), F.Contact())) { return false; }
	TestFalse(TEXT("Contact without resources cannot finish"), F.Stage->SubmitForestFinaleCompletion(Token));
	if (!TestTrue(TEXT("Native forest session begins"), F.Stage->BeginForestPresentation(Token))) { return false; }
	for (const double Progress : {.0, .75, .99})
	{
		TestTrue(TEXT("Native partial growth accepted"), F.Stage->SetForestNormalizedGrowth(Token, Progress));
		TestFalse(TEXT("Not all real branches full, completion denied"), F.Stage->SubmitForestFinaleCompletion(Token));
		TestTrue(TEXT("Denied cosmetic completion preserves success fact"), F.Director->IsResolvedTokenCurrent(Token));
	}
	TestTrue(TEXT("Final full growth applied"), F.Stage->SetForestNormalizedGrowth(Token, 1));
	TestTrue(TEXT("Actual full forest finishes"), F.Stage->SubmitForestFinaleCompletion(Token));
	for (int32 Case = 0; Case < 8; ++Case)
	{
		DYActSequenceTests::FFixture Tampered;
		if (!TestTrue(TEXT("Tamper fixture final ready"), Tampered.Ready() && Tampered.ReachFinal())) { return false; }
		const FGuid T = Tampered.Resolve();
		if (!TestTrue(TEXT("Tamper starts from genuine full forest"), Tampered.Grow(T, 1))) { return false; }
		const auto Components = Tampered.Forest->GetBranchMeshComponents();
		if (!TestTrue(TEXT("Two actual branch components exist"), Components.Num() == 2)) { return false; }
		switch (Case)
		{
		case 0: Components[1]->SetVisibility(false); break;
		case 1: Components[1]->DestroyComponent(); break;
		case 2: Components[1]->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"))); break;
		case 3: Components[1]->AddWorldOffset(FVector(0, 1, 0)); break;
		case 4: Components[1]->SetCastShadow(false); break;
		case 5: Tampered.Light->AddActorWorldOffset(FVector(0, 1, 0)); break;
		case 6: Tampered.Receiver->AddActorWorldOffset(FVector(0, 1, 0)); break;
		default: Tampered.Forest->SetActorHiddenInGame(true); break;
		}
		TestFalse(TEXT("Live geometry tamper cannot finish from stale valid sample"), Tampered.Stage->SubmitForestFinaleCompletion(T));
		TestEqual(TEXT("Tampered proof leaves experience awaiting finale"), Tampered.Phase(), EDYActSequencePhase::AwaitingFinale);
		TestTrue(TEXT("Presentation fault cannot revoke puzzle fact"), Tampered.Director->IsResolvedTokenCurrent(T));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActCompletionLifetimeTest,
	"DengYingShanHai.ThreeAct.CompletionRetentionAndEndPlay", DYActSequenceTests::Flags)
bool FDYActCompletionLifetimeTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F;
	if (!TestTrue(TEXT("Final fixture ready"), F.Ready() && F.ReachFinal())) { return false; }
	int32 CompletedNotifications = 0;
	const FDelegateHandle Handle = F.Director->OnActSequenceChanged().AddLambda([&](const FDYActSequenceSnapshot& S)
	{
		if (S.Phase == EDYActSequencePhase::Complete) { ++CompletedNotifications; }
	});
	const FGuid Token = F.Resolve();
	if (!TestTrue(TEXT("Full actual forest established"), F.Grow(Token, 1))) { F.Director->OnActSequenceChanged().Remove(Handle); return false; }
	const auto Components = F.Forest->GetBranchMeshComponents();
	TestTrue(TEXT("Native full proof completes once"), F.Stage->SubmitForestFinaleCompletion(Token));
	TestFalse(TEXT("Duplicate native completion rejected"), F.Stage->SubmitForestFinaleCompletion(Token));
	TestEqual(TEXT("One true complete notification"), CompletedNotifications, 1);
	TestTrue(TEXT("Complete keeps authoritative identity"), F.Director->IsResolvedTokenCurrent(Token));
	TestTrue(TEXT("Complete keeps contact and forest"), F.Stage->GetStaffContactPresentationSnapshot().bHasContact && F.Forest->HasForestSession());
	TestTrue(TEXT("Complete does not rebuild resources"), Components == F.Forest->GetBranchMeshComponents());
	F.Stage->SynchronizeFromDirector();
	TestEqual(TEXT("Late display synchronization shows real accepted ending"), F.Stage->GetPlayerActDisplay().Phase, EDYActSequencePhase::Complete);
	TestTrue(TEXT("Late sync does not restart or clear final geometry"), Components == F.Forest->GetBranchMeshComponents() && F.Forest->HasForestSession());
	TestFalse(TEXT("Late growth cannot rewind completed tableau"), F.Stage->SetForestNormalizedGrowth(Token, .5));
	TestFalse(TEXT("Late cosmetic clear cannot erase completed tableau"), F.Stage->ClearForestPresentation(Token));
	FDYControlContext Context;
	IDYControllable::Execute_ResetControlState(F.Puppet, Context);
	TestEqual(TEXT("Explicit current-act retry alone returns playing"), F.Phase(), EDYActSequencePhase::Playing);
	TestFalse(TEXT("Explicit retry invalidates old token"), F.Director->IsResolvedTokenCurrent(Token));
	TestFalse(TEXT("Explicit retry releases final resources"), F.Forest->HasForestSession());
	const FGuid Next = F.Resolve();
	if (!TestTrue(TEXT("Retried actual full forest established"), F.Grow(Next, 1))) { F.Director->OnActSequenceChanged().Remove(Handle); return false; }
	TestTrue(TEXT("Retry can complete a new attempt"), F.Stage->SubmitForestFinaleCompletion(Next));
	F.Director->OnActSequenceChanged().Remove(Handle);
	F.Director->Destroy();
	TestFalse(TEXT("Real Director EndPlay invalidates identity"), F.Director->IsResolvedTokenCurrent(Next));
	TestFalse(TEXT("Director teardown clears forest"), F.Forest->HasForestSession());
	TestFalse(TEXT("Late finale after EndPlay rejected"), F.Stage->SubmitForestFinaleCompletion(Next));
	TestFalse(TEXT("Late transition after EndPlay rejected"), F.Advance(Next));
	for (int32 Case = 0; Case < 2; ++Case)
	{
		DYActSequenceTests::FFixture Lost;
		if (!TestTrue(TEXT("Independent presentation teardown fixture ready"), Lost.Ready() && Lost.ReachFinal())) { return false; }
		const FGuid T = Lost.Resolve();
		if (!TestTrue(TEXT("Full forest before teardown"), Lost.Grow(T, 1))) { return false; }
		if (Case == 0) { Lost.Stage->Destroy(); } else { Lost.Forest->Destroy(); }
		TestFalse(TEXT("Missing live presentation resource cannot finish"), Lost.Stage->SubmitForestFinaleCompletion(T));
		TestEqual(TEXT("Cosmetic teardown leaves finale uncompleted"), Lost.Phase(), EDYActSequencePhase::AwaitingFinale);
		TestTrue(TEXT("Cosmetic teardown preserves independent puzzle success"), Lost.Director->IsResolvedTokenCurrent(T));
	}
	return true;
}

namespace DYActSequenceTests
{
	class FDeferredDependencyCommand final : public IAutomationLatentCommand
	{
	public:
		explicit FDeferredDependencyCommand(FAutomationTestBase* InTest)
			: Test(InTest), Fixture(MakeShared<FFixture>(true, true, false)) {}
		virtual bool Update() override
		{
			if (!Fixture->Ready()) { Test->AddError(TEXT("Deferred dependency fixture unavailable")); return true; }
			if (Step == 0)
			{
				Test->TestEqual(TEXT("Director first remains inactive until dependencies BeginPlay"), Fixture->Phase(), EDYActSequencePhase::Inactive);
				Test->TestTrue(TEXT("Director first did not move light before rail initialization"), Fixture->Light->GetActorLocation().Equals(FVector(-460, -20, 310)));
				Test->TestTrue(TEXT("Director first did not move puppet before rail initialization"), Fixture->Puppet->GetActorLocation().Equals(FVector(600, -80, 210)));
				Fixture->Light->DispatchBeginPlay();
				Fixture->Puppet->DispatchBeginPlay();
				Fixture->World->Tick(LEVELTICK_All, .01f);
				++Step;
				return false;
			}
			Fixture->World->Tick(LEVELTICK_All, .01f);
			Test->TestEqual(TEXT("Single native next-tick retry activates first act"), Fixture->Index(), 0);
			Test->TestEqual(TEXT("Deferred dependency activation becomes playing"), Fixture->Phase(), EDYActSequencePhase::Playing);
			FVector Start, End;
			Fixture->Light->GetLightControlComponent()->GetRailWorldEndpoints(Start, End);
			Test->TestTrue(TEXT("Light rail centre remains original author placement"), ((Start + End) * .5).Equals(FVector(-460, -20, 310), UE_DOUBLE_SMALL_NUMBER));
			Fixture->Puppet->GetPuppetControlComponent()->GetRailWorldEndpoints(Start, End);
			Test->TestTrue(TEXT("Puppet rail centre remains original author placement"), ((Start + End) * .5).Equals(FVector(600, -80, 210), UE_DOUBLE_SMALL_NUMBER));
			Test->TestEqual(TEXT("No doubled light baseline offset"), Fixture->Light->GetLightControlComponent()->GetNormalizedValue(), .15);
			Test->TestEqual(TEXT("No doubled puppet baseline offset"), Fixture->Puppet->GetPuppetControlComponent()->GetNormalizedValue(), .15);
			return true;
		}
	private:
		FAutomationTestBase* Test;
		TSharedPtr<FFixture> Fixture;
		int32 Step = 0;
	};

	/** TimerManager skips duplicate GFrameCounter ticks. Use actual framework frames,
	 * not a synchronous loop or a test write to the engine's global frame counter.
	 */
	class FNativeTransitionTimerCommand final : public IAutomationLatentCommand
	{
	public:
		explicit FNativeTransitionTimerCommand(FAutomationTestBase* InTest)
			: Test(InTest), Fixture(MakeShared<FFixture>()) {}
		virtual bool Update() override
		{
			if (!Fixture->Ready()) { Test->AddError(TEXT("Native timer fixture unavailable")); return true; }
			if (Step == 0)
			{
				OldToken = Fixture->Resolve();
				Test->TestTrue(TEXT("Timer starts from actual success"), OldToken.IsValid());
				Fixture->World->Tick(LEVELTICK_All, .01f); // Commit newly pending timers.
				++Step;
				return false;
			}
			if (Step == 1)
			{
				// UWorld clamps large requested DeltaSeconds. Small per-framework-frame
				// steps test the REAL timer instead of pretending that a 1.9s tick elapsed.
				Fixture->World->Tick(LEVELTICK_All, .1f);
				if (++ElapsedFrames < 19) { return false; }
				Test->TestEqual(TEXT("Before two seconds remains first act"), Fixture->Index(), 0);
				Test->TestEqual(TEXT("Before two seconds still awaits transition"), Fixture->Phase(), EDYActSequencePhase::AwaitingTransition);
				++Step;
				return false;
			}
			Fixture->World->Tick(LEVELTICK_All, .1f);
			if (++ElapsedFrames < 21) { return false; }
			Test->TestEqual(TEXT("Native approved timer advances once"), Fixture->Index(), 1);
			Test->TestEqual(TEXT("Native timer starts next act playing"), Fixture->Phase(), EDYActSequencePhase::Playing);
			Test->TestFalse(TEXT("Native timer invalidates previous token"), Fixture->Director->IsResolvedTokenCurrent(OldToken));
			Test->TestEqual(TEXT("Native timer resets light entry baseline"), Fixture->Light->GetLightControlComponent()->GetNormalizedValue(), .15);
			Test->TestEqual(TEXT("Native timer resets puppet entry baseline"), Fixture->Puppet->GetPuppetControlComponent()->GetNormalizedValue(), .15);
			return true;
		}
	private:
		FAutomationTestBase* Test;
		TSharedPtr<FFixture> Fixture;
		FGuid OldToken;
		int32 Step = 0;
		int32 ElapsedFrames = 0;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActDeferredDependencyTest,
	"DengYingShanHai.ThreeAct.DirectorFirstBeginPlayKeepsRailCentres", DYActSequenceTests::Flags)
bool FDYActDeferredDependencyTest::RunTest(const FString& Parameters)
{
	FAutomationTestFramework::Get().EnqueueLatentCommand(MakeShared<DYActSequenceTests::FDeferredDependencyCommand>(this));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActNativeTimerTest,
	"DengYingShanHai.ThreeAct.NativeTwoSecondTransitionTimer", DYActSequenceTests::Flags)
bool FDYActNativeTimerTest::RunTest(const FString& Parameters)
{
	FAutomationTestFramework::Get().EnqueueLatentCommand(MakeShared<DYActSequenceTests::FNativeTransitionTimerCommand>(this));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActHudStatusTest,
	"DengYingShanHai.ThreeAct.PassiveHudStatusContract", DYActSequenceTests::Flags)
bool FDYActHudStatusTest::RunTest(const FString& Parameters)
{
	FDYActSequenceSnapshot Snapshot;
	TestEqual(TEXT("Legacy status unchanged"), UDYInteractionHUDWidget::GetActStatusText(Snapshot, EDYStageFeedbackDisplay::Complete).ToString(),
		UDYInteractionHUDWidget::GetStatusText(EDYStageFeedbackDisplay::Complete).ToString());
	Snapshot.bSequenceEnabled = true;
	Snapshot.Phase = EDYActSequencePhase::AwaitingTransition;
	TestEqual(TEXT("Transition explains next adjustment"), UDYInteractionHUDWidget::GetActStatusText(Snapshot, EDYStageFeedbackDisplay::Complete).ToString(),
		FString(TEXT("本幕已成 · 下幕请重新调整灯与皮影")));
	Snapshot.Phase = EDYActSequencePhase::AwaitingFinale;
	TestEqual(TEXT("Resolve is not prematurely called finished"), UDYInteractionHUDWidget::GetActStatusText(Snapshot, EDYStageFeedbackDisplay::Complete).ToString(),
		FString(TEXT("影形已合，静待杖落成林")));
	Snapshot.Phase = EDYActSequencePhase::Complete;
	TestEqual(TEXT("Only accepted finale announces ending"), UDYInteractionHUDWidget::GetActStatusText(Snapshot, EDYStageFeedbackDisplay::Complete).ToString(), FString(TEXT("复演已成")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActHudReentryTest,
	"DengYingShanHai.ThreeAct.PassiveHudMulticastReentryAndDetach", DYActSequenceTests::Flags)
bool FDYActHudReentryTest::RunTest(const FString& Parameters)
{
	for (int32 Case = 0; Case < 2; ++Case)
	{
		DYActSequenceTests::FFixture F;
		if (!TestTrue(TEXT("HUD reentry fixture ready"), F.Ready())) { return false; }
		ADYInteractionHUD* Hud = F.World->SpawnActor<ADYInteractionHUD>();
		if (!TestNotNull(TEXT("Real passive HUD adapter exists"), Hud)) { return false; }
		bool bResetOnce = false;
		FDelegateHandle ActHandle, FeedbackHandle;
		if (Case == 0)
		{
			ActHandle = F.Stage->OnPlayerActDisplayChanged().AddLambda([&](const FDYActSequenceSnapshot& S)
			{
				if (!bResetOnce && S.Phase == EDYActSequencePhase::AwaitingTransition)
				{
					bResetOnce = true;
					F.Director->ResetCurrentPuzzle();
				}
			});
		}
		else
		{
			FeedbackHandle = F.Stage->OnPlayerFeedbackDisplayChanged().AddLambda([&](EDYStageFeedbackDisplay Display)
			{
				if (!bResetOnce && Display == EDYStageFeedbackDisplay::Complete)
				{
					bResetOnce = true;
					F.Director->ResetCurrentPuzzle();
				}
			});
		}
		FDYActSequenceTestSeam::AttachHud(*Hud, F.Stage); // Resetting observer is earlier in the same multicast.
		TestEqual(TEXT("Late attach reads current title"), FDYActSequenceTestSeam::HudAct(*Hud).ActIndex, 0);
		F.Resolve();
		TestTrue(TEXT("Actual success notification caused one reset"), bResetOnce);
		TestEqual(TEXT("Actual Director remains playing"), F.Phase(), EDYActSequencePhase::Playing);
		TestEqual(TEXT("Old Stage payload cannot overwrite HUD phase"), FDYActSequenceTestSeam::HudAct(*Hud).Phase, EDYActSequencePhase::Playing);
		TestEqual(TEXT("HUD uses latest feedback getter"), FDYActSequenceTestSeam::HudFeedback(*Hud), F.Stage->GetPlayerFeedbackDisplay());
		TestFalse(TEXT("Newly reset act is not falsely displayed complete"), FDYActSequenceTestSeam::HudFeedback(*Hud) == EDYStageFeedbackDisplay::Complete);
		F.Stage->OnPlayerActDisplayChanged().Remove(ActHandle);
		F.Stage->OnPlayerFeedbackDisplayChanged().Remove(FeedbackHandle);
		FDYActSequenceTestSeam::AttachHud(*Hud, nullptr);
		TestFalse(TEXT("Detach clears sequence display"), FDYActSequenceTestSeam::HudAct(*Hud).bSequenceEnabled);
		F.Resolve();
		TestFalse(TEXT("Old publisher cannot refill detached HUD"), FDYActSequenceTestSeam::HudAct(*Hud).bSequenceEnabled);
		TestEqual(TEXT("Detached feedback stays hidden"), FDYActSequenceTestSeam::HudFeedback(*Hud), EDYStageFeedbackDisplay::Hidden);
	}
	return true;
}

namespace DYActSequenceTests
{
	class FReadyStartSupersedesDeferredCommand final : public IAutomationLatentCommand
	{
	public:
		explicit FReadyStartSupersedesDeferredCommand(FAutomationTestBase* InTest)
			: Test(InTest), Fixture(MakeShared<FFixture>(true, true, false)) {}
		virtual bool Update() override
		{
			if (!Fixture->Ready()) { Test->AddError(TEXT("Manual ready start fixture unavailable")); return true; }
			if (Step == 0)
			{
				Fixture->Light->DispatchBeginPlay();
				Fixture->Puppet->DispatchBeginPlay();
				Fixture->Director->StartCurrentPuzzle();
				Token = Fixture->Resolve();
				Test->TestTrue(TEXT("Explicit ready start really resolved"), Token.IsValid());
				Fixture->World->Tick(LEVELTICK_All, .01f);
				++Step;
				return false;
			}
			Fixture->World->Tick(LEVELTICK_All, .01f);
			Test->TestTrue(TEXT("Canceled old initial callback cannot reset a newer success"), Fixture->Director->IsResolvedTokenCurrent(Token));
			Test->TestEqual(TEXT("No duplicate activation after explicit start"), Fixture->Phase(), EDYActSequencePhase::AwaitingTransition);
			return true;
		}
	private:
		FAutomationTestBase* Test;
		TSharedPtr<FFixture> Fixture;
		FGuid Token;
		int32 Step = 0;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActManualReadyStartTest,
	"DengYingShanHai.ThreeAct.ReadyStartCancelsDeferredActivation", DYActSequenceTests::Flags)
bool FDYActManualReadyStartTest::RunTest(const FString& Parameters)
{
	FAutomationTestFramework::Get().EnqueueLatentCommand(MakeShared<DYActSequenceTests::FReadyStartSupersedesDeferredCommand>(this));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYActOldEvaluationTest,
	"DengYingShanHai.ThreeAct.StaleEvaluationNotificationRejectedAfterReset", DYActSequenceTests::Flags)
bool FDYActOldEvaluationTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F;
	if (!TestTrue(TEXT("Stale notification fixture ready"), F.Ready())) { return false; }
	bool bDeliveredRealOldResult = false;
	const FDelegateHandle Handle = F.Director->OnActSequenceChanged().AddLambda([&](const FDYActSequenceSnapshot& S)
	{
		if (S.Phase != EDYActSequencePhase::AwaitingTransition || bDeliveredRealOldResult) { return; }
		const FDYEvaluationResult OldResult = F.Director->GetLastEvaluation(); // Genuine outer Resolve, not a fabricated result.
		bDeliveredRealOldResult = true;
		F.Director->ResetCurrentPuzzle();
		// Emulate a remaining Stage receiver of the old notification stack. The
		// native provenance is still the actual outer activation, not the new one.
		FDYActSequenceTestSeam::DeliverEvaluation(*F.Stage, OldResult);
	});
	F.Resolve();
	F.Director->OnActSequenceChanged().Remove(Handle);
	TestTrue(TEXT("Actual old evaluator result was delivered after reset"), bDeliveredRealOldResult);
	TestEqual(TEXT("Current activation remains playing"), F.Phase(), EDYActSequencePhase::Playing);
	TestFalse(TEXT("Old notification cannot restore success feedback"), F.Stage->GetPlayerFeedbackDisplay() == EDYStageFeedbackDisplay::Complete);
	TestFalse(TEXT("Old notification cannot synthesize a resolved fact"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEnvironmentSequenceMapTest,
	"DengYingShanHai.EnvironmentDev.PureFiveStateMapValidAndMalformed", DYActSequenceTests::Flags)
bool FDYEnvironmentSequenceMapTest::RunTest(const FString& Parameters)
{
	// Fabricated VALUE snapshots exercise the pure mapping only. These never enter
	// a Director, Presentation event, runtime phase or accepted completion path.
	struct FMapCase { EDYActSequencePhase Phase; int32 Index; EDYStageEnvironmentState Expected; };
	const FMapCase Cases[] = {
		{EDYActSequencePhase::Inactive, INDEX_NONE, EDYStageEnvironmentState::Dormant},
		{EDYActSequencePhase::Inactive, 0, EDYStageEnvironmentState::Dormant},
		{EDYActSequencePhase::Playing, 0, EDYStageEnvironmentState::Dormant},
		{EDYActSequencePhase::Playing, 1, EDYStageEnvironmentState::SunAwakened},
		{EDYActSequencePhase::Playing, 2, EDYStageEnvironmentState::ChaseAwakened},
		{EDYActSequencePhase::AwaitingTransition, 0, EDYStageEnvironmentState::SunAwakened},
		{EDYActSequencePhase::AwaitingTransition, 1, EDYStageEnvironmentState::ChaseAwakened},
		{EDYActSequencePhase::AwaitingFinale, 2, EDYStageEnvironmentState::FinaleReady},
		{EDYActSequencePhase::Complete, 2, EDYStageEnvironmentState::ForestComplete},
		{EDYActSequencePhase::AwaitingTransition, 2, EDYStageEnvironmentState::Dormant},
		{EDYActSequencePhase::AwaitingFinale, 0, EDYStageEnvironmentState::Dormant},
		{EDYActSequencePhase::AwaitingFinale, 1, EDYStageEnvironmentState::Dormant},
		{EDYActSequencePhase::Complete, 0, EDYStageEnvironmentState::Dormant},
		{EDYActSequencePhase::Complete, 1, EDYStageEnvironmentState::Dormant},
		{static_cast<EDYActSequencePhase>(255), 2, EDYStageEnvironmentState::Dormant}
	};
	for (const FMapCase& Case : Cases)
	{
		FDYActSequenceSnapshot S;
		S.bSequenceEnabled = true;
		S.ActCount = 3;
		S.ActIndex = Case.Index;
		S.Phase = Case.Phase;
		TestEqual(FString::Printf(TEXT("Pure phase %d index %d"), static_cast<int32>(Case.Phase), Case.Index),
			ADYStagePresentation::MapSequenceToEnvironment(S), Case.Expected);
		S.bSequenceEnabled = false;
		TestEqual(TEXT("Disabled sequence fails to Dormant for every phase"),
			ADYStagePresentation::MapSequenceToEnvironment(S), EDYStageEnvironmentState::Dormant);
	}
	for (const int32 Count : {-1, 0, 1, 2, 4})
	{
		FDYActSequenceSnapshot S;
		S.bSequenceEnabled = true;
		S.ActCount = Count;
		S.ActIndex = 2;
		S.Phase = EDYActSequencePhase::Complete;
		TestEqual(TEXT("Malformed three-act count never claims a completed forest"),
			ADYStagePresentation::MapSequenceToEnvironment(S), EDYStageEnvironmentState::Dormant);
	}
	for (const int32 Index : {-2, -1, 3, 99})
	{
		for (const EDYActSequencePhase Phase : {EDYActSequencePhase::Playing, EDYActSequencePhase::AwaitingTransition,
			EDYActSequencePhase::AwaitingFinale, EDYActSequencePhase::Complete})
		{
			FDYActSequenceSnapshot S;
			S.bSequenceEnabled = true;
			S.ActCount = 3;
			S.ActIndex = Index;
			S.Phase = Phase;
			TestEqual(TEXT("Malformed active index fails to Dormant"),
				ADYStagePresentation::MapSequenceToEnvironment(S), EDYStageEnvironmentState::Dormant);
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEnvironmentProfilesTest,
	"DengYingShanHai.EnvironmentDev.DefaultOptInEnumAndPassiveAccentProfiles", DYActSequenceTests::Flags)
bool FDYEnvironmentProfilesTest::RunTest(const FString& Parameters)
{
	const ADYStagePresentation* Defaults = GetDefault<ADYStagePresentation>();
	const ADYStageEnvironment* EnvironmentDefaults = GetDefault<ADYStageEnvironment>();
	if (!TestNotNull(TEXT("Presentation CDO exists"), Defaults)
		|| !TestNotNull(TEXT("Environment CDO exists"), EnvironmentDefaults)) { return false; }
	TestFalse(TEXT("Five-state Dev adapter is opt-in, not an old-map migration"), Defaults->IsFiveStateEnvironmentEnabled());
	TestFalse(TEXT("Presentation has no per-frame polling"), Defaults->PrimaryActorTick.bCanEverTick);
	TestFalse(TEXT("Environment has no per-frame polling"), EnvironmentDefaults->PrimaryActorTick.bCanEverTick);
	TestEqual(TEXT("Old Dormant numeric value preserved"), static_cast<uint8>(EDYStageEnvironmentState::Dormant), uint8(0));
	TestEqual(TEXT("Old Sun numeric value preserved"), static_cast<uint8>(EDYStageEnvironmentState::SunAwakened), uint8(1));
	TestEqual(TEXT("Old Chase numeric value preserved"), static_cast<uint8>(EDYStageEnvironmentState::ChaseAwakened), uint8(2));
	TestEqual(TEXT("FinaleReady appended, not inserted"), static_cast<uint8>(EDYStageEnvironmentState::FinaleReady), uint8(3));
	TestEqual(TEXT("ForestComplete appended, not inserted"), static_cast<uint8>(EDYStageEnvironmentState::ForestComplete), uint8(4));
	DYActSequenceTests::FFixture F;
	if (!TestTrue(TEXT("Independent native accent fixture ready"), F.Ready())) { return false; }
	UPointLightComponent* Sun = F.Environment->GetSunAwakenedAccent();
	UPointLightComponent* Wing = F.Environment->GetChaseAwakenedAccent();
	if (!TestNotNull(TEXT("Existing sun accent"), Sun) || !TestNotNull(TEXT("Existing wing accent"), Wing)) { return false; }
	const FVector LightLocation = F.Light->GetActorLocation();
	const double LightParameter = F.Light->GetLightControlComponent()->GetNormalizedValue();
	struct FProfileCase { EDYStageEnvironmentState State; float Sun; float Wing; };
	const FProfileCase Cases[] = {
		{EDYStageEnvironmentState::Dormant, 0.0f, 0.0f},
		{EDYStageEnvironmentState::SunAwakened, 5000.0f, 0.0f},
		{EDYStageEnvironmentState::ChaseAwakened, 3500.0f, 4500.0f},
		{EDYStageEnvironmentState::FinaleReady, 1750.0f, 1125.0f},
		{EDYStageEnvironmentState::ForestComplete, 5000.0f, 4500.0f}
	};
	for (const FProfileCase& Case : Cases)
	{
		// Direct ApplyState tests cosmetic profiles only, not narrative authority.
		F.Environment->ApplyState(Case.State);
		TestEqual(TEXT("Requested profile current state"), F.Environment->GetCurrentState(), Case.State);
		TestEqual(TEXT("Exact sun accent intensity"), Sun->Intensity, Case.Sun);
		TestEqual(TEXT("Exact wing accent intensity"), Wing->Intensity, Case.Wing);
		Sun->SetIntensity(1.0f);
		Wing->SetIntensity(1.0f);
		F.Environment->ApplyState(Case.State);
		TestEqual(TEXT("Same-state application reapplies cosmetic sun profile"), Sun->Intensity, Case.Sun);
		TestEqual(TEXT("Same-state application reapplies cosmetic wing profile"), Wing->Intensity, Case.Wing);
		TestEqual(TEXT("Cosmetic application cannot advance Director"), F.Phase(), EDYActSequencePhase::Playing);
		TestEqual(TEXT("Cosmetic application cannot change act"), F.Index(), 0);
		TestTrue(TEXT("Cosmetic accent never moves controllable lamp"), F.Light->GetActorLocation().Equals(LightLocation));
		TestEqual(TEXT("Cosmetic accent never changes controllable lamp parameter"),
			F.Light->GetLightControlComponent()->GetNormalizedValue(), LightParameter);
	}
	TestFalse(TEXT("Existing sun accent never casts a competing shadow"), Sun->CastShadows);
	TestFalse(TEXT("Existing wing accent never casts a competing shadow"), Wing->CastShadows);
	F.Environment->ResetToDormant();
	TestEqual(TEXT("Explicit cosmetic reset goes Dormant"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::Dormant);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEnvironmentActualFlowTest,
	"DengYingShanHai.EnvironmentDev.RealFiveStateFlowContactGrowthAndLateSync", DYActSequenceTests::Flags)
bool FDYEnvironmentActualFlowTest::RunTest(const FString& Parameters)
{
	{
		DYActSequenceTests::FFixture F(true, false);
		if (!TestTrue(TEXT("Real five-state fixture ready"), F.Ready())) { return false; }
		FDYActSequenceTestSeam::SetFiveStateDev(*F.Stage);
		F.Stage->DispatchBeginPlay();
		TestTrue(TEXT("Authoring opt-in exposed read-only"), F.Stage->IsFiveStateEnvironmentEnabled());
		TestEqual(TEXT("Actual first Playing state stays Dormant"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::Dormant);
		for (int32 Act = 0; Act < 2; ++Act)
		{
			const FGuid Token = F.Resolve();
			if (!TestTrue(TEXT("Evaluator supplied real earlier success"), F.Director->IsResolvedTokenCurrent(Token))) { return false; }
			const auto Expected = Act == 0 ? EDYStageEnvironmentState::SunAwakened : EDYStageEnvironmentState::ChaseAwakened;
			TestEqual(TEXT("Real earlier resolve advances cosmetic state"), F.Environment->GetCurrentState(), Expected);
			if (!TestTrue(TEXT("Real earlier identity advances one act"), F.Advance(Token))) { return false; }
			TestEqual(TEXT("Next Playing state keeps already earned environment"), F.Environment->GetCurrentState(), Expected);
		}
		const FGuid Final = F.Resolve();
		TestTrue(TEXT("Final evaluator identity valid"), F.Director->IsResolvedTokenCurrent(Final));
		TestEqual(TEXT("Resolve is FinaleReady, never ForestComplete"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::FinaleReady);
		TestFalse(TEXT("Resolve alone cannot submit a forest"), F.Stage->SubmitForestFinaleCompletion(Final));
		if (!TestTrue(TEXT("Actual A endpoint reaches test-only ground line"), F.Contact())) { return false; }
		TestEqual(TEXT("Accepted contact still FinaleReady"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::FinaleReady);
		TestFalse(TEXT("Contact alone cannot announce complete environment"), F.Stage->SubmitForestFinaleCompletion(Final));
		if (!TestTrue(TEXT("Native forest geometry starts"), F.Stage->BeginForestPresentation(Final))) { return false; }
		for (const double Progress : {.0, .75, .99})
		{
			TestTrue(TEXT("Partial geometry growth accepted"), F.Stage->SetForestNormalizedGrowth(Final, Progress));
			TestFalse(TEXT("Partial geometry cannot accept finale"), F.Stage->SubmitForestFinaleCompletion(Final));
			TestEqual(TEXT("Partial geometry keeps FinaleReady"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::FinaleReady);
		}
		TestTrue(TEXT("Actual full branch transforms applied"), F.Stage->SetForestNormalizedGrowth(Final, 1));
		TestEqual(TEXT("Even full growth awaits accepted finale proof"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::FinaleReady);
		const auto Components = F.Forest->GetBranchMeshComponents();
		if (!TestTrue(TEXT("Actual full untampered proof is accepted"), F.Stage->SubmitForestFinaleCompletion(Final))) { return false; }
		TestEqual(TEXT("Authoritative phase now Complete"), F.Phase(), EDYActSequencePhase::Complete);
		TestEqual(TEXT("Only accepted proof establishes ForestComplete"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::ForestComplete);
		TestFalse(TEXT("Repeated completion cannot run twice"), F.Stage->SubmitForestFinaleCompletion(Final));
		for (int32 Sync = 0; Sync < 3; ++Sync) { F.Stage->SynchronizeFromDirector(); }
		TestEqual(TEXT("Late display sync cannot downgrade completed environment"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::ForestComplete);
		TestTrue(TEXT("Late sync neither rebuilds nor clears forest"), Components == F.Forest->GetBranchMeshComponents() && F.Forest->HasForestSession());
		F.Stage->Destroy();
		TestFalse(TEXT("Destroyed Presentation cannot submit accepted proof again"), F.Stage->SubmitForestFinaleCompletion(Final));
	}
	DYActSequenceTests::FFixture Fresh(true, false);
	if (!TestTrue(TEXT("Fresh independent world after completed-world teardown"), Fresh.Ready())) { return false; }
	FDYActSequenceTestSeam::SetFiveStateDev(*Fresh.Stage);
	Fresh.Stage->DispatchBeginPlay();
	TestEqual(TEXT("New world starts Dormant without previous forest state"), Fresh.Environment->GetCurrentState(), EDYStageEnvironmentState::Dormant);
	TestFalse(TEXT("New world inherits no completed forest session"), Fresh.Forest->HasForestSession());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEnvironmentRejectedProofTest,
	"DengYingShanHai.EnvironmentDev.RejectedTokensAndLiveGeometryNeverPromote", DYActSequenceTests::Flags)
bool FDYEnvironmentRejectedProofTest::RunTest(const FString& Parameters)
{
	for (int32 Case = 0; Case < 8; ++Case)
	{
		DYActSequenceTests::FFixture F(true, false);
		if (!TestTrue(TEXT("Independent tamper fixture ready"), F.Ready())) { return false; }
		FDYActSequenceTestSeam::SetFiveStateDev(*F.Stage);
		F.Stage->DispatchBeginPlay();
		const FGuid Old = F.Resolve();
		if (!TestTrue(TEXT("Real P01 transition accepted"), F.Advance(Old))
			|| !TestTrue(TEXT("Real P02 transition accepted"), F.Advance(F.Resolve()))) { return false; }
		const FGuid Final = F.Resolve();
		for (const FGuid& Invalid : {FGuid(), FGuid::NewGuid(), Old})
		{
			TestFalse(TEXT("Empty random or old identity cannot finish environment"), F.Stage->SubmitForestFinaleCompletion(Invalid));
			TestEqual(TEXT("Rejected identity leaves current environment FinaleReady"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::FinaleReady);
		}
		if (!TestTrue(TEXT("Tamper probe begins from genuine full geometry"), F.Grow(Final, 1))) { return false; }
		const auto Components = F.Forest->GetBranchMeshComponents();
		if (!TestTrue(TEXT("Actual fixture branches present"), Components.Num() == 2)) { return false; }
		switch (Case)
		{
		case 0: Components[1]->SetVisibility(false); break;
		case 1: Components[1]->DestroyComponent(); break;
		case 2: Components[1]->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"))); break;
		case 3: Components[1]->AddWorldOffset(FVector(0, 1, 0)); break;
		case 4: Components[1]->SetCastShadow(false); break;
		case 5: F.Light->AddActorWorldOffset(FVector(0, 1, 0)); break;
		case 6: F.Receiver->AddActorWorldOffset(FVector(0, 1, 0)); break;
		default: F.Forest->SetActorHiddenInGame(true); break;
		}
		TestFalse(TEXT("Live geometry tamper prevents accepted finale proof"), F.Stage->SubmitForestFinaleCompletion(Final));
		TestEqual(TEXT("Tampered forest cannot promote cosmetic environment"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::FinaleReady);
		TestEqual(TEXT("Tampered forest cannot advance authoritative phase"), F.Phase(), EDYActSequencePhase::AwaitingFinale);
		TestTrue(TEXT("Cosmetic failure does not revoke real puzzle success"), F.Director->IsResolvedTokenCurrent(Final));
		F.Stage->SynchronizeFromDirector();
		TestEqual(TEXT("Sync cannot manufacture missing proof"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::FinaleReady);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEnvironmentThirdActResetTest,
	"DengYingShanHai.EnvironmentDev.ThirdActResetRestoresChaseAndRejectsLateFinale", DYActSequenceTests::Flags)
bool FDYEnvironmentThirdActResetTest::RunTest(const FString& Parameters)
{
	for (int32 Case = 0; Case < 3; ++Case)
	{
		DYActSequenceTests::FFixture F(true, false);
		if (!TestTrue(TEXT("Independent reset fixture ready"), F.Ready())) { return false; }
		FDYActSequenceTestSeam::SetFiveStateDev(*F.Stage);
		F.Stage->DispatchBeginPlay();
		if (!TestTrue(TEXT("Reached third act through real first two successes"), F.ReachFinal())) { return false; }
		const FGuid Old = F.Resolve();
		if (Case > 0 && !TestTrue(TEXT("Real forest established before reset"), F.Grow(Old, Case == 1 ? .75 : 1.0))) { return false; }
		if (Case == 2 && !TestTrue(TEXT("Genuine full forest accepted before reset"), F.Stage->SubmitForestFinaleCompletion(Old))) { return false; }
		TestEqual(TEXT("Before reset, environment matches actual authoritative phase"), F.Environment->GetCurrentState(),
			Case == 2 ? EDYStageEnvironmentState::ForestComplete : EDYStageEnvironmentState::FinaleReady);
		FDYControlContext Context;
		IDYControllable::Execute_ResetControlState(F.Puppet, Context);
		TestEqual(TEXT("Current reset keeps third-act index"), F.Index(), 2);
		TestEqual(TEXT("Current reset returns to real Playing"), F.Phase(), EDYActSequencePhase::Playing);
		TestEqual(TEXT("Third-act reset restores earned Chase, not Dormant or ForestComplete"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::ChaseAwakened);
		TestFalse(TEXT("Reset releases completed or partial forest resources"), F.Forest->HasForestSession());
		TestFalse(TEXT("Reset invalidates old identity"), F.Director->IsResolvedTokenCurrent(Old));
		TestFalse(TEXT("Late old contact rejected"), F.Stage->TryAcceptStaffContact(Old));
		TestFalse(TEXT("Late old growth rejected"), F.Stage->SetForestNormalizedGrowth(Old, 1));
		TestFalse(TEXT("Late old complete rejected"), F.Stage->SubmitForestFinaleCompletion(Old));
		F.Stage->SynchronizeFromDirector();
		TestEqual(TEXT("Post-reset synchronization keeps current Chase state"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::ChaseAwakened);
		const FGuid Next = F.Resolve();
		TestTrue(TEXT("New attempt receives a new authoritative token"), Next.IsValid() && Next != Old && F.Director->IsResolvedTokenCurrent(Next));
		TestEqual(TEXT("New real Resolve can return to FinaleReady"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::FinaleReady);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEnvironmentLegacyCompatibilityTest,
	"DengYingShanHai.EnvironmentDev.DefaultOffAndNonSequenceLegacyUnchanged", DYActSequenceTests::Flags)
bool FDYEnvironmentLegacyCompatibilityTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture OldSequence, Legacy(false), LegacyOptIn(false, false);
	if (!TestTrue(TEXT("Independent old and legacy fixtures ready"), OldSequence.Ready() && Legacy.Ready() && LegacyOptIn.Ready())) { return false; }
	TestFalse(TEXT("Old three-act Presentation keeps opt-in false"), OldSequence.Stage->IsFiveStateEnvironmentEnabled());
	if (!TestTrue(TEXT("Old three-act flow reaches final"), OldSequence.ReachFinal())) { return false; }
	const FGuid Final = OldSequence.Resolve();
	TestEqual(TEXT("Old final Resolve keeps pre-existing Chase profile"), OldSequence.Environment->GetCurrentState(), EDYStageEnvironmentState::ChaseAwakened);
	if (!TestTrue(TEXT("Old native full forest can still finish"), OldSequence.Grow(Final, 1)
		&& OldSequence.Stage->SubmitForestFinaleCompletion(Final))) { return false; }
	OldSequence.Stage->SynchronizeFromDirector();
	TestEqual(TEXT("Default-off accepted ending remains old Chase, not new ForestComplete"), OldSequence.Environment->GetCurrentState(), EDYStageEnvironmentState::ChaseAwakened);
	const FGuid LegacyToken = Legacy.Resolve();
	TestTrue(TEXT("Non-sequence legacy still really resolves"), Legacy.Director->IsResolvedTokenCurrent(LegacyToken));
	TestEqual(TEXT("Non-sequence resolved profile stays its authored legacy default"), Legacy.Environment->GetCurrentState(), Legacy.Stage->GetResolvedEnvironmentState());
	FDYActSequenceTestSeam::SetFiveStateDev(*LegacyOptIn.Stage);
	LegacyOptIn.Stage->DispatchBeginPlay();
	const FGuid OptInToken = LegacyOptIn.Resolve();
	TestFalse(TEXT("Five-state opt-in does not fabricate a missing sequence"), LegacyOptIn.Director->IsActSequenceEnabled());
	TestTrue(TEXT("Opt-in legacy evaluator identity remains genuine"), LegacyOptIn.Director->IsResolvedTokenCurrent(OptInToken));
	TestEqual(TEXT("Opt-in without sequence still uses legacy authored resolved state"), LegacyOptIn.Environment->GetCurrentState(), LegacyOptIn.Stage->GetResolvedEnvironmentState());
	TestFalse(TEXT("Legacy cannot submit a whole-experience ending"), LegacyOptIn.Stage->SubmitForestFinaleCompletion(OptInToken));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEnvironmentPhaseReentryTest,
	"DengYingShanHai.EnvironmentDev.ActDisplayReentryResetPreservesCurrentEnvironment", DYActSequenceTests::Flags)
bool FDYEnvironmentPhaseReentryTest::RunTest(const FString& Parameters)
{
	DYActSequenceTests::FFixture F(true, false);
	if (!TestTrue(TEXT("Real reentry fixture ready"), F.Ready())) { return false; }
	FDYActSequenceTestSeam::SetFiveStateDev(*F.Stage);
	F.Stage->DispatchBeginPlay();
	if (!TestTrue(TEXT("Real prior successes reach third act"), F.ReachFinal())) { return false; }
	bool bResetOnce = false;
	const FDelegateHandle Handle = F.Stage->OnPlayerActDisplayChanged().AddLambda([&](const FDYActSequenceSnapshot& S)
	{
		if (!bResetOnce && S.Phase == EDYActSequencePhase::AwaitingFinale)
		{
			bResetOnce = true;
			F.Director->ResetCurrentPuzzle();
		}
	});
	F.Resolve(); // Genuine evaluator success drives the real Stage display multicast.
	F.Stage->OnPlayerActDisplayChanged().Remove(Handle);
	TestTrue(TEXT("Actual AwaitingFinale display callback caused one reset"), bResetOnce);
	TestEqual(TEXT("Nested reset leaves authoritative phase Playing"), F.Phase(), EDYActSequencePhase::Playing);
	TestEqual(TEXT("Nested reset leaves display Playing"), F.Stage->GetPlayerActDisplay().Phase, EDYActSequencePhase::Playing);
	TestEqual(TEXT("Stale outer phase cannot overwrite nested Chase state"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::ChaseAwakened);
	TestFalse(TEXT("Stale outer success cannot recreate a current resolved identity"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	TestFalse(TEXT("Nested reset inherits no forest or contact"), F.Forest->HasForestSession() || F.Stage->GetStaffContactPresentationSnapshot().bHasContact);
	F.Stage->SynchronizeFromDirector();
	TestEqual(TEXT("Explicit late sync preserves the settled nested state"), F.Environment->GetCurrentState(), EDYStageEnvironmentState::ChaseAwakened);
	return true;
}

#endif
