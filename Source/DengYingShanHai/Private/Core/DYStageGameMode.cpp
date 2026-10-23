#include "Core/DYStageGameMode.h"

#include "DengYingShanHai.h"

#include "Core/DYReleaseEntryPlayerController.h"
#include "Core/DYStagePlayerController.h"
#include "Player/DYStageOperatorPawn.h"
#include "Player/DYTheatreOperatorPawn.h"
#include "Engine/World.h"
#include "Stage/DYStagePresentation.h"

#if !UE_BUILD_SHIPPING
#include "UI/DYDevInteractionHUD.h"
#endif

ADYStageGameMode::ADYStageGameMode()
{
	DefaultPawnClass = ADYTheatreOperatorPawn::StaticClass();
	PlayerControllerClass = ADYStagePlayerController::StaticClass();

#if !UE_BUILD_SHIPPING
	// Development readout so the player can see whether the object under the crosshair
	// is interactive. Only this ASSIGNMENT is guarded: in Shipping the default
	// GameMode does not mount the HUD, but the class and its strings may still be
	// linked into the binary. The formal art UI replaces this class later.
	HUDClass = ADYDevInteractionHUD::StaticClass();
#endif
}

void ADYStageGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
	Super::InitGame(MapName, Options, ErrorMessage);
	// Only the formal main world mounts the V2.2 entry menu. Map identity, not a build
	// flag, decides this, so Development and Shipping launch the same flow.
	const FString Canonical = UWorld::RemovePIEPrefix(MapName);
	if (Canonical.Contains(TEXT("L_DY_Main")))
	{
		PlayerControllerClass = ADYReleaseEntryPlayerController::StaticClass();
	}
}

ADYStagePresentation* ADYStageGameMode::GetStagePresentation() const
{
#if !UE_BUILD_SHIPPING
	const UWorld* World = GetWorld();
	return World && IsDevContentPackage(World->GetPackage()->GetName()) ? StagePresentation.Get() : nullptr;
#else
	return nullptr;
#endif
}

void ADYStageGameMode::RegisterStagePresentation(ADYStagePresentation* InPresentation)
{
	if (!GetWorld() || !InPresentation)
	{
		return;
	}
	// Only a live actor belonging to this world may claim the registration slot.
	if (!IsValid(InPresentation) || InPresentation->GetWorld() != GetWorld())
	{
		UE_LOG(
			LogDengYingShanHai,
			Warning,
			TEXT("Stage GameMode rejected a Presentation registration from a foreign or invalid actor."));
		return;
	}

	if (StagePresentation.Get() == InPresentation)
	{
		// Already registered. Broadcasting again would make listeners re-read state
		// they already have, so this is intentionally a no-op.
		return;
	}

	StagePresentation = InPresentation;
	UE_LOG(LogDengYingShanHai, Display, TEXT("Stage GameMode registered presentation %s (%s)"),
		*InPresentation->GetName(), *InPresentation->GetClass()->GetName());
	OnStagePresentationChanged.Broadcast(InPresentation);
}

void ADYStageGameMode::UnregisterStagePresentation(ADYStagePresentation* InPresentation)
{
	// An old actor tearing down after a new one registered must not clear the new
	// binding, so identity is checked before anything is reset.
	if (!InPresentation || StagePresentation.Get() != InPresentation)
	{
		return;
	}

	StagePresentation = nullptr;
	OnStagePresentationChanged.Broadcast(nullptr);
}
