#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "CoreGlobals.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Interaction/DYControllable.h"
#include "Interaction/DYInteractionComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Player/DYStageOperatorPawn.h"
#include "Tests/DYControlExitRecorder.h"

namespace DYControlStaleTests
{
	constexpr EAutomationTestFlags TestFlags =
		EAutomationTestFlags::EditorContext |
		EAutomationTestFlags::EngineFilter;

	/**
	 * Transient game world so spawned actors receive the play-mode initialisation the
	 * interface dispatch depends on. Same pattern as DYFocusAutomationTests.cpp.
	 */
	struct FScopedTestWorld
	{
		FScopedTestWorld()
		{
			if (!GEngine)
			{
				return;
			}

			const FName WorldName = MakeUniqueObjectName(
				nullptr,
				UWorld::StaticClass(),
				TEXT("DYControlStaleWorld"),
				EUniqueObjectNameOptions::GloballyUnique);
			FWorldContext& WorldContext = GEngine->CreateNewWorldContext(EWorldType::Game);
			World = UWorld::CreateWorld(EWorldType::Game, false, WorldName, GetTransientPackage());
			if (!World)
			{
				return;
			}

			World->AddToRoot();
			bIsRooted = true;
			WorldContext.SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
		}

		~FScopedTestWorld()
		{
			if (!World || !GEngine)
			{
				return;
			}

			GEngine->DestroyWorldContext(World);
			World->DestroyWorld(false);
			if (bIsRooted)
			{
				World->RemoveFromRoot();
			}
			World = nullptr;
		}

		UWorld* World = nullptr;

	private:
		bool bIsRooted = false;
	};

	void RegisterComponents(AActor* Actor)
	{
		if (Actor)
		{
			Actor->RegisterAllComponents();
		}
	}

	/** The production focus evaluation, driven through the automation-only seam. */
	void EvaluateFocus(
		UDYInteractionComponent& Component,
		const FVector& ViewLocation,
		const FRotator& ViewRotation,
		const FVector& PawnLocation)
	{
		FDYFocusAutomationSeam::EvaluateFocus(Component, ViewLocation, ViewRotation, PawnLocation);
	}
}

// The reproduction path from the review: manipulating -> destroy the controlled
// actor -> request manipulation again. The exit broadcast must still happen exactly
// once, and the component must remain usable afterwards.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYControlStaleActorExitNotifyTest,
	"DengYingShanHai.M1.Control.StaleActorExitNotify",
	DYControlStaleTests::TestFlags)

