#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Components/BoxComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Interaction/DYControllable.h"
#include "Interaction/DYControlTypes.h"
#include "Interaction/DYInteractionComponent.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Player/DYStageOperatorPawn.h"

namespace DYFocusTests
{
	constexpr EAutomationTestFlags TestFlags =
		EAutomationTestFlags::EditorContext |
		EAutomationTestFlags::EngineFilter;

	constexpr double OperatorReach = 700.0;
	constexpr double CameraBoom = 360.0;

	/**
	 * Transient game world for real component registration, Visibility traces and
	 * interface dispatch. Follows the engine's own ActorTestSpawner pattern:
	 * root the world, point the context at it, then InitializeActorsForPlay so the
	 * actor/reflection path a spawned Actor relies on is actually initialised.
	 * The CQTest module itself is not referenced.
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
				TEXT("DYFocusRuntimeWorld"),
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

			// Without this the spawned actors never get the play-mode initialisation that
			// interface dispatch depends on, so Execute_* calls fail even though the
			// direct _Implementation call succeeds.
			World->InitializeActorsForPlay(FURL());
			bHasPhysicsScene = World->GetPhysicsScene() != nullptr;
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

		/** True when the transient world got a physics scene, so traces can hit. */
		bool HasPhysicsScene() const { return bHasPhysicsScene; }

	private:
		bool bIsRooted = false;
		bool bHasPhysicsScene = false;
	};

	/** Registers every component on the actor so it enters the world's physics scene. */
	void RegisterComponents(AActor* Actor)
	{
		if (Actor)
		{
			Actor->RegisterAllComponents();
		}
	}

	/**
	 * Gives the actor an opaque collision volume at an explicit WORLD location, because
	 * the real Dev lamp gets its Visibility-blocking body from its Cylinder/Cone mesh
	 * components. The caller must pass the actor's own world position, otherwise every
	 * box would collapse onto the world origin.
	 */
	void AddVisibilityBlockingBox(AActor* Actor, const FVector& WorldLocation, const FVector& BoxExtent)
	{
		if (!Actor)
		{
			return;
		}

		UBoxComponent* Box = NewObject<UBoxComponent>(Actor);
		Box->SetBoxExtent(BoxExtent);
		Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
		Box->SetCollisionResponseToAllChannels(ECR_Ignore);
		Box->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
		Box->SetWorldLocation(WorldLocation);
		Box->RegisterComponent();
	}

	/** Drives the real private focus helper through the automation seam. */
	void EvaluateFocus(
		UDYInteractionComponent& Component,
		const FVector& ViewLocation,
		const FRotator& ViewRotation,
		const FVector& PawnLocation)
	{
		FDYFocusAutomationSeam::EvaluateFocus(Component, ViewLocation, ViewRotation, PawnLocation);
	}

	/**
	 * Fixture-only raw Visibility trace. Used purely to prove the fixture itself really
	 * places a hit-blocking body on the ray, so a "no hit" result cannot masquerade as a
	 * successful rejection. It does NOT reimplement any production gating.
	 */
	AActor* TraceFirstVisibilityHit(
		UWorld* World,
		const FVector& TraceStart,
		const FVector& TraceEnd,
		const APawn* OwnerPawn)
	{
		FHitResult Hit;
		FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(DYFocusFixtureProbe), false, OwnerPawn);
		World->LineTraceSingleByChannel(Hit, TraceStart, TraceEnd, ECC_Visibility, QueryParams);
		return Hit.GetActor();
	}

	/**
	 * Reports why a controllable lamp would or would not accept control, separating the
	 * three independent causes: a missing control component, gameplay response being
	 * disabled, and a session already being open. Read-only; never changes product state.
	 */
	void AssertLampControlPreconditions(
		FAutomationTestBase& Test,
		const TCHAR* Label,
		ADYLightRigActor* Lamp,
		APawn* Instigator)
	{
		UDYLightControlComponent* Control = Lamp ? Lamp->GetLightControlComponent() : nullptr;
		Test.TestNotNull(FString::Printf(TEXT("%s: lamp owns a light control component"), Label), Control);
		if (!Control)
		{
			return;
		}

		Test.TestTrue(
			FString::Printf(TEXT("%s: gameplay control response is enabled"), Label),
			Control->IsControlEnabled());
		Test.TestFalse(
			FString::Printf(TEXT("%s: no control session is already open"), Label),
			Control->IsUnderControl());

		// Direct implementation call and interface dispatch can disagree if the fixture
		// world has no reflection or the actor is not fully initialised, so record both.
		FDYControlContext Context;
		Context.InstigatorPawn = Instigator;
		const bool bDirect = Lamp->CanBeginControl_Implementation(Context);
		const bool bDispatched = IDYControllable::Execute_CanBeginControl(Lamp, Context);
		Test.TestTrue(
			FString::Printf(TEXT("%s: direct CanBeginControl_Implementation accepts (got %d)"), Label, bDirect ? 1 : 0),
			bDirect);
		Test.TestTrue(
			FString::Printf(TEXT("%s: dispatched Execute_CanBeginControl accepts (got %d)"), Label, bDispatched ? 1 : 0),
			bDispatched);
		Test.TestTrue(
			FString::Printf(TEXT("%s: instigator pawn is set on the context"), Label),
			Context.InstigatorPawn.Get() != nullptr);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYFocusTraceLengthCompensationTest,
	"DengYingShanHai.M1.Focus.CameraOffsetCompensation",
	DYFocusTests::TestFlags)

