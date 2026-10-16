#include "Player/DYStageOperatorPawn.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Core/DYStagePlayerController.h"
#include "DengYingShanHai.h"
#include "EnhancedInputComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputAction.h"
#include "InputActionValue.h"
#include "Interaction/DYInteractionComponent.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UObject/ConstructorHelpers.h"

namespace DYOperatorInput
{
	static const TCHAR* MoveActionPath = TEXT("/Game/DengYingShanHai/Core/Input/IA_DY_Move.IA_DY_Move");
	static const TCHAR* LookActionPath = TEXT("/Game/DengYingShanHai/Core/Input/IA_DY_Look.IA_DY_Look");
	static const TCHAR* ResetActionPath = TEXT("/Game/DengYingShanHai/Core/Input/IA_DY_ResetOperator.IA_DY_ResetOperator");
	static const TCHAR* InteractActionPath = TEXT("/Game/DengYingShanHai/Dev/M1/Input/IA_DY_Interact.IA_DY_Interact");
	static const TCHAR* ManipulateActionPath = TEXT("/Game/DengYingShanHai/Dev/M1/Input/IA_DY_Manipulate.IA_DY_Manipulate");
	static const TCHAR* ResetControlledActionPath = TEXT("/Game/DengYingShanHai/Dev/M1/Input/IA_DY_ResetControlled.IA_DY_ResetControlled");
}

ADYStageOperatorPawn::ADYStageOperatorPawn()
{
	PrimaryActorTick.bCanEverTick = false;

	GetCapsuleComponent()->InitCapsuleSize(42.0f, 96.0f);

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->bOrientRotationToMovement = true;
	Movement->RotationRate = FRotator(0.0f, 480.0f, 0.0f);
	Movement->MaxWalkSpeed = 360.0f;
	Movement->MinAnalogWalkSpeed = 20.0f;
	Movement->BrakingDecelerationWalking = 1800.0f;
	Movement->AirControl = 0.25f;

	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 360.0f;
	CameraBoom->TargetOffset = FVector(0.0f, 0.0f, 70.0f);
	CameraBoom->SocketOffset = FVector(0.0f, 55.0f, 10.0f);
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bDoCollisionTest = true;
	CameraBoom->ProbeSize = 12.0f;
	CameraBoom->ProbeChannel = ECC_Camera;
	CameraBoom->bEnableCameraLag = false;
	CameraBoom->bEnableCameraRotationLag = false;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;
	FollowCamera->FieldOfView = 70.0f;

	InteractionComponent = CreateDefaultSubobject<UDYInteractionComponent>(TEXT("InteractionComponent"));

	DevPlaceholderBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DevPlaceholderBody"));
	DevPlaceholderBody->SetupAttachment(RootComponent);
	DevPlaceholderBody->SetRelativeLocation(FVector(0.0f, 0.0f, -20.0f));
	DevPlaceholderBody->SetRelativeScale3D(FVector(0.68f, 0.68f, 1.25f));
	DevPlaceholderBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	DevPlaceholderHead = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DevPlaceholderHead"));
	DevPlaceholderHead->SetupAttachment(RootComponent);
	DevPlaceholderHead->SetRelativeLocation(FVector(0.0f, 0.0f, 62.0f));
	DevPlaceholderHead->SetRelativeScale3D(FVector(0.34f));
	DevPlaceholderHead->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> PlaceholderMaterial(TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	if (CylinderMesh.Succeeded())
	{
		DevPlaceholderBody->SetStaticMesh(CylinderMesh.Object);
	}
	if (SphereMesh.Succeeded())
	{
		DevPlaceholderHead->SetStaticMesh(SphereMesh.Object);
	}
	if (PlaceholderMaterial.Succeeded())
	{
		DevPlaceholderBody->SetMaterial(0, PlaceholderMaterial.Object);
		DevPlaceholderHead->SetMaterial(0, PlaceholderMaterial.Object);
	}

	static ConstructorHelpers::FObjectFinder<UInputAction> MoveAction(DYOperatorInput::MoveActionPath);
	static ConstructorHelpers::FObjectFinder<UInputAction> LookAction(DYOperatorInput::LookActionPath);
	static ConstructorHelpers::FObjectFinder<UInputAction> ResetAction(DYOperatorInput::ResetActionPath);
	static ConstructorHelpers::FObjectFinder<UInputAction> InteractAction(DYOperatorInput::InteractActionPath);
	static ConstructorHelpers::FObjectFinder<UInputAction> ManipulateAction(DYOperatorInput::ManipulateActionPath);
	static ConstructorHelpers::FObjectFinder<UInputAction> ResetControlledAction(DYOperatorInput::ResetControlledActionPath);
	MoveActionAsset = MoveAction.Object;
	LookActionAsset = LookAction.Object;
	ResetActionAsset = ResetAction.Object;
	InteractActionAsset = InteractAction.Object;
	ManipulateActionAsset = ManipulateAction.Object;
	ResetControlledActionAsset = ResetControlledAction.Object;
}

void ADYStageOperatorPawn::BeginPlay()
{
	Super::BeginPlay();
	InteractionComponent->OnControlStateChanged.AddUniqueDynamic(this, &ADYStageOperatorPawn::HandleControlStateChanged);
	CaptureInitialState();
}

void ADYStageOperatorPawn::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	InteractionComponent->OnControlStateChanged.RemoveDynamic(this, &ADYStageOperatorPawn::HandleControlStateChanged);
	InteractionComponent->EndActiveControl();
	if (ADYStagePlayerController* StageController = Cast<ADYStagePlayerController>(Controller))
	{
		StageController->SetManipulationMode(false);
	}
	Super::EndPlay(EndPlayReason);
}

void ADYStageOperatorPawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	if (BoundInputComponent.Get() == PlayerInputComponent)
	{
		UE_LOG(LogDengYingShanHai, Warning, TEXT("Skipped duplicate input binding for %s."), *GetNameSafe(this));
		return;
	}

	UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!EnhancedInputComponent)
	{
		UE_LOG(LogDengYingShanHai, Error, TEXT("%s requires UEnhancedInputComponent."), *GetNameSafe(this));
		return;
	}

	if (!HasCompleteInputConfiguration())
	{
		return;
	}

	EnhancedInputComponent->BindAction(MoveActionAsset, ETriggerEvent::Triggered, this, &ADYStageOperatorPawn::HandleMoveInput);
	EnhancedInputComponent->BindAction(LookActionAsset, ETriggerEvent::Triggered, this, &ADYStageOperatorPawn::HandleLookInput);
	EnhancedInputComponent->BindAction(ResetActionAsset, ETriggerEvent::Started, this, &ADYStageOperatorPawn::HandleResetInput);
	EnhancedInputComponent->BindAction(InteractActionAsset, ETriggerEvent::Started, this, &ADYStageOperatorPawn::HandleInteractInput);
	EnhancedInputComponent->BindAction(ManipulateActionAsset, ETriggerEvent::Triggered, this, &ADYStageOperatorPawn::HandleManipulateInput);
	EnhancedInputComponent->BindAction(ResetControlledActionAsset, ETriggerEvent::Started, this, &ADYStageOperatorPawn::HandleResetControlledInput);
	BoundInputComponent = PlayerInputComponent;
}

void ADYStageOperatorPawn::ApplyMoveIntent(const FVector2D& MovementIntent)
{
	if (!Controller || MovementIntent.IsNearlyZero())
	{
		return;
	}

	const FRotator ControlRotation = Controller->GetControlRotation();
	const FRotator YawOnlyRotation(0.0f, ControlRotation.Yaw, 0.0f);
	const FVector ForwardDirection = FRotationMatrix(YawOnlyRotation).GetUnitAxis(EAxis::X);
	const FVector RightDirection = FRotationMatrix(YawOnlyRotation).GetUnitAxis(EAxis::Y);

	AddMovementInput(ForwardDirection, MovementIntent.Y);
	AddMovementInput(RightDirection, MovementIntent.X);
}

void ADYStageOperatorPawn::ApplyLookIntent(const FVector2D& LookIntent)
{
	if (!Controller || LookIntent.IsNearlyZero())
	{
		return;
	}

	AddControllerYawInput(LookIntent.X);
	AddControllerPitchInput(LookIntent.Y);
}

