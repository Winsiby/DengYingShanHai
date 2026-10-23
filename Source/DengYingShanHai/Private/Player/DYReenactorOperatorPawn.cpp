#include "Player/DYReenactorOperatorPawn.h"

#include "Animation/AnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/SpringArmComponent.h"
#include "Player/DYFootstepAudioComponent.h"
#include "Sound/SoundBase.h"
#include "UObject/ConstructorHelpers.h"

ADYReenactorOperatorPawn::ADYReenactorOperatorPawn()
{
	static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshFinder(
		TEXT("/Game/DengYingShanHai/Dev/ReenactorChestBandRemoval_20261018/SK_DY_Reenactor_NoChestSash_v10.SK_DY_Reenactor_NoChestSash_v10"));
	static ConstructorHelpers::FClassFinder<UAnimInstance> AnimFinder(
		TEXT("/Game/DengYingShanHai/Dev/ReenactorMovement_20261018/Animation/ABP_DYReenactorMovement_V2.ABP_DYReenactorMovement_V2_C"));
	static ConstructorHelpers::FObjectFinder<USoundBase> LeftStep(
		TEXT("/Game/DengYingShanHai/Dev/TheatreAudio/Sounds/SFX_DevFootstepA.SFX_DevFootstepA"));
	static ConstructorHelpers::FObjectFinder<USoundBase> RightStep(
		TEXT("/Game/DengYingShanHai/Dev/TheatreAudio/Sounds/SFX_DevFootstepB.SFX_DevFootstepB"));
	ReenactorMeshAsset = MeshFinder.Object;
	ReenactorAnimClass = AnimFinder.Class;

	GetCharacterMovement()->MaxWalkSpeed = 180.0f;
	FootstepAudio->StepDistanceCentimeters = 75.0;
	FootstepAudio->bEnableDevelopmentFootsteps = true;
	FootstepAudio->LeftSound = LeftStep.Object;
	FootstepAudio->RightSound = RightStep.Object;
	if (USpringArmComponent* Boom = GetCameraBoom())
	{
		// Candidate framing for the supplied 177 cm visual; inherited camera logic is unchanged.
		Boom->TargetArmLength = 460.0f;
		Boom->TargetOffset = FVector(0.0f, 0.0f, 20.0f);
		Boom->SocketOffset = FVector(0.0f, 55.0f, 30.0f);
	}

	USkeletalMeshComponent* Visual = GetMesh();
	if (ReenactorMeshAsset)
	{
		Visual->SetSkeletalMeshAsset(ReenactorMeshAsset);
	}
	if (ReenactorAnimClass)
	{
		Visual->SetAnimInstanceClass(ReenactorAnimClass);
	}
	// The capsule does not cover the head. Block only the camera so the spring arm stops outside the body.
	Visual->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Visual->SetCollisionResponseToAllChannels(ECR_Ignore);
	Visual->SetCollisionResponseToChannel(ECC_Camera, ECR_Block);
	Visual->SetGenerateOverlapEvents(false);
	Visual->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));
	Visual->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
	Visual->SetCastShadow(true);
}

void ADYReenactorOperatorPawn::BeginPlay()
{
	Super::BeginPlay();
	HideLegacyPlaceholders();
}

bool ADYReenactorOperatorPawn::HasReenactorVisual() const
{
	const USkeletalMeshComponent* Visual = GetMesh();
	return Visual && Visual->GetSkeletalMeshAsset() && Visual->GetAnimInstance();
}

void ADYReenactorOperatorPawn::HideLegacyPlaceholders()
{
	TArray<UStaticMeshComponent*> Components;
	GetComponents<UStaticMeshComponent>(Components);
	for (UStaticMeshComponent* Component : Components)
	{
		if (Component && Component->GetName().StartsWith(TEXT("DevPlaceholder")))
		{
			Component->SetVisibility(false, true);
			Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		}
	}
}