bool FDYControlStaleActorExitNotifyTest::RunTest(const FString& Parameters)
{
	DYControlStaleTests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}
	UWorld* World = TestWorld.World;

	FActorSpawnParameters SpawnParameters;
	SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	ADYStageOperatorPawn* Pawn = World->SpawnActor<ADYStageOperatorPawn>(
		ADYStageOperatorPawn::StaticClass(),
		FTransform(FRotator::ZeroRotator, FVector(0.0, 0.0, 0.0)),
		SpawnParameters);
	TestNotNull(TEXT("Operator pawn spawns"), Pawn);
	if (!Pawn)
	{
		return false;
	}
	DYControlStaleTests::RegisterComponents(Pawn);

	UDYInteractionComponent* Interaction = Pawn->GetInteractionComponent();
	TestNotNull(TEXT("Operator owns the interaction component under test"), Interaction);
	if (!Interaction)
	{
		Pawn->Destroy();
		return false;
	}

	ADYLightRigActor* Lamp = World->SpawnActor<ADYLightRigActor>(
		ADYLightRigActor::StaticClass(),
		FTransform(FRotator::ZeroRotator, FVector(515.0, 0.0, 0.0)),
		SpawnParameters);
	TestNotNull(TEXT("Controllable lamp spawns"), Lamp);
	if (!Lamp)
	{
		Pawn->Destroy();
		return false;
	}
	DYControlStaleTests::RegisterComponents(Lamp);
	TestTrue(TEXT("Lamp implements the Controllable interface"), Lamp->Implements<UDYControllable>());

	// Enter control through the same seam the focus tests use, so FocusedActor is set
	// by the real evaluation before ToggleControl runs.
	DYControlStaleTests::EvaluateFocus(
		*Interaction,
		FVector(-360.0, 0.0, 0.0),
		FRotator::ZeroRotator,
		FVector(0.0, 0.0, 0.0));
	TestTrue(
		TEXT("Precondition: the lamp is focused before the control request"),
		Interaction->GetFocusedActor() == Lamp);

	UDYControlExitRecorder* Recorder = NewObject<UDYControlExitRecorder>(GetTransientPackage());
	TestNotNull(TEXT("Broadcast recorder is created"), Recorder);
	if (!Recorder)
	{
		Lamp->Destroy();
		Pawn->Destroy();
		return false;
	}
	Recorder->AddToRoot();
	Interaction->OnControlStateChanged.AddDynamic(
		Recorder,
		&UDYControlExitRecorder::HandleControlStateChanged);

	// Step 1: entering control broadcasts exactly one enter notification.
	const bool bEntered = Interaction->ToggleControl();
	TestTrue(TEXT("ToggleControl enters control on a focused controllable lamp"), bEntered);
	TestTrue(TEXT("IsControlling reports the open session"), Interaction->IsControlling());
	TestEqual(TEXT("One enter broadcast after entering control"), Recorder->Count, 1);
	TestEqual(TEXT("The enter broadcast is not a null-actor exit"), Recorder->NullActorCount, 0);
	TestEqual(TEXT("Enter count is one"), Recorder->EnterCount, 1);
	TestEqual(TEXT("Exit count is still zero"), Recorder->ExitCount, 0);

	// Step 2: destroy the controlled actor while it is being manipulated. The weak
	// reference expires; before the fix the exit broadcast was skipped entirely.
	Lamp->Destroy();
	TestFalse(
		TEXT("The destroyed lamp's weak reference no longer reports as controlling"),
		Interaction->IsControlling());

	// Step 3: requesting the toggle again must first finish the interrupted session
	// with exactly one null-actor exit broadcast, instead of stranding the pawn in
	// manipulation mode. This toggle does not enter a new control (no focus candidate
	// has been re-established yet), which mirrors the real operator's first press.
	const bool bSecondToggle = Interaction->ToggleControl();
	TestFalse(
		TEXT("The first re-request after destruction does not enter a new control"),
		bSecondToggle);
	TestFalse(
		TEXT("No control session remains after the stale cleanup"),
		Interaction->IsControlling());
	TestEqual(
		TEXT("Exactly one additional broadcast followed the stale cleanup"),
		Recorder->Count, 2);
	TestEqual(
		TEXT("That additional broadcast is the null-actor exit"),
		Recorder->NullActorCount, 1);
	TestEqual(TEXT("Enter count is unchanged"), Recorder->EnterCount, 1);
	TestEqual(TEXT("Exit count is now one"), Recorder->ExitCount, 1);

	// Step 4: repeated EndActiveControl calls must not broadcast again.
	Interaction->EndActiveControl();
	Interaction->EndActiveControl();
	TestEqual(
		TEXT("Repeated exit requests do not duplicate the exit broadcast"),
		Recorder->Count, 2);

	// Step 5: the component must remain usable. A newly focused lamp can be entered
	// and released through the same contract, proving the stale cleanup did not wedge
	// the session state.
	ADYLightRigActor* SecondLamp = World->SpawnActor<ADYLightRigActor>(
		ADYLightRigActor::StaticClass(),
		FTransform(FRotator::ZeroRotator, FVector(515.0, 0.0, 0.0)),
		SpawnParameters);
	TestNotNull(TEXT("A replacement lamp spawns"), SecondLamp);
	if (SecondLamp)
	{
		DYControlStaleTests::RegisterComponents(SecondLamp);
		DYControlStaleTests::EvaluateFocus(
			*Interaction,
			FVector(-360.0, 0.0, 0.0),
			FRotator::ZeroRotator,
			FVector(0.0, 0.0, 0.0));
		TestTrue(
			TEXT("The replacement lamp becomes focused after the stale cleanup"),
			Interaction->GetFocusedActor() == SecondLamp);

		const bool bReentered = Interaction->ToggleControl();
		TestTrue(TEXT("Control can be entered again after the stale cleanup"), bReentered);
		TestTrue(TEXT("The new session is active"), Interaction->IsControlling());
		TestEqual(TEXT("One enter broadcast for the new session"), Recorder->Count, 3);
		TestEqual(TEXT("The new session's broadcast is a real actor enter"), Recorder->NullActorCount, 1);

		Interaction->EndActiveControl();
		TestEqual(
			TEXT("Releasing the new session broadcasts its exit"),
			Recorder->Count, 4);
		TestEqual(TEXT("Exit count is now two"), Recorder->ExitCount, 2);

		SecondLamp->Destroy();
	}

	Interaction->OnControlStateChanged.RemoveDynamic(
		Recorder,
		&UDYControlExitRecorder::HandleControlStateChanged);
	Recorder->RemoveFromRoot();
	Pawn->Destroy();
	return true;
}

