#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Core/DYStageGameMode.h"
#include "Core/DYStagePlayerController.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EnhancedActionKeyMapping.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputAction.h"
#include "InputCoreTypes.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "Player/DYFootstepAudioComponent.h"
#include "Player/DYStageOperatorPawn.h"
#include "Player/DYTheatreOperatorPawn.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "UObject/Package.h"
#include "UObject/UObjectGlobals.h"

namespace DYPhase1Tests
{
	constexpr EAutomationTestFlags TestFlags =
		EAutomationTestFlags::EditorContext |
		EAutomationTestFlags::EngineFilter;

	const TCHAR* MoveActionPath = TEXT("/Game/DengYingShanHai/Core/Input/IA_DY_Move.IA_DY_Move");
	const TCHAR* LookActionPath = TEXT("/Game/DengYingShanHai/Core/Input/IA_DY_Look.IA_DY_Look");
	const TCHAR* ResetActionPath = TEXT("/Game/DengYingShanHai/Core/Input/IA_DY_ResetOperator.IA_DY_ResetOperator");
	const TCHAR* InteractActionPath = TEXT("/Game/DengYingShanHai/Dev/M1/Input/IA_DY_Interact.IA_DY_Interact");
	const TCHAR* ExploreContextPath = TEXT("/Game/DengYingShanHai/Core/Input/IMC_DY_Explore.IMC_DY_Explore");

	const FEnhancedActionKeyMapping* FindMapping(
		const UInputMappingContext* Context,
		const UInputAction* Action,
		const FKey& Key)
	{
		if (!Context || !Action)
		{
			return nullptr;
		}

		return Context->GetMappings().FindByPredicate(
			[Action, &Key](const FEnhancedActionKeyMapping& Mapping)
			{
				return Mapping.Action == Action && Mapping.Key == Key;
			});
	}

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
				TEXT("DYPhase1ResetWorld"),
				EUniqueObjectNameOptions::GloballyUnique);
			FWorldContext& WorldContext = GEngine->CreateNewWorldContext(EWorldType::Game);
			World = UWorld::CreateWorld(EWorldType::Game, false, WorldName, GetTransientPackage());
			if (World)
			{
				World->AddToRoot();
				WorldContext.SetCurrentWorld(World);
			}
		}

		~FScopedTestWorld()
		{
			if (!World || !GEngine)
			{
				return;
			}

			if (World->AreActorsInitialized())
			{
				World->EndPlay(EEndPlayReason::Quit);
			}
			GEngine->DestroyWorldContext(World);
			World->DestroyWorld(false);
			World->RemoveFromRoot();
			World = nullptr;
		}

		UWorld* World = nullptr;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYPhase1ClassDefaultsTest,
	"DengYingShanHai.Phase1.ClassDefaults",
	DYPhase1Tests::TestFlags)

