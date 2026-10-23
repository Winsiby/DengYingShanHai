#include "Player/DYTheatreOperatorPawn.h"

#include "Animation/AnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Player/DYFootstepAudioComponent.h"
#include "UObject/ConstructorHelpers.h"

ADYTheatreOperatorPawn::ADYTheatreOperatorPawn()
{
	FootstepAudio = CreateDefaultSubobject<UDYFootstepAudioComponent>(TEXT("FootstepAudio"));
	// The formal carrier keeps its original 150 cm stride. Diagnostics drive the
	// visual gait; no sound assets are assigned here, so this adds no audible steps.
	FootstepAudio->StepDistanceCentimeters = 150.0;
	FootstepAudio->bEnableDevelopmentFootsteps = true;

	static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshFinder(
		TEXT("/Game/DengYingShanHai/Dev/ReenactorChestBandRemoval_20261018/SK_DY_Reenactor_NoChestSash_v10.SK_DY_Reenactor_NoChestSash_v10"));
	static ConstructorHelpers::FClassFinder<UAnimInstance> AnimFinder(
		TEXT("/Game/DengYingShanHai/Dev/ReenactorMovement_20261018/Animation/ABP_DYReenactorMovement_V2.ABP_DYReenactorMovement_V2_C"));

	USkeletalMeshComponent* Visual = GetMesh();
	if (MeshFinder.Succeeded())
	{
		Visual->SetSkeletalMeshAsset(MeshFinder.Object);
	}
	if (AnimFinder.Succeeded())
	{
		Visual->SetAnimInstanceClass(AnimFinder.Class);
	}
	Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Visual->SetGenerateOverlapEvents(false);
	Visual->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));
	Visual->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
	Visual->SetCastShadow(true);
}

void ADYTheatreOperatorPawn::BeginPlay()
{
	Super::BeginPlay();

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