void ADYStageOperatorPawn::ResetOperatorToStart(const EDYOperatorResetReason Reason)
{
	if (!bHasInitialState)
	{
		UE_LOG(LogDengYingShanHai, Error, TEXT("Cannot reset %s before its initial state is captured."), *GetNameSafe(this));
		return;
	}

	InteractionComponent->EndActiveControl();

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->StopMovementImmediately();
	Movement->ClearAccumulatedForces();

	SetActorTransform(InitialActorTransform, false, nullptr, ETeleportType::TeleportPhysics);
	Movement->SetMovementMode(MOVE_Falling);

	if (Controller)
	{
		Controller->SetControlRotation(InitialControlRotation);
	}

	++OperatorResetCount;
	OnOperatorReset.Broadcast(Reason, OperatorResetCount);

	UE_LOG(LogDengYingShanHai, Display, TEXT("Operator reset to start. Reason=%s Count=%d"),
		Reason == EDYOperatorResetReason::Manual ? TEXT("Manual") : TEXT("OutOfWorld"),
		OperatorResetCount);
}

void ADYStageOperatorPawn::FellOutOfWorld(const UDamageType& DamageType)
{
	if (bHasInitialState)
	{
		ResetOperatorToStart(EDYOperatorResetReason::OutOfWorld);
		return;
	}

	Super::FellOutOfWorld(DamageType);
}

void ADYStageOperatorPawn::HandleMoveInput(const FInputActionValue& Value)
{
	ApplyMoveIntent(Value.Get<FVector2D>());
}

void ADYStageOperatorPawn::HandleLookInput(const FInputActionValue& Value)
{
	ApplyLookIntent(Value.Get<FVector2D>());
}

void ADYStageOperatorPawn::HandleResetInput(const FInputActionValue& Value)
{
	ResetOperatorToStart(EDYOperatorResetReason::Manual);
}

void ADYStageOperatorPawn::HandleInteractInput(const FInputActionValue& Value)
{
#if !UE_BUILD_SHIPPING
	// Key-level evidence: this fires from the Interact action's Started event, so it only
	// appears when the input system actually delivered the key. Gated on the same
	// explicit -DYDebug switch as the rest of the diagnostics.
	if (FParse::Param(FCommandLine::Get(), TEXT("DYDebug")))
	{
		UE_LOG(
			LogDengYingShanHai,
			Display,
			TEXT("InputDebug InteractStarted=1 FocusedActor=%s IsControlling=%d"),
			(InteractionComponent && InteractionComponent->GetFocusedActor())
				? *InteractionComponent->GetFocusedActor()->GetName()
				: TEXT("None"),
			(InteractionComponent && InteractionComponent->IsControlling()) ? 1 : 0);
	}
#endif

	InteractionComponent->ToggleControl();
}

void ADYStageOperatorPawn::HandleManipulateInput(const FInputActionValue& Value)
{
	const UWorld* World = GetWorld();
	InteractionComponent->ApplyPrimaryAxis(Value.Get<float>(), World ? World->GetDeltaSeconds() : 0.0);
}

void ADYStageOperatorPawn::HandleResetControlledInput(const FInputActionValue& Value)
{
	InteractionComponent->ResetActiveControl();
}

void ADYStageOperatorPawn::HandleControlStateChanged(AActor* ControlledActor, const bool bIsControlling)
{
	if (ADYStagePlayerController* StageController = Cast<ADYStagePlayerController>(Controller))
	{
		StageController->SetManipulationMode(bIsControlling);
	}
}

void ADYStageOperatorPawn::CaptureInitialState()
{
	InitialActorTransform = GetActorTransform();
	InitialControlRotation = Controller ? Controller->GetControlRotation() : GetActorRotation();
	bHasInitialState = true;
}

bool ADYStageOperatorPawn::HasCompleteInputConfiguration() const
{
	const bool bComplete = MoveActionAsset && LookActionAsset && ResetActionAsset
		&& InteractActionAsset && ManipulateActionAsset && ResetControlledActionAsset;
	if (!bComplete)
	{
		UE_LOG(LogDengYingShanHai, Error, TEXT("Required hard input references are incomplete. Move=%s Look=%s Reset=%s Interact=%s Manipulate=%s ResetControlled=%s"),
			*GetNameSafe(MoveActionAsset),
			*GetNameSafe(LookActionAsset),
			*GetNameSafe(ResetActionAsset),
			*GetNameSafe(InteractActionAsset),
			*GetNameSafe(ManipulateActionAsset),
			*GetNameSafe(ResetControlledActionAsset));
	}

	return bComplete;
}