bool FDYPhase1ClassDefaultsTest::RunTest(const FString& Parameters)
{
	const ADYStageGameMode* GameMode = GetDefault<ADYStageGameMode>();
	TestNotNull(TEXT("GameMode CDO exists"), GameMode);
	if (!GameMode)
	{
		return false;
	}

	TestTrue(
		TEXT("GameMode selects the formal reenactor operator pawn"),
		GameMode->DefaultPawnClass == ADYTheatreOperatorPawn::StaticClass());
	TestTrue(
		TEXT("GameMode selects the stage player controller"),
		GameMode->PlayerControllerClass == ADYStagePlayerController::StaticClass());

	const ADYTheatreOperatorPawn* FormalPawn = GetDefault<ADYTheatreOperatorPawn>();
	TestNotNull(TEXT("Formal reenactor pawn CDO exists"), FormalPawn);
	if (FormalPawn)
	{
		TestNotNull(
			TEXT("Formal reenactor mesh assigned"),
			FormalPawn->GetMesh()->GetSkeletalMeshAsset());
		TestNotNull(
			TEXT("Formal reenactor AnimBP assigned"),
			FormalPawn->GetMesh()->GetAnimClass());
		TestEqual(
			TEXT("Formal movement speed remains 360 cm/s"),
			FormalPawn->GetCharacterMovement()->MaxWalkSpeed,
			360.0f);
		TestEqual(
			TEXT("Formal camera arm remains 360 cm"),
			FormalPawn->GetCameraBoom()->TargetArmLength,
			360.0f);
		TestEqual(
			TEXT("Formal stride remains 150 cm"),
			FormalPawn->FootstepAudio->StepDistanceCentimeters,
			150.0);
	}

	const ADYStagePlayerController* Controller = GetDefault<ADYStagePlayerController>();
	TestNotNull(TEXT("PlayerController CDO exists"), Controller);
	if (Controller)
	{
		TestEqual(TEXT("Explore mapping priority is zero"), Controller->GetExploreMappingPriority(), 0);
		const UInputMappingContext* ExploreContext = Controller->GetExploreMappingContextAsset();
		TestNotNull(TEXT("Explore mapping context is a hard cook dependency"), ExploreContext);
		if (ExploreContext)
		{
			TestEqual(
				TEXT("Explore mapping context uses the project asset"),
				ExploreContext->GetPathName(),
				FString(DYPhase1Tests::ExploreContextPath));
		}
	}

	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYPhase1OperatorComponentsTest,
	"DengYingShanHai.Phase1.OperatorComponents",
	DYPhase1Tests::TestFlags)

bool FDYPhase1OperatorComponentsTest::RunTest(const FString& Parameters)
{
	const ADYStageOperatorPawn* Pawn = GetDefault<ADYStageOperatorPawn>();
	TestNotNull(TEXT("Operator pawn CDO exists"), Pawn);
	if (!Pawn)
	{
		return false;
	}

	const UCapsuleComponent* Capsule = Pawn->GetCapsuleComponent();
	const UCharacterMovementComponent* Movement = Pawn->GetCharacterMovement();
	const USpringArmComponent* Boom = Pawn->GetCameraBoom();
	const UCameraComponent* Camera = Pawn->GetFollowCamera();

	TestNotNull(TEXT("Capsule exists"), Capsule);
	TestNotNull(TEXT("Character movement exists"), Movement);
	TestNotNull(TEXT("Spring arm exists"), Boom);
	TestNotNull(TEXT("Follow camera exists"), Camera);
	TestNotNull(TEXT("Move action is a hard cook dependency"), Pawn->GetMoveActionAsset());
	TestNotNull(TEXT("Look action is a hard cook dependency"), Pawn->GetLookActionAsset());
	TestNotNull(TEXT("Reset action is a hard cook dependency"), Pawn->GetResetActionAsset());
	TestNotNull(TEXT("Interact action is a hard cook dependency"), Pawn->GetInteractActionAsset());
	TestNotNull(TEXT("Manipulate action is a hard cook dependency"), Pawn->GetManipulateActionAsset());
	TestNotNull(TEXT("Controlled reset action is a hard cook dependency"), Pawn->GetResetControlledActionAsset());

	if (Capsule)
	{
		TestEqual(TEXT("Capsule radius"), Capsule->GetUnscaledCapsuleRadius(), 42.0f);
		TestEqual(TEXT("Capsule half height"), Capsule->GetUnscaledCapsuleHalfHeight(), 96.0f);
	}
	if (Movement)
	{
		TestTrue(TEXT("Movement faces travel direction"), Movement->bOrientRotationToMovement);
		TestEqual(TEXT("Maximum walk speed"), Movement->MaxWalkSpeed, 360.0f);
	}
	if (Boom)
	{
		TestEqual(TEXT("Camera boom arm length"), Boom->TargetArmLength, 360.0f);
		TestTrue(TEXT("Camera boom uses controller rotation"), Boom->bUsePawnControlRotation);
		TestTrue(TEXT("Camera collision is enabled"), Boom->bDoCollisionTest);
		TestEqual(TEXT("Camera collision probe size"), Boom->ProbeSize, 28.0f);
		TestEqual(TEXT("Camera collision channel"), Boom->ProbeChannel, ECC_Camera);
		TestFalse(TEXT("Camera position lag is disabled"), Boom->bEnableCameraLag);
		TestFalse(TEXT("Camera rotation lag is disabled"), Boom->bEnableCameraRotationLag);
	}
	if (Camera && Boom)
	{
		TestTrue(TEXT("Follow camera is attached to the spring arm"), Camera->GetAttachParent() == Boom);
		TestEqual(TEXT("Follow camera uses the spring-arm socket"), Camera->GetAttachSocketName(), USpringArmComponent::SocketName);
		TestFalse(TEXT("Follow camera does not rotate independently from pawn control"), Camera->bUsePawnControlRotation);
		TestEqual(TEXT("Follow camera field of view"), Camera->FieldOfView, 70.0f);
	}

	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYPhase1InputContractTest,
	"DengYingShanHai.Phase1.InputContract",
	DYPhase1Tests::TestFlags)

