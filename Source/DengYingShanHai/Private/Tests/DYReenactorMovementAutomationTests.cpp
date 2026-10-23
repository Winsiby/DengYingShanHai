#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Core/DYReenactorStageGameMode.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/HUD.h"
#include "GameFramework/SpringArmComponent.h"
#include "Player/DYFootstepAudioComponent.h"
#include "Player/DYReenactorOperatorPawn.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"

namespace DYReenactorMovementTests
{
	constexpr EAutomationTestFlags Flags =
		EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYReenactorMovementDefaultsTest,
	"DengYingShanHai.ReenactorMovement.CompiledDefaults",
	DYReenactorMovementTests::Flags)

bool FDYReenactorMovementDefaultsTest::RunTest(const FString& Parameters)
{
	const ADYReenactorOperatorPawn* Pawn = GetDefault<ADYReenactorOperatorPawn>();
	TestNotNull(TEXT("Candidate Pawn CDO exists"), Pawn);
	if (!Pawn)
	{
		return false;
	}

	TestEqual(TEXT("Candidate speed is 180 cm/s"),
		Pawn->GetCharacterMovement()->MaxWalkSpeed, 180.0f);
	TestEqual(TEXT("Candidate step distance is 75 cm"),
		Pawn->FootstepAudio->StepDistanceCentimeters, 75.0);
	TestTrue(TEXT("Footstep session is enabled"), Pawn->FootstepAudio->bEnableDevelopmentFootsteps);
	TestNotNull(TEXT("Left footstep sound assigned"), Pawn->FootstepAudio->LeftSound.Get());
	TestNotNull(TEXT("Right footstep sound assigned"), Pawn->FootstepAudio->RightSound.Get());

	const USkeletalMeshComponent* Visual = Pawn->GetMesh();
	TestNotNull(TEXT("Character mesh component exists"), Visual);
	if (!Visual)
	{
		return false;
	}
	TestNotNull(TEXT("Supplied Reenactor mesh assigned"), Visual->GetSkeletalMeshAsset());
	TestNotNull(TEXT("Movement AnimBP assigned"), Pawn->GetMesh()->GetAnimClass());
	TArray<USkeletalMeshComponent*> SkeletalComponents;
	Pawn->GetComponents(SkeletalComponents);
	TestEqual(TEXT("Single corrected mesh is the only visual layer"), SkeletalComponents.Num(), 1);
	TestEqual(TEXT("Visual feet align to capsule bottom"),
		Visual->GetRelativeLocation().Z, -96.0);
	TestEqual(TEXT("Supplied mesh faces actor +X"),
		Visual->GetRelativeRotation().Yaw, -90.0);
	// The capsule stops the walk; the visual only blocks the camera probe so the spring arm
	// cannot sit inside the head. Nothing on the visual may block movement or interaction traces.
	TestEqual(TEXT("Visual collision is camera-only query"),
		Visual->GetCollisionEnabled(), ECollisionEnabled::QueryOnly);
	TestEqual(TEXT("Visual ignores world geometry"),
		Visual->GetCollisionResponseToChannel(ECC_Visibility), ECR_Ignore);
	TestEqual(TEXT("Visual blocks the camera probe"),
		Visual->GetCollisionResponseToChannel(ECC_Camera), ECR_Block);

	const USpringArmComponent* Boom = Pawn->GetCameraBoom();
	TestNotNull(TEXT("Camera boom exists"), Boom);
	if (Boom)
	{
		TestEqual(TEXT("Candidate camera arm is 460 cm"), Boom->TargetArmLength, 460.0f);
		TestEqual(TEXT("Candidate camera target is lowered"), Boom->TargetOffset.Z, 20.0);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYReenactorMovementGameModeTest,
	"DengYingShanHai.ReenactorMovement.GameModeComposition",
	DYReenactorMovementTests::Flags)

bool FDYReenactorMovementGameModeTest::RunTest(const FString& Parameters)
{
	const ADYReenactorStageGameMode* GameMode = GetDefault<ADYReenactorStageGameMode>();
	TestNotNull(TEXT("Candidate GameMode CDO exists"), GameMode);
	if (!GameMode)
	{
		return false;
	}
	TestEqual(TEXT("Candidate GameMode owns the new Pawn"),
		GameMode->DefaultPawnClass.Get(), ADYReenactorOperatorPawn::StaticClass());
	TestNull(TEXT("Movement lab hides the generic Dev HUD"), GameMode->HUDClass.Get());
	return true;
}

#endif