// A direct EndActiveControl on an already stale session (no toggle re-request in
// between) must also complete the exit contract exactly once. This is the path an
// EndPlay or a reset takes when the controlled actor died earlier.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYControlStaleActorDirectEndTest,
	"DengYingShanHai.M1.Control.StaleActorDirectEnd",
	DYControlStaleTests::TestFlags)

bool FDYControlStaleActorDirectEndTest::RunTest(const FString& Parameters)
{
	DYControlStaleTests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}
	UWorld* World = TestWorld.World;

	FActorSpawnParameters SpawnParameters;
	SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	ADYStageOperatorPawn* Pawn = World->SpawnActor<ADYStageOperatorPawn>(
		ADYStageOperatorPawn::StaticClass(),
		FTransform(FRotator::ZeroRotator, FVector(0.0, 0.0, 0.0)),
		SpawnParameters);
	TestNotNull(TEXT("Operator pawn spawns"), Pawn);
	if (!Pawn)
	{
		return false;
	}
	DYControlStaleTests::RegisterComponents(Pawn);

	UDYInteractionComponent* Interaction = Pawn->GetInteractionComponent();
	TestNotNull(TEXT("Operator owns the interaction component under test"), Interaction);
	if (!Interaction)
	{
		Pawn->Destroy();
		return false;
	}

	ADYLightRigActor* Lamp = World->SpawnActor<ADYLightRigActor>(
		ADYLightRigActor::StaticClass(),
		FTransform(FRotator::ZeroRotator, FVector(515.0, 0.0, 0.0)),
		SpawnParameters);
	TestNotNull(TEXT("Controllable lamp spawns"), Lamp);
	if (!Lamp)
	{
		Pawn->Destroy();
		return false;
	}
	DYControlStaleTests::RegisterComponents(Lamp);

	DYControlStaleTests::EvaluateFocus(
		*Interaction,
		FVector(-360.0, 0.0, 0.0),
		FRotator::ZeroRotator,
		FVector(0.0, 0.0, 0.0));
	TestTrue(
		TEXT("Precondition: the lamp is focused before the control request"),
		Interaction->GetFocusedActor() == Lamp);

	UDYControlExitRecorder* Recorder = NewObject<UDYControlExitRecorder>(GetTransientPackage());
	TestNotNull(TEXT("Broadcast recorder is created"), Recorder);
	if (!Recorder)
	{
		Lamp->Destroy();
		Pawn->Destroy();
		return false;
	}
	Recorder->AddToRoot();
	Interaction->OnControlStateChanged.AddDynamic(
		Recorder,
		&UDYControlExitRecorder::HandleControlStateChanged);

	TestTrue(TEXT("Control is entered"), Interaction->ToggleControl());
	TestEqual(TEXT("One enter broadcast"), Recorder->EnterCount, 1);

	// Destroy the controlled actor, then end the session directly, the way EndPlay
	// and the operator reset already do.
	Lamp->Destroy();
	Interaction->EndActiveControl();

	TestFalse(TEXT("No control session remains"), Interaction->IsControlling());
	TestEqual(
		TEXT("The stale exit broadcast happened exactly once"),
		Recorder->ExitCount, 1);
	TestEqual(
		TEXT("The stale exit used a null actor because the real one is gone"),
		Recorder->NullActorCount, 1);

	// Ending again must stay silent: the exit contract is already fulfilled.
	Interaction->EndActiveControl();
	TestEqual(
		TEXT("A repeated direct end does not duplicate the broadcast"),
		Recorder->ExitCount, 1);

	Interaction->OnControlStateChanged.RemoveDynamic(
		Recorder,
		&UDYControlExitRecorder::HandleControlStateChanged);
	Recorder->RemoveFromRoot();
	Pawn->Destroy();
	return true;
}