bool FDYPhase1InputContractTest::RunTest(const FString& Parameters)
{
	const UInputAction* Move = LoadObject<UInputAction>(nullptr, DYPhase1Tests::MoveActionPath);
	const UInputAction* Look = LoadObject<UInputAction>(nullptr, DYPhase1Tests::LookActionPath);
	const UInputAction* Reset = LoadObject<UInputAction>(nullptr, DYPhase1Tests::ResetActionPath);
	const UInputAction* Interact = LoadObject<UInputAction>(nullptr, DYPhase1Tests::InteractActionPath);
	const UInputMappingContext* Context = LoadObject<UInputMappingContext>(nullptr, DYPhase1Tests::ExploreContextPath);

	TestNotNull(TEXT("Move input action loads"), Move);
	TestNotNull(TEXT("Look input action loads"), Look);
	TestNotNull(TEXT("Reset input action loads"), Reset);
	TestNotNull(TEXT("Interact input action loads"), Interact);
	TestNotNull(TEXT("Explore mapping context loads"), Context);
	if (!Move || !Look || !Reset || !Interact || !Context)
	{
		return false;
	}

	TestEqual(TEXT("Move action is Axis2D"), Move->ValueType, EInputActionValueType::Axis2D);
	TestEqual(TEXT("Look action is Axis2D"), Look->ValueType, EInputActionValueType::Axis2D);
	TestEqual(TEXT("Reset action is Boolean"), Reset->ValueType, EInputActionValueType::Boolean);
	TestEqual(TEXT("Interact action is Boolean"), Interact->ValueType, EInputActionValueType::Boolean);
	TestEqual(TEXT("Exactly seven current development mappings exist"), Context->GetMappings().Num(), 7);

	const FEnhancedActionKeyMapping* W = DYPhase1Tests::FindMapping(Context, Move, EKeys::W);
	const FEnhancedActionKeyMapping* S = DYPhase1Tests::FindMapping(Context, Move, EKeys::S);
	const FEnhancedActionKeyMapping* A = DYPhase1Tests::FindMapping(Context, Move, EKeys::A);
	const FEnhancedActionKeyMapping* D = DYPhase1Tests::FindMapping(Context, Move, EKeys::D);
	const FEnhancedActionKeyMapping* Mouse = DYPhase1Tests::FindMapping(Context, Look, EKeys::Mouse2D);
	const FEnhancedActionKeyMapping* R = DYPhase1Tests::FindMapping(Context, Reset, EKeys::R);
	const FEnhancedActionKeyMapping* E = DYPhase1Tests::FindMapping(Context, Interact, EKeys::E);

	TestNotNull(TEXT("W maps to Move"), W);
	TestNotNull(TEXT("S maps to Move"), S);
	TestNotNull(TEXT("A maps to Move"), A);
	TestNotNull(TEXT("D maps to Move"), D);
	TestNotNull(TEXT("Mouse2D maps to Look"), Mouse);
	TestNotNull(TEXT("R maps to Reset"), R);
	TestNotNull(TEXT("E maps to Interact"), E);

	if (W)
	{
		TestEqual(TEXT("W has one modifier"), W->Modifiers.Num(), 1);
		const UInputModifierSwizzleAxis* Swizzle = W->Modifiers.Num() == 1
			? Cast<UInputModifierSwizzleAxis>(W->Modifiers[0])
			: nullptr;
		TestNotNull(TEXT("W swizzles X input onto Y"), Swizzle);
		if (Swizzle)
		{
			TestEqual(TEXT("W uses YXZ swizzle"), Swizzle->Order, EInputAxisSwizzle::YXZ);
		}
	}
	if (S)
	{
		TestEqual(TEXT("S has Negate then Swizzle"), S->Modifiers.Num(), 2);
		if (S->Modifiers.Num() == 2)
		{
			TestTrue(TEXT("S modifier 0 is Negate"), S->Modifiers[0]->IsA<UInputModifierNegate>());
			const UInputModifierSwizzleAxis* Swizzle = Cast<UInputModifierSwizzleAxis>(S->Modifiers[1]);
			TestNotNull(TEXT("S modifier 1 is Swizzle"), Swizzle);
			if (Swizzle)
			{
				TestEqual(TEXT("S uses YXZ swizzle"), Swizzle->Order, EInputAxisSwizzle::YXZ);
			}
		}
	}
	if (A)
	{
		TestEqual(TEXT("A has one modifier"), A->Modifiers.Num(), 1);
		if (A->Modifiers.Num() == 1)
		{
			TestTrue(TEXT("A modifier is Negate"), A->Modifiers[0]->IsA<UInputModifierNegate>());
		}
	}
	if (D)
	{
		TestEqual(TEXT("D has no modifier"), D->Modifiers.Num(), 0);
	}
	if (Mouse)
	{
		TestEqual(TEXT("Mouse2D has no mapping modifier"), Mouse->Modifiers.Num(), 0);
	}
	if (R)
	{
		TestEqual(TEXT("R has no mapping modifier"), R->Modifiers.Num(), 0);
	}
	if (E)
	{
		TestEqual(TEXT("E has no mapping modifier"), E->Modifiers.Num(), 0);
	}

	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYPhase1ResetContractTest,
	"DengYingShanHai.Phase1.ResetContract",
	DYPhase1Tests::TestFlags)

