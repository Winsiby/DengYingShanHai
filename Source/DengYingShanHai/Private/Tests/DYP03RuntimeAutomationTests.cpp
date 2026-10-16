#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Components/StaticMeshComponent.h"
#include "Components/TimelineComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Stage/DYForestPresentationActor.h"
#include "Stage/DYStagePresentation.h"
#include "UObject/UnrealType.h"

#if WITH_EDITOR
#include "Engine/StaticMeshActor.h"
#include "Misc/ScopeExit.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#endif

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYP03StageRuntimeContractTest,
	"DengYingShanHai.P03.Runtime.StageReadOnlyBoundary",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDYP03StageRuntimeContractTest::RunTest(const FString& Parameters)
{
	const UClass* Class = ADYStagePresentation::StaticClass();
	const UFunction* Getter = Class->FindFunctionByName(TEXT("GetForestPresentationActor"));
	const UFunction* Event = Class->FindFunctionByName(TEXT("ReceiveStaffPresentationInvalidated"));
	if (!TestNotNull(TEXT("Actual resource getter reflected"), Getter)
		|| !TestNotNull(TEXT("Invalidation event reflected"), Event)) { return false; }
	TestTrue(TEXT("Read-only constant BP getter"), Getter->HasAllFunctionFlags(FUNC_BlueprintPure | FUNC_Const));
	TestTrue(TEXT("Cosmetic Blueprint event"), Event->HasAllFunctionFlags(FUNC_BlueprintEvent | FUNC_Event));
	TestFalse(TEXT("Not a new callable invalidation authority"), Event->HasAnyFunctionFlags(FUNC_BlueprintCallable));
	TestFalse(TEXT("Getter has no default resource discovery"), GetDefault<ADYStagePresentation>()->GetForestPresentationActor() != nullptr);
	const FStructProperty* Token = FindFProperty<FStructProperty>(Event, TEXT("Token"));
	TestTrue(TEXT("Event carries the real typed identity"), Token && Token->Struct == TBaseStructure<FGuid>::Get());
	return true;
}

