#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Animation/AnimInstance.h"
#include "Components/AudioComponent.h"
#include "Components/BoxComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/Level.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/WorldSettings.h"
#include "Player/DYFootstepAudioComponent.h"
#include "Player/DYReenactorOperatorPawn.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"

namespace DYReenactorRuntimeTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext
		| EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter;
	constexpr float DeltaSeconds = 1.0f / 60.0f;
	constexpr double WalkLengthSeconds = 50.0 / 60.0;

	/** One real world update per latent-command update preserves normal animation scheduling. */
	struct FSession
	{
		explicit FSession(FAutomationTestBase& InTest) : Test(InTest)
		{
			if (!GEngine) { return; }
			UWorld::InitializationValues Values;
			Values.CreatePhysicsScene(true).ShouldSimulatePhysics(true).EnableTraceCollision(true)
				.CreateNavigation(false).CreateAISystem(false).CreateFXSystem(false);
			World.Reset(UWorld::CreateWorld(EWorldType::Game, false,
				MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYReenactorRuntimeWorld")),
				GetTransientPackage(), false, ERHIFeatureLevel::Num, &Values));
			if (!World) { return; }
			// The packaged GameEngine also ticks registered contexts; this test alone owns fixed-step updates.
			World->SetShouldTick(false);
			GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World.Get());
			World->InitializeActorsForPlay(FURL());
			AActor* Floor = World->SpawnActor<AActor>();
			if (!Floor) { return; }
			UBoxComponent* FloorCollision = NewObject<UBoxComponent>(Floor);
			Floor->AddInstanceComponent(FloorCollision);
			Floor->SetRootComponent(FloorCollision);
			FloorCollision->SetBoxExtent(FVector(2000.0, 2000.0, 25.0));
			FloorCollision->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
			FloorCollision->SetCollisionObjectType(ECC_WorldStatic);
			FloorCollision->SetCollisionResponseToAllChannels(ECR_Block);
			FloorCollision->RegisterComponent();
			Floor->SetActorLocation(FVector(0.0, 0.0, -25.0));
			FActorSpawnParameters Spawn;
			Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
			Pawn = World->SpawnActor<ADYReenactorOperatorPawn>(StartLocation, FRotator::ZeroRotator, Spawn);
			Controller = World->SpawnActor<APlayerController>();
			if (!Pawn || !Controller) { return; }
			// This fixture has no viewport/LocalPlayer; use the same local designation as GameModeBase.
			Controller->SetAsLocalPlayerController();
			Controller->Possess(Pawn);
			Controller->SetControlRotation(FRotator::ZeroRotator);
			CapturedStartTransform = Pawn->GetActorTransform();
			World->BeginPlay();
			// No GameMode/GameState exists in this isolated world to route StartPlay.
			World->GetWorldSettings()->NotifyBeginPlay();
		}

		~FSession()
		{
			if (World && GEngine)
			{
				World->EndPlay(EEndPlayReason::Quit);
				GEngine->DestroyWorldContext(World.Get());
				World->DestroyWorld(false);
			}
		}

		bool Ready()
		{
			if (!Test.TestNotNull(TEXT("Isolated Game world"), World.Get())
				|| !Test.TestNotNull(TEXT("Runtime Reenactor"), Pawn)
				|| !Test.TestNotNull(TEXT("Possessing controller"), Controller)) { return false; }
			Test.TestTrue(TEXT("World and pawn entered BeginPlay"), World->HasBegunPlay() && Pawn->HasActorBegunPlay());
			Test.TestTrue(TEXT("Isolated world keeps real Game-world behavior"), World->IsGameWorld());
			Test.TestFalse(TEXT("Engine automatic ticking cannot race the fixed-step fixture"), World->ShouldTick());
			Test.TestTrue(TEXT("Controller possesses the candidate"), Controller->GetPawn() == Pawn);
			Test.TestTrue(TEXT("Candidate has a local controller for CharacterMovement"), Pawn->IsLocallyControlled());
			Test.TestTrue(TEXT("Movement tick is registered and enabled"),
				Pawn->GetCharacterMovement()->PrimaryComponentTick.IsTickFunctionRegistered()
				&& Pawn->GetCharacterMovement()->IsComponentTickEnabled());
			bool bLevelWillTick = false;
			for (const FLevelCollection& Collection : World->GetLevelCollections())
			{
				bLevelWillTick |= Collection.GetLevels().Contains(World->PersistentLevel);
			}
			Test.TestTrue(TEXT("Visible persistent level belongs to a ticked level collection"),
				World->PersistentLevel->bIsVisible && bLevelWillTick);
			Test.AddInfo(FString::Printf(TEXT("Fixture: local=%d, movement tick=%d, level collected=%d, captured spawn=%s"),
				Pawn->IsLocallyControlled(), Pawn->GetCharacterMovement()->PrimaryComponentTick.IsTickFunctionRegistered(),
				bLevelWillTick, *CapturedStartTransform.GetLocation().ToString()));
			USkeletalMeshComponent* Visual = Pawn->GetMesh();
			if (!Test.TestNotNull(TEXT("Runtime body"), Visual)
				|| !Test.TestNotNull(TEXT("Runtime AnimInstance"), Visual->GetAnimInstance())) { return false; }
			Test.TestTrue(TEXT("Runtime visual reports ready"), Pawn->HasReenactorVisual());
			Test.TestTrue(TEXT("AnimInstance uses configured movement AnimBP"), Visual->GetAnimInstance()->IsA(Visual->GetAnimClass()));
			Test.TestEqual(TEXT("Runtime body collision is camera-only query"), Visual->GetCollisionEnabled(), ECollisionEnabled::QueryOnly);
			Test.TestEqual(TEXT("Runtime body never blocks interaction traces"),
				Visual->GetCollisionResponseToChannel(ECC_Visibility), ECR_Ignore);
			Test.TestEqual(TEXT("Runtime body blocks the camera probe"),
				Visual->GetCollisionResponseToChannel(ECC_Camera), ECR_Block);
			TArray<USkeletalMeshComponent*> SkeletalComponents;
			Pawn->GetComponents(SkeletalComponents);
			Test.TestEqual(TEXT("Corrected character uses one skeletal mesh layer"), SkeletalComponents.Num(), 1);
			int32 Placeholders = 0;
			TArray<UStaticMeshComponent*> Meshes;
			Pawn->GetComponents(Meshes);
			for (const UStaticMeshComponent* Mesh : Meshes)
			{
				if (!Mesh->GetName().StartsWith(TEXT("DevPlaceholder"))) { continue; }
				++Placeholders;
				Test.TestFalse(TEXT("Inherited placeholder hidden during BeginPlay"), Mesh->IsVisible());
				Test.TestEqual(TEXT("Inherited placeholder has no collision"), Mesh->GetCollisionEnabled(), ECollisionEnabled::NoCollision);
			}
			Test.TestEqual(TEXT("Both placeholders inspected"), Placeholders, 2);
			Test.TestTrue(TEXT("Footstep runtime session active"), Pawn->FootstepAudio->GetFootstepDiagnostics().bRuntimeActive);
			return Test.TestNotNull(TEXT("Runtime footstep voice exists"), Pawn->FootstepAudio->GetFootstepVoice());
		}

		double AnimNumber(const TCHAR* Name)
		{
			UAnimInstance* Anim = Pawn->GetMesh()->GetAnimInstance();
			const FNumericProperty* Property = FindFProperty<FNumericProperty>(Anim->GetClass(), Name);
			if (!Property || !Property->IsFloatingPoint())
			{
				Test.AddError(FString::Printf(TEXT("Movement AnimBP lacks numeric property %s"), Name));
				return -1.0;
			}
			return Property->GetFloatingPointPropertyValue(Property->ContainerPtrToValuePtr<void>(Anim));
		}

		void CheckWalkingPhase()
		{
			const FDYFootstepAudioDiagnostics Clock = Pawn->FootstepAudio->GetFootstepDiagnostics();
			Test.TestTrue(TEXT("Physical movement drives footstep clock"), Clock.bMoving);
			Test.TestTrue(TEXT("Physical movement drives walk blend"), AnimNumber(TEXT("MoveAlpha")) > 0.9);
			const double Expected = FMath::Frac((Clock.bLastStepLeft ? 0.0 : 0.5)
				+ Clock.AccumulatedDistanceCentimeters / (2.0 * Pawn->FootstepAudio->StepDistanceCentimeters)) * WalkLengthSeconds;
			const double Error = FMath::Abs(AnimNumber(TEXT("WalkExplicitTime")) - Expected);
			Test.TestTrue(TEXT("Walk evaluator shares the footstep distance phase"),
				FMath::Min(Error, FMath::Abs(WalkLengthSeconds - Error)) < 0.04);
		}

		bool Update()
		{
			if (Frame == 0 && !Ready()) { return true; }
			// Semantic input reaches CharacterMovement; no fabricated movement callback or displacement.
			if (Frame >= 60 && Frame < 180) { Pawn->ApplyMoveIntent(FVector2D(0.0, 1.0)); }
			if (Frame >= 300 && Frame < 360) { Pawn->ApplyMoveIntent(FVector2D(1.0, 0.0)); }
			World->Tick(LEVELTICK_All, DeltaSeconds);
			++Frame;
			const FDYFootstepAudioDiagnostics Clock = Pawn->FootstepAudio->GetFootstepDiagnostics();
			if (Frame == 60)
			{
				Test.TestTrue(TEXT("Character lands on colliding floor"), Pawn->GetCharacterMovement()->IsMovingOnGround());
				Test.TestTrue(TEXT("Stationary landing emits no footsteps"), Clock.Steps == 0 && !Clock.bMoving);
				Test.TestTrue(TEXT("Stationary AnimBP stays idle"), AnimNumber(TEXT("MoveAlpha")) < 0.05);
				WalkStart = Pawn->GetActorLocation();
			}
			if (Frame == 180)
			{
				WalkDistance = FVector::Dist2D(WalkStart, Pawn->GetActorLocation());
				Test.TestTrue(TEXT("Two seconds of intent produces 180 cm/s physical travel"), WalkDistance > 300.0 && WalkDistance < 365.0);
				Test.TestTrue(TEXT("Real movement updates reach diagnostics"), Clock.MovementUpdates > 100);
				Test.TestTrue(TEXT("Physical travel produces the 75 cm cadence without bursts"), Clock.Steps >= 4 && Clock.Steps <= 6);
				Test.TestEqual(TEXT("Footstep sides alternate from left"), Clock.bLastStepLeft, Clock.Steps % 2 == 1);
				CheckWalkingPhase();
			}
			if (Frame == 210) { StepsAtRest = Clock.Steps; }
			if (Frame == 240)
			{
				Test.TestTrue(TEXT("Released intent physically stops pawn"), Pawn->GetVelocity().Size2D() < 0.01);
				Test.TestFalse(TEXT("Stop clears moving clock"), Clock.bMoving);
				Test.TestEqual(TEXT("Stationary interval emits no further footsteps"), Clock.Steps, StepsAtRest);
				Test.TestEqual(TEXT("Stop clears stride debt"), Clock.AccumulatedDistanceCentimeters, 0.0);
				Test.TestTrue(TEXT("Walk blend fades to idle after stop"), AnimNumber(TEXT("MoveAlpha")) < 0.05);
				Pawn->ResetOperatorToStart(EDYOperatorResetReason::Manual);
				const FDYFootstepAudioDiagnostics ResetClock = Pawn->FootstepAudio->GetFootstepDiagnostics();
				Test.TestTrue(TEXT("Reset restores the actual transform captured at BeginPlay"),
					Pawn->GetActorTransform().Equals(CapturedStartTransform, 0.01));
				Test.TestTrue(TEXT("Reset clears movement velocity"), Pawn->GetVelocity().IsNearlyZero());
				Test.TestEqual(TEXT("Reset delegate consumed once"), ResetClock.ResetEvents, 1);
				Test.TestEqual(TEXT("Reset cannot emit teleport footstep"), ResetClock.Steps, Clock.Steps);
				Test.TestEqual(TEXT("Reset clears phase immediately"), ResetClock.AccumulatedDistanceCentimeters, 0.0);
				Test.TestFalse(TEXT("Reset leaves no moving phase"), ResetClock.bMoving);
			}
			if (Frame == 300)
			{
				Test.TestTrue(TEXT("Reset pawn lands on same floor"), Pawn->GetCharacterMovement()->IsMovingOnGround());
				Test.TestEqual(TEXT("Teleport and landing do not replay old impacts"), Clock.Steps, StepsAtRest);
				RestartLocation = Pawn->GetActorLocation();
			}
			if (Frame < 360) { return false; }
			Test.TestTrue(TEXT("Fixture alone advances six seconds of simulated world time"),
				FMath::IsNearlyEqual(World->GetTimeSeconds(), 360.0 * DeltaSeconds, 0.01));
			Test.TestTrue(TEXT("Reset pawn moves in second direction"), Pawn->GetActorLocation().Y - RestartLocation.Y > 130.0);
			Test.TestTrue(TEXT("Inherited rotation follows new direction"),
				FMath::Abs(FMath::FindDeltaAngleDegrees(Pawn->GetActorRotation().Yaw, 90.0)) < 10.0);
			Test.TestTrue(TEXT("Walking after reset starts fresh clock"), Clock.Steps > StepsAtRest && Clock.MovementStartEvents >= 2);
			CheckWalkingPhase();
			UDYFootstepAudioComponent* Footsteps = Pawn->FootstepAudio;
			UAudioComponent* Voice = Footsteps->GetFootstepVoice();
			Test.AddInfo(FString::Printf(TEXT("Runtime: first travel=%.2fcm, updates=%d, steps=%d, resets=%d; semantic input only, no manual-keyboard claim."),
				WalkDistance, Clock.MovementUpdates, Clock.Steps, Clock.ResetEvents));
			Test.TestTrue(TEXT("Runtime candidate destroys successfully"), Pawn->Destroy());
			Test.TestFalse(TEXT("EndPlay deactivates footsteps"), Footsteps->GetFootstepDiagnostics().bRuntimeActive);
			Test.TestNull(TEXT("EndPlay releases owned voice"), Footsteps->GetFootstepVoice());
			Test.TestTrue(TEXT("Destroyed voice is unregistered"), !Voice || !Voice->IsRegistered());
			return true;
		}

		FAutomationTestBase& Test;
		TStrongObjectPtr<UWorld> World;
		ADYReenactorOperatorPawn* Pawn = nullptr;
		APlayerController* Controller = nullptr;
		const FVector StartLocation = FVector(0.0, 0.0, 110.0);
		FTransform CapturedStartTransform = FTransform::Identity;
		FVector WalkStart = FVector::ZeroVector;
		FVector RestartLocation = FVector::ZeroVector;
		double WalkDistance = 0.0;
		int32 Frame = 0;
		int32 StepsAtRest = 0;
	};
}

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FDYReenactorRuntimeCommand,
	TSharedPtr<DYReenactorRuntimeTests::FSession>, Session);
bool FDYReenactorRuntimeCommand::Update() { return Session->Update(); }

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYReenactorRuntimeLifecycleTest,
	"DengYingShanHai.ReenactorMovement.RuntimeLifecycle", DYReenactorRuntimeTests::Flags)
bool FDYReenactorRuntimeLifecycleTest::RunTest(const FString& Parameters)
{
	ADD_LATENT_AUTOMATION_COMMAND(FDYReenactorRuntimeCommand(MakeShared<DYReenactorRuntimeTests::FSession>(*this)));
	return true;
}

#endif