bool FDYPhase1ResetContractTest::RunTest(const FString& Parameters)
{
	DYPhase1Tests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}

	const FTransform StartTransform(FRotator(0.0, 35.0, 0.0), FVector(125.0, -80.0, 240.0));
	FActorSpawnParameters SpawnParameters;
	SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	ADYStageOperatorPawn* Pawn = TestWorld.World->SpawnActor<ADYStageOperatorPawn>(
		ADYStageOperatorPawn::StaticClass(),
		StartTransform,
		SpawnParameters);
	TestNotNull(TEXT("Operator pawn spawns"), Pawn);
	if (!Pawn)
	{
		return false;
	}

	Pawn->DispatchBeginPlay();
	Pawn->SetActorLocationAndRotation(FVector(700.0, 400.0, -200.0), FRotator(0.0, -120.0, 0.0), false, nullptr, ETeleportType::TeleportPhysics);
	Pawn->GetCharacterMovement()->Velocity = FVector(100.0, 50.0, -300.0);
	Pawn->ResetOperatorToStart(EDYOperatorResetReason::Manual);

	TestTrue(TEXT("Reset restores the captured transform"), Pawn->GetActorTransform().Equals(StartTransform, 0.01f));
	TestTrue(TEXT("Reset clears movement velocity"), Pawn->GetCharacterMovement()->Velocity.IsNearlyZero());
	TestEqual(TEXT("Reset restores falling movement mode"), Pawn->GetCharacterMovement()->MovementMode, MOVE_Falling);
	TestEqual(TEXT("Reset count increments exactly once"), Pawn->GetOperatorResetCount(), 1);

	Pawn->Destroy();
	return true;
}

#endif