// Timer-driven cleanup path: entering control, destroying the controlled actor and
// then letting the REAL world timer (not a manual method call) observe the stale
// session. This is the path a player hits by simply waiting after the actor died,
// without pressing the toggle or triggering an EndPlay/reset.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYControlStaleActorTimerDrivenCleanupTest,
	"DengYingShanHai.M1.Control.StaleActorTimerDrivenCleanup",
	DYControlStaleTests::TestFlags)

bool FDYControlStaleActorTimerDrivenCleanupTest::RunTest(const FString& Parameters)
{
	DYControlStaleTests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}
	UWorld* World = TestWorld.World;

	FActorSpawnParameters SpawnParameters;
	SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	ADYStageOperatorPawn* Pawn = World->SpawnActor<ADYStageOperatorPawn>(
		ADYStageOperatorPawn::StaticClass(),
		FTransform(FRotator::ZeroRotator, FVector(0.0, 0.0, 0.0)),
		SpawnParameters);
	TestNotNull(TEXT("Operator pawn spawns"), Pawn);
	if (!Pawn)
	{
		return false;
	}
	DYControlStaleTests::RegisterComponents(Pawn);

	UDYInteractionComponent* Interaction = Pawn->GetInteractionComponent();
	TestNotNull(TEXT("Operator owns the interaction component under test"), Interaction);
	if (!Interaction)
	{
		Pawn->Destroy();
		return false;
	}

	ADYLightRigActor* Lamp = World->SpawnActor<ADYLightRigActor>(
		ADYLightRigActor::StaticClass(),
		FTransform(FRotator::ZeroRotator, FVector(515.0, 0.0, 0.0)),
		SpawnParameters);
	TestNotNull(TEXT("Controllable lamp spawns"), Lamp);
	if (!Lamp)
	{
		Pawn->Destroy();
		return false;
	}
	DYControlStaleTests::RegisterComponents(Lamp);

	// BeginPlay arms the periodic focus timer. The transient world has no GameMode, so
	// UWorld::BeginPlay() alone does not dispatch actor BeginPlay here; instead the
	// engine's real per-actor dispatch path is used on the two spawned actors, which
	// is exactly what arms the timer inside UDYInteractionComponent::BeginPlay.
	// TimerManager then advances through real World->Tick calls below.
	Pawn->DispatchBeginPlay();
	Lamp->DispatchBeginPlay();

	// The light control component re-locates the lamp onto its rail during BeginPlay
	// (SetNormalizedValue -> SetActorLocation), so the spawned position is no longer
	// where the lamp actually is. Place the operator and the camera relative to the
	// lamp's real post-BeginPlay location, exactly like the real run does.
	const FVector LampLocation = Lamp->GetActorLocation();
	const FVector PawnLocation = LampLocation - FVector(515.0, 0.0, 0.0);
	Pawn->SetActorLocation(PawnLocation);
	const FVector ViewLocation = PawnLocation - FVector(360.0, 0.0, 0.0);

	UDYControlExitRecorder* Recorder = NewObject<UDYControlExitRecorder>(GetTransientPackage());
	TestNotNull(TEXT("Broadcast recorder is created"), Recorder);
	if (!Recorder)
	{
		Lamp->Destroy();
		Pawn->Destroy();
		return false;
	}
	Recorder->AddToRoot();
	Interaction->OnControlStateChanged.AddDynamic(
		Recorder,
		&UDYControlExitRecorder::HandleControlStateChanged);

	// Precondition: the real focus timer is armed. Without it the Ticks below could
	// not trigger the cleanup path and a pass would be vacuous.
	TestTrue(
		TEXT("Precondition: the periodic focus timer is armed after BeginPlay"),
		FDYFocusAutomationSeam::HasActiveFocusTimer(*Interaction));

	// Enter control through the real focus evaluation, then destroy the actor.
	DYControlStaleTests::EvaluateFocus(
		*Interaction,
		ViewLocation,
		FRotator::ZeroRotator,
		PawnLocation);
	TestTrue(
		TEXT("Precondition: the lamp is focused before the control request"),
		Interaction->GetFocusedActor() == Lamp);
	TestTrue(TEXT("Control is entered"), Interaction->ToggleControl());
	TestEqual(TEXT("One enter broadcast before the actor is destroyed"), Recorder->Count, 1);

	Lamp->Destroy();
	TestFalse(
		TEXT("The destroyed lamp no longer reports as controlling"),
		Interaction->IsControlling());

	// Advance the timer manager exactly the way the engine frame loop does: one frame
	// counter increment, then one FTimerManager::Tick. TimerManager deduplicates ticks
	// within a single frame (HasBeenTickedThisFrame), so without advancing the frame
	// counter only the first call in this loop would ever run. The transient test
	// world has no engine loop of its own; the component under test is not called by
	// hand at any point in this loop. 6 x 0.2 s gives the 0.1 s focus timer several
	// firing opportunities with margin for float comparison.
	for (int32 FrameIndex = 0; FrameIndex < 6; ++FrameIndex)
	{
		++GFrameCounter;
		World->GetTimerManager().Tick(0.2f);
	}

	TestEqual(
		TEXT("The timer-driven cleanup broadcast the exit exactly once"),
		Recorder->Count, 2);
	TestEqual(
		TEXT("The timer-driven exit used a null actor"),
		Recorder->NullActorCount, 1);
	TestEqual(TEXT("Enter count is unchanged"), Recorder->EnterCount, 1);
	TestEqual(TEXT("Exit count is now one"), Recorder->ExitCount, 1);
	TestFalse(
		TEXT("No control session remains after the timer-driven cleanup"),
		Interaction->IsControlling());

	// Keep the frame loop advancing: the cleanup must not repeat itself on later
	// timer fires, and the now-normal focus refreshes must not broadcast anything.
	for (int32 FrameIndex = 0; FrameIndex < 6; ++FrameIndex)
	{
		++GFrameCounter;
		World->GetTimerManager().Tick(0.2f);
	}
	TestEqual(
		TEXT("Later timer fires do not duplicate the exit broadcast"),
		Recorder->Count, 2);

	// The component must remain usable afterwards: a new lamp can be focused and
	// entered, then released through the normal contract. The replacement lamp also
	// goes through BeginPlay (rail relocation included), and the operator is placed
	// relative to its actual post-BeginPlay location.
	ADYLightRigActor* SecondLamp = World->SpawnActor<ADYLightRigActor>(
		ADYLightRigActor::StaticClass(),
		FTransform(FRotator::ZeroRotator, FVector(515.0, 0.0, 0.0)),
		SpawnParameters);
	TestNotNull(TEXT("A replacement lamp spawns"), SecondLamp);
	if (SecondLamp)
	{
		DYControlStaleTests::RegisterComponents(SecondLamp);
		SecondLamp->DispatchBeginPlay();
		const FVector SecondLampLocation = SecondLamp->GetActorLocation();
		const FVector SecondPawnLocation = SecondLampLocation - FVector(515.0, 0.0, 0.0);
		Pawn->SetActorLocation(SecondPawnLocation);
		DYControlStaleTests::EvaluateFocus(
			*Interaction,
			SecondPawnLocation - FVector(360.0, 0.0, 0.0),
			FRotator::ZeroRotator,
			SecondPawnLocation);
		TestTrue(
			TEXT("The replacement lamp becomes focused after the timer-driven cleanup"),
			Interaction->GetFocusedActor() == SecondLamp);

		const bool bReentered = Interaction->ToggleControl();
		TestTrue(TEXT("Control can be entered again after the timer-driven cleanup"), bReentered);
		TestEqual(TEXT("The new session's enter broadcast is recorded"), Recorder->Count, 3);
		TestEqual(TEXT("Still exactly one null-actor exit so far"), Recorder->NullActorCount, 1);

		Interaction->EndActiveControl();
		TestEqual(TEXT("Releasing the new session broadcasts its exit"), Recorder->Count, 4);
		TestEqual(TEXT("Exit count is now two"), Recorder->ExitCount, 2);

		SecondLamp->Destroy();
	}

	Interaction->OnControlStateChanged.RemoveDynamic(
		Recorder,
		&UDYControlExitRecorder::HandleControlStateChanged);
	Recorder->RemoveFromRoot();
	Pawn->Destroy();
	return true;
}

#endif
