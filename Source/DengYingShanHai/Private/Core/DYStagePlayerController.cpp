#include "Core/DYStagePlayerController.h"

#include "DengYingShanHai.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "InputMappingContext.h"
#include "Camera/PlayerCameraManager.h"
#include "UObject/ConstructorHelpers.h"

namespace DYStageInput
{
	static const TCHAR* ExploreContextPath = TEXT("/Game/DengYingShanHai/Core/Input/IMC_DY_Explore.IMC_DY_Explore");
	static const TCHAR* ManipulateContextPath = TEXT("/Game/DengYingShanHai/Dev/M1/Input/IMC_DY_Manipulate.IMC_DY_Manipulate");
}

ADYStagePlayerController::ADYStagePlayerController()
{
	static ConstructorHelpers::FObjectFinder<UInputMappingContext> ExploreContext(DYStageInput::ExploreContextPath);
	static ConstructorHelpers::FObjectFinder<UInputMappingContext> ManipulateContext(DYStageInput::ManipulateContextPath);
	ExploreMappingContextAsset = ExploreContext.Object;
	ManipulateMappingContextAsset = ManipulateContext.Object;
}

void ADYStagePlayerController::BeginPlay()
{
	Super::BeginPlay();

	if (PlayerCameraManager)
	{
		PlayerCameraManager->ViewPitchMin = -60.0f;
		PlayerCameraManager->ViewPitchMax = 45.0f;
	}

	ApplyExploreMappingContext();
}

void ADYStagePlayerController::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	RemoveManipulateMappingContext();
	RemoveExploreMappingContext();
	Super::EndPlay(EndPlayReason);
}

void ADYStagePlayerController::SetManipulationMode(const bool bEnabled)
{
	if (!IsLocalPlayerController() || bManipulationModeActive == bEnabled)
	{
		return;
	}

	if (bEnabled)
	{
		UEnhancedInputLocalPlayerSubsystem* InputSubsystem = GetEnhancedInputSubsystem();
		UInputMappingContext* ManipulateContext = ManipulateMappingContextAsset;
		if (!InputSubsystem || !ManipulateContext)
		{
			UE_LOG(LogDengYingShanHai, Error, TEXT("Cannot enter Manipulate mode: context or local-player subsystem is unavailable."));
			return;
		}

		RemoveExploreMappingContext();
		AppliedManipulateMappingContext = ManipulateContext;
		InputSubsystem->AddMappingContext(AppliedManipulateMappingContext, ManipulateMappingPriority);
		bManipulationModeActive = true;
		UE_LOG(LogDengYingShanHai, Display, TEXT("Entered Dev Manipulate input mode at priority %d."), ManipulateMappingPriority);
		return;
	}

	RemoveManipulateMappingContext();
	ApplyExploreMappingContext();
	UE_LOG(LogDengYingShanHai, Display, TEXT("Restored Explore input mode."));
}

void ADYStagePlayerController::ApplyExploreMappingContext()
{
	if (!IsLocalPlayerController() || bExploreMappingContextApplied)
	{
		return;
	}

	UEnhancedInputLocalPlayerSubsystem* InputSubsystem = GetEnhancedInputSubsystem();
	if (!InputSubsystem)
	{
		UE_LOG(LogDengYingShanHai, Error, TEXT("Cannot apply Explore input context: no Enhanced Input subsystem for %s."), *GetNameSafe(this));
		return;
	}

	AppliedExploreMappingContext = ExploreMappingContextAsset;
	if (!AppliedExploreMappingContext)
	{
		UE_LOG(LogDengYingShanHai, Error, TEXT("Cannot apply Explore input context: required hard asset reference is null."));
		return;
	}

	InputSubsystem->AddMappingContext(AppliedExploreMappingContext, ExploreMappingPriority);
	bExploreMappingContextApplied = true;

	UE_LOG(LogDengYingShanHai, Log, TEXT("Applied Explore input context once at priority %d."), ExploreMappingPriority);
}

void ADYStagePlayerController::RemoveExploreMappingContext()
{
	if (!bExploreMappingContextApplied || !AppliedExploreMappingContext)
	{
		return;
	}

	if (UEnhancedInputLocalPlayerSubsystem* InputSubsystem = GetEnhancedInputSubsystem())
	{
		InputSubsystem->RemoveMappingContext(AppliedExploreMappingContext);
	}

	bExploreMappingContextApplied = false;
	AppliedExploreMappingContext = nullptr;
}

void ADYStagePlayerController::RemoveManipulateMappingContext()
{
	if (!bManipulationModeActive || !AppliedManipulateMappingContext)
	{
		return;
	}

	if (UEnhancedInputLocalPlayerSubsystem* InputSubsystem = GetEnhancedInputSubsystem())
	{
		InputSubsystem->RemoveMappingContext(AppliedManipulateMappingContext);
	}

	bManipulationModeActive = false;
	AppliedManipulateMappingContext = nullptr;
}

UEnhancedInputLocalPlayerSubsystem* ADYStagePlayerController::GetEnhancedInputSubsystem() const
{
	ULocalPlayer* LocalPlayer = GetLocalPlayer();
	return LocalPlayer ? LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
}