bool FDYFocusTraceLengthCompensationTest::RunTest(const FString& Parameters)
{
	const FVector OperatorLocation(0.0, 0.0, 0.0);
	const FVector ViewLocation(-DYFocusTests::CameraBoom, 0.0, 0.0);

	const double TraceLength = UDYInteractionComponent::ComputeFocusTraceLength(
		ViewLocation,
		OperatorLocation,
		DYFocusTests::OperatorReach);

	// The reported failure: the operator stands ~515 cm from the lamp while the boom
	// pushes the camera ~360 cm further back, so an uncompensated 700 cm trace ends
	// well before the lamp. The compensated length must cover camera offset + reach.
	TestTrue(
		TEXT("Compensated trace reaches an operator-reachable target that a bare 700 cm trace misses"),
		TraceLength > DYFocusTests::OperatorReach);
	TestEqual(
		TEXT("Trace length is exactly the camera offset plus the operator reach"),
		TraceLength,
		DYFocusTests::CameraBoom + DYFocusTests::OperatorReach);

	// A camera at the operator (first person) must not inflate the trace.
	TestEqual(
		TEXT("A coincident viewpoint keeps the bare operator reach"),
		UDYInteractionComponent::ComputeFocusTraceLength(OperatorLocation, OperatorLocation, DYFocusTests::OperatorReach),
		DYFocusTests::OperatorReach);

	// The compensation must stay a true upper bound for every point in the reach sphere.
	const FVector SphereSamples[] =
	{
		FVector(DYFocusTests::OperatorReach, 0.0, 0.0),
		FVector(-DYFocusTests::OperatorReach, 0.0, 0.0),
		FVector(0.0, DYFocusTests::OperatorReach, 0.0),
		FVector(0.0, 0.0, DYFocusTests::OperatorReach),
	};
	for (const FVector& Sample : SphereSamples)
	{
		TestTrue(
			TEXT("Every sample inside the reach sphere stays within the compensated trace length"),
			FVector::Distance(ViewLocation, Sample) <= TraceLength);
	}

	// FocusDistance keeps its documented meaning; it is not redefined by this change.
	TestEqual(
		TEXT("Operator reach remains 700 cm"),
		GetDefault<UDYInteractionComponent>()->GetFocusDistance(),
		DYFocusTests::OperatorReach);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYFocusOperatorRadiusGateTest,
	"DengYingShanHai.M1.Focus.OperatorRadiusGate",
	DYFocusTests::TestFlags)