#if WITH_EDITOR
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYP03EngineMicroTransformObservationTest,
	"DengYingShanHai.P03.Runtime.EngineMicroTransformObservation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDYP03EngineMicroTransformObservationTest::RunTest(const FString& Parameters)
{
	// Isolated registered component only. Never writes a live Forest or advances a cue.
	if (!TestNotNull(TEXT("Engine available for isolated diagnostic"), GEngine)) { return false; }
	TStrongObjectPtr<UWorld> World(UWorld::CreateWorld(EWorldType::Game, false,
		MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYP03MicroTransformWorld")), GetTransientPackage()));
	if (!TestNotNull(TEXT("Independent transient world"), World.Get())) { return false; }
	GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World.Get());
	ON_SCOPE_EXIT
	{
		World->EndPlay(EEndPlayReason::Quit);
		GEngine->DestroyWorldContext(World.Get());
		World->DestroyWorld(false);
		World.Reset();
	};
	World->InitializeActorsForPlay(FURL());
	FActorSpawnParameters Spawn;
	Spawn.ObjectFlags |= RF_Transient;
	Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AStaticMeshActor* Actor = World->SpawnActor<AStaticMeshActor>(FVector::ZeroVector, FRotator::ZeroRotator, Spawn);
	if (!TestNotNull(TEXT("Independent diagnostic actor"), Actor)) { return false; }
	UStaticMeshComponent* Component = Actor->GetStaticMeshComponent();
	Component->SetMobility(EComponentMobility::Movable);
	Component->SetAbsolute(true, true, true);
	Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Component->SetGenerateOverlapEvents(false);
	if (!TestTrue(TEXT("Diagnostic component registered"), Component->IsRegistered())) { return false; }
	TestFalse(TEXT("Diagnostic has no simulated body"), Component->IsSimulatingPhysics());
	const FTransform Start(FRotator(0, -90, 0), FVector(700, 10, 100), FVector(.01, .01, .5));
	for (const bool bChangeScale : {false, true})
	{
		Component->SetWorldTransform(Start);
		TestTrue(TEXT("Baseline meets unchanged 1e-8 contract"), Component->GetComponentTransform().Equals(Start, UE_DOUBLE_SMALL_NUMBER));
		FTransform Tiny = Start;
		Tiny.AddToTranslation(FVector(0, 0, 5.e-5));
		if (bChangeScale) { Tiny.SetScale3D(FVector(.01, .01, .75)); }
		Component->SetWorldTransform(Tiny);
		const FTransform BeforeCandidate = Component->GetComponentTransform();
		TestTrue(TEXT("Ordinary setter retains prior sub-tolerance location"), BeforeCandidate.GetTranslation().Equals(Start.GetTranslation(), UE_DOUBLE_SMALL_NUMBER));
		TestFalse(TEXT("Observed ordinary setter does not meet tiny target at 1e-8"), BeforeCandidate.Equals(Tiny, UE_DOUBLE_SMALL_NUMBER));
		TestTrue(TEXT("Scale setter still applies its target"), BeforeCandidate.GetScale3D().Equals(Tiny.GetScale3D(), UE_DOUBLE_SMALL_NUMBER));
		// Public normal scene update, not a cache/direct setter. Candidate, not product fix.
		Component->SetWorldLocationAndRotationNoPhysics(Tiny.GetLocation(), Tiny.Rotator());
		const FTransform AfterCandidate = Component->GetComponentTransform();
		TestTrue(TEXT("NoPhysics candidate meets unchanged full-transform 1e-8 contract"), AfterCandidate.Equals(Tiny, UE_DOUBLE_SMALL_NUMBER));
		AddInfo(FString::Printf(TEXT("DY_P03_MICRO_TRANSFORM scaleChanged=%d registered=%d; ordinary Zdelta=%.17g; candidate Zdelta=%.17g; candidate strictMatches=%d; no live Forest writes"),
			bChangeScale, Component->IsRegistered(), BeforeCandidate.GetLocation().Z - Tiny.GetLocation().Z,
			AfterCandidate.GetLocation().Z - Tiny.GetLocation().Z, AfterCandidate.Equals(Tiny, UE_DOUBLE_SMALL_NUMBER)));
		FTransform Larger = Tiny;
		Larger.AddToTranslation(FVector(0, 0, 2.e-4));
		Component->SetWorldTransform(Larger);
		TestTrue(TEXT("Ordinary setter applies larger movement at unchanged 1e-8"), Component->GetComponentTransform().Equals(Larger, UE_DOUBLE_SMALL_NUMBER));
	}
	return true;
}
#endif

namespace DYP03RuntimeTests
{
	/** The live-map diagnostic reads BP state, but only uses native control/reset APIs.
	 * It never advances Timelines, writes Staff transforms, changes Definition or POV.
	 */
	struct FCheck
	{
		FAutomationTestBase* Test = nullptr;
		TWeakObjectPtr<ADYStagePresentation> Stage;
		TWeakObjectPtr<ADYPuzzleDirector> Director;
		TWeakObjectPtr<ADYPuppetActor> Puppet;
		TWeakObjectPtr<ADYLightRigActor> Light;
		TWeakObjectPtr<ADYForestPresentationActor> Forest;
		TWeakObjectPtr<UStaticMeshComponent> Staff;
		FVector BaseLocation = FVector::ZeroVector;
		FGuid OldToken;
		double Deadline = 0, DropClock = 0;
		int32 Phase = 0;
		bool bFailed = false, bDropObserved = false, bReplayChecked = false;
		FString CaptureDirectory;
		uint64 CaptureFrame = 0;
		bool bFinalCaptureQueued = false;
		bool bTailObserved = false;
		int32 TailPhase = -1;
		uint64 TailFrame = 0;
		double TailPortion = -1;
		FTransform TailActual = FTransform::Identity, TailExpected = FTransform::Identity;
		FRotator TailRelativeRotation = FRotator::ZeroRotator;

		void Capture(const TCHAR* Name)
		{
			// Optional diagnostic only: no screenshots or delays in player startup.
			FScreenshotRequest::RequestScreenshot(FPaths::Combine(CaptureDirectory, Name), true, false);
			CaptureFrame = GFrameCounter;
		}

		bool Assert(bool Value, const TCHAR* Message)
		{
			if (!Value) { Test->AddError(Message); bFailed = true; }
			return Value;
		}
		bool Flag(const TCHAR* Name)
		{
			const FBoolProperty* Property = FindFProperty<FBoolProperty>(Stage->GetClass(), Name);
			return Assert(Property != nullptr, TEXT("Saved BP flag missing")) && Property->GetPropertyValue_InContainer(Stage.Get());
		}
		FGuid Token(const TCHAR* Name)
		{
			const FStructProperty* Property = FindFProperty<FStructProperty>(Stage->GetClass(), Name);
			return Assert(Property && Property->Struct == TBaseStructure<FGuid>::Get(), TEXT("Saved BP typed identity missing"))
				? *Property->ContainerPtrToValuePtr<FGuid>(Stage.Get()) : FGuid();
		}
		UTimelineComponent* DropTimeline() const
		{
			for (UTimelineComponent* Timeline : TInlineComponentArray<UTimelineComponent*>(Stage.Get()))
			{
				if (Timeline->GetTimelineLength() == 2.f) { return Timeline; }
			}
			return nullptr;
		}
		void DriveAnswers()
		{
			Light->GetLightControlComponent()->SetNormalizedValue(.72);
			Puppet->GetPuppetControlComponent()->SetNormalizedValue(.85);
		}
		void Reset(const TCHAR* Description)
		{
			OldToken = Token(TEXT("CueToken"));
			Director->ResetCurrentPuzzle();
			Assert(!Flag(TEXT("CueOwned")) && !Flag(TEXT("Dropping")) && !Flag(TEXT("Growing")), TEXT("Reset retained local cue ownership"));
			for (UTimelineComponent* Timeline : TInlineComponentArray<UTimelineComponent*>(Stage.Get()))
			{
				Assert(!Timeline->IsPlaying(), TEXT("Reset retained a running presentation Timeline"));
			}
			Assert(!Forest->HasForestSession() && Forest->GetBranchMeshComponents().IsEmpty(), TEXT("Reset leaked branches"));
			Assert(Staff->GetRelativeLocation().Equals(BaseLocation, UE_DOUBLE_SMALL_NUMBER), TEXT("Reset did not restore owner-relative translation"));
			Assert(!Director->IsResolvedTokenCurrent(OldToken) && !Stage->TryAcceptStaffContact(OldToken), TEXT("Old identity remained usable"));
			UE_LOG(LogTemp, Display, TEXT("DY_P03_PACKAGED_RUNTIME Reset %s: native identity invalidated, translation restored, resources released"), Description);
			bDropObserved = false;
			bTailObserved = false;
		}
		void CheckFinal()
		{
			Assert(Flag(TEXT("CueOwned")) && !Flag(TEXT("Growing")) && Forest->HasForestSession(), TEXT("Completed holding lost current session"));
			const auto Components = Forest->GetBranchMeshComponents();
			const auto Final = Forest->GetForestGeometrySample();
			if (!Assert(Final.Status == EDYForestGeometryStatus::Valid && Components.Num() == 15 && Final.Branches.Num() == 15, TEXT("Final 15-branch geometry missing"))) { return; }
			for (int32 Index = 0; Index < 15; ++Index)
			{
				const auto* Component = Components[Index];
				const auto& Branch = Final.Branches[Index];
				Assert(Branch.bVisible && FMath::IsNearlyEqual(Branch.Portion, 1.0, UE_DOUBLE_SMALL_NUMBER), TEXT("Completed branch was not fully expanded"));
				if (!Assert(IsValid(Component), TEXT("Completed branch component missing"))) { return; }
				const FTransform Actual = Component->GetComponentTransform();
				const FTransform Expected = Branch.MeshWorldTransform;
				const bool bMatches = Component->IsVisible() == Branch.bVisible && Component->CastShadow == Branch.bVisible
					&& (!Branch.bVisible || Actual.Equals(Expected, UE_DOUBLE_SMALL_NUMBER));
				if (!bMatches)
				{
					const FVector Delta = Actual.GetTranslation() - Expected.GetTranslation();
					const FVector ScaleDelta = Actual.GetScale3D() - Expected.GetScale3D();
					const FQuat ActualQuat = Actual.GetRotation(), ExpectedQuat = Expected.GetRotation();
					Test->AddInfo(FString::Printf(TEXT("Branch=%d visible=%d shadow=%d portion=%.17g; translation delta=[%.17g,%.17g,%.17g]; scale delta=[%.17g,%.17g,%.17g]; actual quat=[%.17g,%.17g,%.17g,%.17g]; expected quat=[%.17g,%.17g,%.17g,%.17g]"),
						Index, Component->IsVisible(), Component->CastShadow, Branch.Portion, Delta.X, Delta.Y, Delta.Z,
						ScaleDelta.X, ScaleDelta.Y, ScaleDelta.Z, ActualQuat.X, ActualQuat.Y, ActualQuat.Z, ActualQuat.W,
						ExpectedQuat.X, ExpectedQuat.Y, ExpectedQuat.Z, ExpectedQuat.W));
					if (Index == 0 && bTailObserved && TailPhase == Phase)
					{
						const FVector TargetDelta = Expected.GetLocation() - TailActual.GetLocation();
						Test->AddInfo(FString::Printf(TEXT("Last diagnostic observation only (not immediate setter boundary): phase=%d lastFrame=%llu finalFrame=%llu lastPortion=%.17g; lastActualZ=%.17g lastExpectedZ=%.17g finalActualZ=%.17g finalExpectedZ=%.17g; finalActualRetainsLast=%d; targetDelta=[%.17g,%.17g,%.17g]; targetNearLastLocationAtEngine1e-4=%d targetNearLastRotatorAtEngine1e-4=%d"),
							Phase, static_cast<unsigned long long>(TailFrame), static_cast<unsigned long long>(GFrameCounter), TailPortion,
							TailActual.GetLocation().Z, TailExpected.GetLocation().Z, Actual.GetLocation().Z, Expected.GetLocation().Z,
							Actual.Equals(TailActual, UE_DOUBLE_SMALL_NUMBER), TargetDelta.X, TargetDelta.Y, TargetDelta.Z,
							Expected.GetLocation().Equals(TailActual.GetLocation(), 1.e-4), Expected.Rotator().Equals(TailRelativeRotation, 1.e-4)));
					}
				}
				Assert(bMatches, TEXT("Rendered branch differs from actual native geometry"));
			}
			if (bFailed) { return; }
			const FGuid Current = Token(TEXT("CueToken"));
			Stage->SynchronizeFromDirector();
			Assert(Token(TEXT("CueToken")) == Current && !Flag(TEXT("Dropping")) && Flag(TEXT("Completed")), TEXT("Late success synchronization restarted completed cue"));
			UE_LOG(LogTemp, Display, TEXT("DY_P03_PACKAGED_RUNTIME Complete: real A contact, 15 real shadow-casting branches; no Python cue driver"));
		}
		bool Update()
		{
			if (bFailed) { return true; }
			if (!Assert(FPlatformTime::Seconds() < Deadline, TEXT("Bounded live runtime test timed out"))) { return true; }
			if (!Assert(Stage.IsValid() && Director.IsValid() && Staff.IsValid() && Forest.IsValid(), TEXT("Live map fixture disappeared"))) { return true; }
			// Read-only last growth observation; does not tick or reposition the Timeline.
			if ((Phase == 3 || Phase == 4) && Flag(TEXT("Growing")))
			{
				const auto Components = Forest->GetBranchMeshComponents();
				const auto Sample = Forest->GetForestGeometrySample();
				if (Sample.Status == EDYForestGeometryStatus::Valid && !Components.IsEmpty()
					&& IsValid(Components[0]) && !Sample.Branches.IsEmpty())
				{
					bTailObserved = true; TailPhase = Phase; TailFrame = GFrameCounter;
					TailPortion = Sample.Branches[0].Portion;
					TailActual = Components[0]->GetComponentTransform();
					TailExpected = Sample.Branches[0].MeshWorldTransform;
					TailRelativeRotation = Components[0]->GetRelativeRotation();
				}
			}
			if (Phase == -1)
			{
				if (GFrameCounter - CaptureFrame < 3) { return false; }
				DriveAnswers(); Phase = 0;
			}
			if (Phase == 0 || Phase == 1)
			{
				if (!Flag(TEXT("Dropping"))) { return bFailed; }
				if (!bDropObserved) { bDropObserved = true; DropClock = FPlatformTime::Seconds(); }
				if (FPlatformTime::Seconds() - DropClock < .4) { return false; }
				Assert(!Staff->GetRelativeLocation().Equals(BaseLocation, UE_DOUBLE_SMALL_NUMBER), TEXT("Timeline did not move actual Staff"));
				Assert(!Forest->HasForestSession(), TEXT("Forest appeared before actual contact"));
				if (Phase == 0)
				{
					const FGuid Current = Token(TEXT("CueToken"));
					UTimelineComponent* Timeline = DropTimeline();
					if (!Assert(IsValid(Timeline), TEXT("Real drop Timeline component missing"))) { return true; }
					const float Before = Timeline->GetPlaybackPosition();
					Stage->SynchronizeFromDirector();
					Assert(Token(TEXT("CueToken")) == Current && Timeline->GetPlaybackPosition() == Before, TEXT("Duplicate Resolve hook restarted Timeline"));
					Reset(TEXT("Drop")); DriveAnswers(); Phase = 1;
				}
				else if (!bReplayChecked)
				{
					const FGuid Current = Token(TEXT("CueToken"));
					UTimelineComponent* Timeline = DropTimeline();
					if (!Assert(IsValid(Timeline), TEXT("Second drop Timeline component missing"))) { return true; }
					const float Before = Timeline->GetPlaybackPosition();
					const FTransform StaffBefore = Staff->GetComponentTransform();
					// Diagnostic replay only: proves an old callback cannot clear a new cue.
					Stage->ReceiveStaffPresentationInvalidated(OldToken);
					Assert(Current != OldToken && Token(TEXT("CueToken")) == Current && Flag(TEXT("CueOwned"))
						&& Timeline->GetPlaybackPosition() == Before && Timeline->IsPlaying()
						&& Staff->GetComponentTransform().Equals(StaffBefore, 0), TEXT("Old invalidation damaged new cue"));
					bReplayChecked = true; Phase = 2;
				}
			}
			else if (Phase == 2 && Flag(TEXT("Growing")))
			{
				Assert(Stage->GetStaffContactPresentationSnapshot().bHasContact && Forest->HasForestSession(), TEXT("Growth bypassed real contact"));
				Reset(TEXT("Growth")); DriveAnswers(); Phase = 3;
			}
			else if (Phase == 3 && Flag(TEXT("Completed")))
			{
				if (!CaptureDirectory.IsEmpty() && !bFinalCaptureQueued)
				{
					CheckFinal();
					if (bFailed) { return true; }
					bFinalCaptureQueued = true; Capture(TEXT("CompletedHolding.png"));
					return bFailed;
				}
				if (bFinalCaptureQueued && GFrameCounter - CaptureFrame < 3) { return false; }
				if (!bFinalCaptureQueued) { CheckFinal(); }
				if (bFailed) { return true; }
				Reset(TEXT("CompletedHolding")); DriveAnswers(); Phase = 4;
			}
			else if (Phase == 4 && Flag(TEXT("Completed")))
			{
				CheckFinal();
				if (bFailed) { return true; }
				// This process is a test-only run that exits afterwards; no map save.
				Director->Destroy();
				Assert(!Flag(TEXT("CueOwned")) && !Forest->HasForestSession() && Forest->GetBranchMeshComponents().IsEmpty()
					&& Staff->GetRelativeLocation().Equals(BaseLocation, UE_DOUBLE_SMALL_NUMBER), TEXT("Director EndPlay leaked completed cue"));
				UE_LOG(LogTemp, Display, TEXT("DY_P03_PACKAGED_RUNTIME DirectorEndPlay: completed cue released; PASS=%d"), !bFailed);
				return true;
			}
			return bFailed;
		}
	};
}

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FDYP03LiveRuntimeCommand, TSharedPtr<DYP03RuntimeTests::FCheck>, Check);
bool FDYP03LiveRuntimeCommand::Update() { return Check->Update(); }

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYP03LiveRuntimeTest,
	"DengYingShanHai.P03.Runtime.LiveMapCausalLifecycle",
	EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter)