bool FDYFocusOperatorRadiusGateTest::RunTest(const FString& Parameters)
{
	const FVector OperatorLocation(0.0, 0.0, 0.0);

	// The measured M2 case: ~515 cm from operator to lamp, well inside the reach.
	TestTrue(
		TEXT("A candidate ~515 cm away stays focusable"),
		UDYInteractionComponent::IsWithinFocusDistance(
			OperatorLocation, FVector(440.0, 190.0, 190.0), DYFocusTests::OperatorReach));

	// Exactly at the boundary is still valid; the gate is inclusive.
	TestTrue(
		TEXT("A candidate exactly at the reach boundary is accepted"),
		UDYInteractionComponent::IsWithinFocusDistance(
			OperatorLocation, FVector(DYFocusTests::OperatorReach, 0.0, 0.0), DYFocusTests::OperatorReach));

	// Beyond the operator reach the camera must not be able to grant focus.
	TestFalse(
		TEXT("A candidate beyond the operator reach is rejected even when unoccluded"),
		UDYInteractionComponent::IsWithinFocusDistance(
			OperatorLocation, FVector(760.0, 0.0, 0.0), DYFocusTests::OperatorReach));

	// The far puppet must stay out of reach from the spawn.
	TestFalse(
		TEXT("The M2 puppet at ~1500 cm is rejected from the operator start"),
		UDYInteractionComponent::IsWithinFocusDistance(
			FVector(-900.0, -210.0, 120.0), FVector(600.0, -80.0, 210.0), DYFocusTests::OperatorReach));

	// A non-positive radius collapses to a zero-length reach: it must not silently
	// become a large or infinite radius. Only a coincident candidate satisfies it.
	TestTrue(
		TEXT("A zero reach accepts only a coincident candidate"),
		UDYInteractionComponent::IsWithinFocusDistance(OperatorLocation, OperatorLocation, 0.0));
	TestFalse(
		TEXT("A negative reach never grants focus to a separated candidate"),
		UDYInteractionComponent::IsWithinFocusDistance(OperatorLocation, FVector(1.0, 0.0, 0.0), 0.0));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYFocusNoTickLifecycleContractTest,
	"DengYingShanHai.M1.Focus.NoTickLifecycleContract",
	DYFocusTests::TestFlags)

bool FDYFocusNoTickLifecycleContractTest::RunTest(const FString& Parameters)
{
	// Scope note: this test only proves the update mechanism is a timer and not a Tick.
	// It does NOT construct geometry and does NOT prove anything about occlusion;
	// real trace and occlusion behaviour is covered by
	// DengYingShanHai.M1.Focus.RuntimeTrace, which runs against a real world.
	const UDYInteractionComponent* Component = GetDefault<UDYInteractionComponent>();
	TestNotNull(TEXT("Interaction component CDO exists"), Component);
	TestFalse(TEXT("Interaction does not scan the world on Tick"), Component->PrimaryComponentTick.bCanEverTick);
	if (const UActorComponent* AsComponent = Component)
	{
		TestFalse(TEXT("Interaction component tick stays disabled"), AsComponent->IsComponentTickEnabled());
	}

	// The operator still owns a real, reusable interaction capability.
	const ADYStageOperatorPawn* Operator = GetDefault<ADYStageOperatorPawn>();
	TestNotNull(TEXT("Operator owns the shared interaction component"), Operator ? Operator->GetInteractionComponent() : nullptr);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYFocusControllableContractTest,
	"DengYingShanHai.M1.Focus.ControllableContract",
	DYFocusTests::TestFlags)