bool FDYP03LiveRuntimeTest::RunTest(const FString& Parameters)
{
	AddInfo(TEXT("DY_P03_RUNTIME_DIAGNOSTIC_VERSION=20261006-MicroSetterProbe; original 1e-8 contract unchanged"));
	UWorld* World = nullptr;
	for (const FWorldContext& Context : GEngine->GetWorldContexts())
	{
		if (Context.WorldType == EWorldType::Game && Context.World()
			&& Context.World()->GetOutermost()->GetName().EndsWith(TEXT("/LV_M3RuntimeCandidate"))) { World = Context.World(); break; }
	}
	if (!TestNotNull(TEXT("Must launch the exact cooked/runtime Dev candidate map"), World)) { return false; }
	auto Check = MakeShared<DYP03RuntimeTests::FCheck>();
	Check->Test = this;
	// One diagnostic fixture lookup, never runtime presentation world discovery.
	for (TActorIterator<ADYStagePresentation> It(World); It; ++It)
	{
		if (It->GetClass()->GetName() == TEXT("BP_DYP03RuntimePresentation_C"))
		{
			if (!TestFalse(TEXT("Only one runtime presentation"), Check->Stage.IsValid())) { return false; }
			Check->Stage = *It;
		}
	}
	if (!TestTrue(TEXT("Actual saved runtime presentation exists"), Check->Stage.IsValid())) { return false; }
	Check->Director = Check->Stage->GetPuzzleDirector();
	Check->Forest = Check->Stage->GetForestPresentationActor();
	if (!TestTrue(TEXT("Same-world authority and actual configured resource"), Check->Director.IsValid() && Check->Forest.IsValid()
		&& Check->Director->GetWorld() == World && Check->Forest->GetWorld() == World)) { return false; }
	Check->Light = Check->Director->GetLightRigActor(); Check->Puppet = Check->Director->GetPuppetActor();
	if (!TestTrue(TEXT("Native controls present"), Check->Light.IsValid() && Check->Puppet.IsValid())) { return false; }
	for (UStaticMeshComponent* Component : TInlineComponentArray<UStaticMeshComponent*>(Check->Puppet.Get()))
	{
		if (Component->GetFName() == TEXT("Staff")) { Check->Staff = Component; }
	}
	if (!TestTrue(TEXT("Actual Staff present"), Check->Staff.IsValid())) { return false; }
	TestEqual(TEXT("Still 15 Hz"), Check->Director->GetEvaluationFrequencyHz(), 15.0);
	if (!TestFalse(TEXT("Startup has no automatic answer"), Check->Director->GetResolvedPuzzleSnapshot().bIsResolved)
		|| !TestFalse(TEXT("Startup has no forest"), Check->Forest->HasForestSession())) { return false; }
	Check->BaseLocation = Check->Staff->GetRelativeLocation();
	Check->Deadline = FPlatformTime::Seconds() + 60;
	FParse::Value(FCommandLine::Get(), TEXT("DYP03CaptureDir="), Check->CaptureDirectory);
	if (!Check->CaptureDirectory.IsEmpty())
	{
		if (!TestFalse(TEXT("Diagnostic capture path must be absolute"), FPaths::IsRelative(Check->CaptureDirectory))) { return false; }
		Check->Capture(TEXT("UnsolvedStartup.png")); Check->Phase = -1;
	}
	else { Check->DriveAnswers(); }
	ADD_LATENT_AUTOMATION_COMMAND(FDYP03LiveRuntimeCommand(Check));
	return true;
}

#endif