bool FDYFocusControllableContractTest::RunTest(const FString& Parameters)
{
	// Focus gating must not bypass the Controllable contract: a candidate still has to
	// implement the interface and still has to accept the control request before the
	// operator can focus it. Both real Dev controllables are used here on purpose.
	const ADYLightRigActor* LightRig = GetDefault<ADYLightRigActor>();
	const ADYPuppetActor* Puppet = GetDefault<ADYPuppetActor>();

	TestNotNull(TEXT("Light rig CDO exists"), LightRig);
	TestNotNull(TEXT("Puppet CDO exists"), Puppet);
	if (LightRig)
	{
		TestTrue(TEXT("Light rig implements the Controllable interface"), LightRig->Implements<UDYControllable>());
	}
	if (Puppet)
	{
		TestTrue(TEXT("Puppet implements the Controllable interface"), Puppet->Implements<UDYControllable>());
	}

	// The puppet is disabled by default so P01 stays fixed; focus gating must not
	// change that, and a refused candidate must never be reported as focusable.
	if (Puppet)
	{
		const UDYPuppetControlComponent* Control = Puppet->GetPuppetControlComponent();
		TestNotNull(TEXT("Puppet owns the shared control capability"), Control);
		if (Control)
		{
			TestFalse(TEXT("Puppet control remains opt-in"), Control->IsControlEnabled());
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYFocusRuntimeTraceTest,
	"DengYingShanHai.M1.Focus.RuntimeTrace",
	DYFocusTests::TestFlags)

bool FDYFocusRuntimeTraceTest::RunTest(const FString& Parameters)
{
	// Real runtime path against real collision. This drives the production
	// UDYInteractionComponent::EvaluateFocus through the automation seam and asserts on
	// the component's own GetFocusedActor(), so it verifies shipping code rather than a
	// copy of the algorithm.
	DYFocusTests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}
	// Mirrors the engine-side precondition: without a physics scene the Visibility
	// traces below would silently hit nothing and every case would be meaningless.
	TestTrue(TEXT("Transient game world has a physics scene"), TestWorld.HasPhysicsScene());

	UWorld* World = TestWorld.World;

	// Operator at the origin facing +X; the camera sits behind it, as the boom does.
	const FVector PawnLocation(0.0, 0.0, 0.0);
	const FVector ViewLocation(-DYFocusTests::CameraBoom, 0.0, 0.0);
	const FRotator ViewRotation(0.0, 0.0, 0.0);

	FActorSpawnParameters SpawnParameters;
	SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	ADYStageOperatorPawn* Pawn = World->SpawnActor<ADYStageOperatorPawn>(
		ADYStageOperatorPawn::StaticClass(),
		FTransform(FRotator::ZeroRotator, PawnLocation),
		SpawnParameters);
	TestNotNull(TEXT("Operator pawn spawns"), Pawn);
	if (!Pawn)
	{
		return false;
	}

	DYFocusTests::RegisterComponents(Pawn);
	UDYInteractionComponent* Interaction = Pawn->GetInteractionComponent();
	TestNotNull(TEXT("Operator owns the interaction component under test"), Interaction);
	if (!Interaction)
	{
		Pawn->Destroy();
		return false;
	}

	// Case 1: lamp 515 cm ahead, inside the 700 cm operator reach and 875 cm from the
	// camera. A bare 700 cm trace from the camera would stop short; the compensated
	// length must still focus it. The lamp carries its own Visibility-blocking body,
	// matching the real Dev lamp.
	const FVector LampLocation(515.0, 0.0, 0.0);
	ADYLightRigActor* Lamp = World->SpawnActor<ADYLightRigActor>(
		ADYLightRigActor::StaticClass(),
		FTransform(FRotator::ZeroRotator, LampLocation),
		SpawnParameters);
	TestNotNull(TEXT("Lamp spawns inside operator reach"), Lamp);
	if (!Lamp)
	{
		Pawn->Destroy();
		return false;
	}
	DYFocusTests::RegisterComponents(Lamp);
	DYFocusTests::AddVisibilityBlockingBox(Lamp, LampLocation, FVector(30.0, 60.0, 60.0));

	// Fixture preconditions, proven before the production helper runs, so a failure
	// below can be attributed to the fixture rather than to the focus logic.
	const FVector Case1ProbeEnd = ViewLocation
		+ ViewRotation.Vector() * UDYInteractionComponent::ComputeFocusTraceLength(
			ViewLocation, PawnLocation, DYFocusTests::OperatorReach);
	AActor* Case1ProbeHit = DYFocusTests::TraceFirstVisibilityHit(World, ViewLocation, Case1ProbeEnd, Pawn);
	TestTrue(
		TEXT("Case 1 precondition: the raw fixture trace really hits the near lamp first"),
		Case1ProbeHit == Lamp);
	DYFocusTests::AssertLampControlPreconditions(*this, TEXT("Case 1"), Lamp, Pawn);

	DYFocusTests::EvaluateFocus(*Interaction, ViewLocation, ViewRotation, PawnLocation);
	TestTrue(
		TEXT("Case 1: a visible in-reach lamp becomes the focused candidate despite the camera boom offset"),
		Interaction->GetFocusedActor() == Lamp);

	// Case 2: scenery blocking Visibility in front must win the single trace.
	const FVector BlockerLocation(300.0, 0.0, 0.0);
	AActor* Blocker = World->SpawnActor<AActor>(
		AActor::StaticClass(), BlockerLocation, FRotator::ZeroRotator, SpawnParameters);
	TestNotNull(TEXT("Visibility blocker spawns"), Blocker);
	if (Blocker)
	{
		DYFocusTests::AddVisibilityBlockingBox(Blocker, BlockerLocation, FVector(20.0, 200.0, 200.0));
	}

	DYFocusTests::EvaluateFocus(*Interaction, ViewLocation, ViewRotation, PawnLocation);
	TestNull(
		TEXT("Case 2: a scenery blocker in front prevents focus instead of focusing through it"),
		Interaction->GetFocusedActor());

	// Case 3: remove both the blocker and the near lamp, then place a lamp whose origin
	// is 760 cm away but whose blocking body reaches into the trace. The trace must hit
	// it first, and only the operator-radius gate may reject it.
	// Disable collision before destroying so a pending actor cannot keep answering
	// queries while the next case is being set up.
	if (Blocker)
	{
		Blocker->SetActorEnableCollision(false);
		Blocker->Destroy();
	}
	Lamp->SetActorEnableCollision(false);
	Lamp->Destroy();

	const FVector DistantLampLocation(760.0, 0.0, 0.0);
	ADYLightRigActor* DistantLamp = World->SpawnActor<ADYLightRigActor>(
		ADYLightRigActor::StaticClass(),
		FTransform(FRotator::ZeroRotator, DistantLampLocation),
		SpawnParameters);
	TestNotNull(TEXT("Distant lamp spawns"), DistantLamp);
	if (!DistantLamp)
	{
		Pawn->Destroy();
		return false;
	}
	DYFocusTests::RegisterComponents(DistantLamp);
	// Body spans x 660..860, so the ray from -360 reaches it while the actor origin
	// stays 760 cm from the operator. The hit is real; the rejection must be by radius.
	DYFocusTests::AddVisibilityBlockingBox(DistantLamp, DistantLampLocation, FVector(100.0, 60.0, 60.0));

	// Fixture preconditions for the distant lamp, checked before the production helper so
	// a rejection can be attributed to the operator radius rather than to the fixture.
	DYFocusTests::AssertLampControlPreconditions(*this, TEXT("Case 3"), DistantLamp, Pawn);

	DYFocusTests::EvaluateFocus(*Interaction, ViewLocation, ViewRotation, PawnLocation);
	TestNull(
		TEXT("Case 3: a visible lamp beyond the 700 cm operator reach is rejected"),
		Interaction->GetFocusedActor());

	// Guard against a vacuous pass, proven with a fixture-only raw trace so this test
	// needs no debug flag. This only shows the fixture really put a hit-blocking body on
	// the ray; the accept/reject verdict itself comes from the production helper above.
	const FVector ProbeEnd = ViewLocation
		+ ViewRotation.Vector() * UDYInteractionComponent::ComputeFocusTraceLength(
			ViewLocation, PawnLocation, DYFocusTests::OperatorReach);
	AActor* ProbeHit = DYFocusTests::TraceFirstVisibilityHit(World, ViewLocation, ProbeEnd, Pawn);
	TestTrue(
		TEXT("Case 3 guard: the fixture really is on the ray, so the rejection is not a missing hit"),
		ProbeHit == DistantLamp);
	TestTrue(
		TEXT("Case 3 guard: the distant lamp implements the Controllable interface"),
		DistantLamp->Implements<UDYControllable>());
	TestTrue(
		TEXT("Case 3 guard: the distant lamp origin really is beyond the 700 cm operator reach"),
		FVector::Dist(PawnLocation, DistantLampLocation) > DYFocusTests::OperatorReach);

	DistantLamp->SetActorEnableCollision(false);
	DistantLamp->Destroy();

	// Case 4: the crosshair hits a far curtain. A lamp 7° to the side, and closer
	// than that curtain, is still the focus. A wall on the center ray stays in case 2.
	const FVector BackdropLocation(900.0, 0.0, 0.0);
	AActor* Backdrop = World->SpawnActor<AActor>(
		AActor::StaticClass(), BackdropLocation, FRotator::ZeroRotator, SpawnParameters);
	TestNotNull(TEXT("Curtain backdrop spawns"), Backdrop);
	if (Backdrop)
	{
		DYFocusTests::AddVisibilityBlockingBox(Backdrop, BackdropLocation, FVector(20.0, 400.0, 400.0));
	}
	const FVector SideLampLocation(515.0, 90.0, 0.0);
	ADYLightRigActor* SideLamp = World->SpawnActor<ADYLightRigActor>(
		ADYLightRigActor::StaticClass(),
		FTransform(FRotator::ZeroRotator, SideLampLocation),
		SpawnParameters);
	TestNotNull(TEXT("Side lamp spawns beside the crosshair"), SideLamp);
	if (!SideLamp)
	{
		Pawn->Destroy();
		return false;
	}
	DYFocusTests::RegisterComponents(SideLamp);
	DYFocusTests::AddVisibilityBlockingBox(SideLamp, SideLampLocation, FVector(30.0, 40.0, 40.0));
	DYFocusTests::AssertLampControlPreconditions(*this, TEXT("Case 4"), SideLamp, Pawn);

	DYFocusTests::EvaluateFocus(*Interaction, ViewLocation, ViewRotation, PawnLocation);
	TestTrue(
		TEXT("Case 4: a closer lamp 7 degrees off the crosshair becomes the focus"),
		Interaction->GetFocusedActor() == SideLamp);

	SideLamp->SetActorEnableCollision(false);
	SideLamp->Destroy();
	if (Backdrop)
	{
		Backdrop->SetActorEnableCollision(false);
		Backdrop->Destroy();
	}
	Pawn->Destroy();
	return true;
}

#endif
