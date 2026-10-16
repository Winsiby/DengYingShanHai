#include "Core/DYDevEntryPlayerController.h"

#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Core/DYStageGameMode.h"
#include "DengYingShanHai.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "Interaction/DYInteractionComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Stage/DYStagePresentation.h"
#include "TimerManager.h"

namespace DYDevEntry
{
	static const TCHAR* EntryMap = TEXT("/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev");
	static const TCHAR* ReadabilityMap = TEXT("/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab");
	static const TCHAR* AlignmentMap = TEXT("/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab");
	static const TCHAR* EnvironmentMap = TEXT("/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab");
	static const TCHAR* FramePostPlacementMap = TEXT("/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab");
	static const TCHAR* FrameBeamPlacementMap = TEXT("/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab");
	static const TCHAR* FrameBeamCandidateMap = TEXT("/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab");
	static const TCHAR* FrameBeamTopUVMap = TEXT("/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab");
}

ADYDevEntryPlayerController::ADYDevEntryPlayerController()
{
	MenuWidgetClass = UDYDevEntryWidget::StaticClass();
}

FName ADYDevEntryPlayerController::ResolveDevEntryMapName(const FString& PackageName, const EWorldType::Type WorldType)
{
#if UE_BUILD_SHIPPING
	return NAME_None;
#else
	if (WorldType != EWorldType::Game && WorldType != EWorldType::PIE) { return NAME_None; }
	const FString Canonical = UWorld::RemovePIEPrefix(PackageName);
	if (Canonical == DYDevEntry::EntryMap) { return FName(DYDevEntry::EntryMap); }
	if (Canonical == DYDevEntry::ReadabilityMap) { return FName(DYDevEntry::ReadabilityMap); }
	if (Canonical == DYDevEntry::AlignmentMap) { return FName(DYDevEntry::AlignmentMap); }
	if (Canonical == DYDevEntry::EnvironmentMap) { return FName(DYDevEntry::EnvironmentMap); }
	if (Canonical == DYDevEntry::FramePostPlacementMap) { return FName(DYDevEntry::FramePostPlacementMap); }
	if (Canonical == DYDevEntry::FrameBeamPlacementMap) { return FName(DYDevEntry::FrameBeamPlacementMap); }
	if (Canonical == DYDevEntry::FrameBeamCandidateMap) { return FName(DYDevEntry::FrameBeamCandidateMap); }
	if (Canonical == DYDevEntry::FrameBeamTopUVMap) { return FName(DYDevEntry::FrameBeamTopUVMap); }
	return NAME_None;
#endif
}

FName ADYDevEntryPlayerController::GetCurrentDevEntryMap() const
{
	const UWorld* World = GetWorld();
	return World ? ResolveDevEntryMapName(World->GetOutermost()->GetName(), World->WorldType) : NAME_None;
}

bool ADYDevEntryPlayerController::IsEntryLoopWorld() const { return !GetCurrentDevEntryMap().IsNone(); }

void ADYDevEntryPlayerController::BeginPlay()
{
	Super::BeginPlay();
	if (!IsLocalPlayerController() || !IsEntryLoopWorld()) { return; }
	if (MenuWidgetClass)
	{
		MenuView = CreateWidget<UDYDevEntryWidget>(this, MenuWidgetClass);
		if (MenuView) { MenuView->AddToPlayerScreen(100); }
	}
	ADYStageGameMode* Mode = GetWorld()->GetAuthGameMode<ADYStageGameMode>();
	if (Mode)
	{
		BoundMode = Mode;
		RegistrationHandle = Mode->OnStagePresentationChanged.AddUObject(this, &ADYDevEntryPlayerController::AttachPresentation);
		AttachPresentation(Mode->GetPlayerStagePresentation());
	}
	// One next-frame refresh covers actor BeginPlay order, not a scanning/polling Tick.
	ReadyRefreshHandle = GetWorld()->GetTimerManager().SetTimerForNextTick(
		FTimerDelegate::CreateWeakLambda(this, [this]() { RefreshMenu(); }));
	RefreshMenu();
}

void ADYDevEntryPlayerController::EndPlay(const EEndPlayReason::Type Reason)
{
	bEndingPlay = true;
	if (GetWorld())
	{
		GetWorld()->GetTimerManager().ClearTimer(ReadyRefreshHandle);
		GetWorld()->GetTimerManager().ClearTimer(ReplayHandle);
	}
	if (GEngine) { GEngine->OnTravelFailure().Remove(TravelFailureHandle); }
	TravelFailureHandle.Reset();
	if (ADYStageGameMode* Mode = BoundMode.Get()) { Mode->OnStagePresentationChanged.Remove(RegistrationHandle); }
	RegistrationHandle.Reset();
	BoundMode.Reset();
	AttachPresentation(nullptr);
	if (MenuView) { MenuView->RemoveFromParent(); MenuView = nullptr; }
	Super::EndPlay(Reason);
}

void ADYDevEntryPlayerController::AttachPresentation(ADYStagePresentation* Stage)
{
	if (ADYStagePresentation* Old = BoundStage.Get()) { Old->OnPlayerActDisplayChanged().Remove(ActHandle); }
	ActHandle.Reset();
	BoundStage.Reset();
	LastObservedPlayingActIndex = INDEX_NONE;
	if (!bEndingPlay && IsValid(Stage) && Stage->GetWorld() == GetWorld())
	{
		BoundStage = Stage;
		ActHandle = Stage->OnPlayerActDisplayChanged().AddUObject(this, &ADYDevEntryPlayerController::HandleActDisplay);
		const auto Current = Stage->GetPlayerActDisplay();
		if (Current.bSequenceEnabled && Current.Phase == EDYActSequencePhase::Playing
			&& Current.ActIndex >= 0 && Current.ActIndex < Current.ActCount)
		{
			LastObservedPlayingActIndex = Current.ActIndex; // A late attachment establishes a baseline, not a new act.
		}
	}
	RefreshMenu();
}

ADYPuzzleDirector* ADYDevEntryPlayerController::GetBoundDirector() const
{
	ADYStagePresentation* Stage = BoundStage.Get();
	ADYPuzzleDirector* Director = IsValid(Stage) ? Stage->GetPuzzleDirector() : nullptr;
	return IsValid(Director) && Director->GetWorld() == GetWorld() ? Director : nullptr;
}

EDYDevEntryPanel ADYDevEntryPlayerController::GetEntryPanel() const
{
	if (bEndingPlay || !IsEntryLoopWorld()) { return EDYDevEntryPanel::Hidden; }
	if (bReplayPending) { return EDYDevEntryPanel::Reloading; }
	ADYPuzzleDirector* Director = GetBoundDirector();
	ADYStagePresentation* Stage = BoundStage.Get();
	if (!Director || !Stage || !MenuView || !MenuView->HasReadyView()
		|| Director->IsAutoStartOnBeginPlay()) { return EDYDevEntryPanel::Waiting; }
	const FDYActSequenceSnapshot Snapshot = Stage->GetPlayerActDisplay();
	if (!Snapshot.bSequenceEnabled) { return EDYDevEntryPanel::Waiting; }
	if (Snapshot.Phase == EDYActSequencePhase::Complete) { return EDYDevEntryPanel::End; }
	if (Snapshot.Phase == EDYActSequencePhase::Inactive)
	{
		return Director->CanStartManualSequence(Stage) ? EDYDevEntryPanel::Start : EDYDevEntryPanel::Waiting;
	}
	return EDYDevEntryPanel::Hidden;
}

void ADYDevEntryPlayerController::HandleActDisplay(const FDYActSequenceSnapshot& Snapshot)
{
	// Read the registered stage again; an earlier listener may have reset/replaced it.
	RefreshControlForActEntry();
	RefreshMenu();
}

bool ADYDevEntryPlayerController::ShouldReleaseControlForActEntry(
	const FDYActSequenceSnapshot& Current, const int32 LastPlayingActIndex)
{
	return Current.bSequenceEnabled && Current.Phase == EDYActSequencePhase::Playing
		&& Current.ActCount > 0 && Current.ActIndex >= 0 && Current.ActIndex < Current.ActCount
		&& LastPlayingActIndex >= 0 && LastPlayingActIndex < Current.ActCount
		&& Current.ActIndex > LastPlayingActIndex;
}

void ADYDevEntryPlayerController::RefreshControlForActEntry()
{
	if (bEndingPlay || bReplayPending || !IsLocalPlayerController()) { return; }
	ADYStagePresentation* Stage = BoundStage.Get();
	ADYPuzzleDirector* Director = GetBoundDirector();
	if (!IsValid(Stage) || !Director || Stage->GetWorld() != GetWorld()) { return; }
	const auto Current = Director->GetActSequenceSnapshot();
	const auto Display = Stage->GetPlayerActDisplay();
	if (!Current.bSequenceEnabled || Current.Phase != EDYActSequencePhase::Playing
		|| Current.ActIndex < 0 || Current.ActIndex >= Current.ActCount
		|| Display.bSequenceEnabled != Current.bSequenceEnabled || Display.Phase != Current.Phase
		|| Display.ActIndex != Current.ActIndex || Display.ActCount != Current.ActCount
		|| !Display.ActTitle.EqualTo(Current.ActTitle)) { return; }
	const bool bNewAct = ShouldReleaseControlForActEntry(Current, LastObservedPlayingActIndex);
	// Consume before EndActiveControl's callbacks. Reentrant synchronization/reset
	// must not release a newly acquired session twice. No state writes after that call.
	LastObservedPlayingActIndex = Current.ActIndex;
	if (!bNewAct) { return; }
	APawn* ControlledPawn = GetPawn();
	if (!IsValid(ControlledPawn) || ControlledPawn->GetWorld() != GetWorld() || ControlledPawn->GetController() != this) { return; }
	if (UDYInteractionComponent* Interaction = ControlledPawn->FindComponentByClass<UDYInteractionComponent>())
	{
		Interaction->EndActiveControl(); // Existing Pawn callback restores Explore; no reset or input remapping here.
	}
}

void ADYDevEntryPlayerController::RefreshMenu()
{
	if (bEndingPlay || !IsLocalPlayerController() || !IsEntryLoopWorld()) { return; }
	const EDYDevEntryPanel Panel = GetEntryPanel();
	if (MenuView) { MenuView->ApplyPanel(Panel); }
	const bool bNeedsMenu = Panel != EDYDevEntryPanel::Hidden;
	if (bNeedsMenu == bMenuInputApplied) { return; }
	bMenuInputApplied = bNeedsMenu;
	FlushPressedKeys();
	bShowMouseCursor = bNeedsMenu;
	if (bNeedsMenu)
	{
		FInputModeUIOnly Mode;
		Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		if (MenuView && MenuView->GetPrimaryFocusWidget())
		{
			Mode.SetWidgetToFocus(MenuView->GetPrimaryFocusWidget()->TakeWidget());
		}
		SetInputMode(Mode);
	}
	else
	{
		SetInputMode(FInputModeGameOnly());
		UWidgetBlueprintLibrary::SetFocusToGameViewport();
	}
}

bool ADYDevEntryPlayerController::RequestStartExperience()
{
	if (bEndingPlay || bRequestInFlight || !IsLocalPlayerController() || GetEntryPanel() != EDYDevEntryPanel::Start) { return false; }
	ADYPuzzleDirector* Director = GetBoundDirector();
	if (!Director) { return false; }
	TGuardValue<bool> RequestGuard(bRequestInFlight, true);
	const bool bStarted = Director->StartManualSequence(BoundStage.Get());
	if (!bEndingPlay && IsValid(this)) { RefreshMenu(); }
	return bStarted;
}

bool ADYDevEntryPlayerController::RequestReplayExperience()
{
	if (bEndingPlay || bRequestInFlight || !IsLocalPlayerController() || GetEntryPanel() != EDYDevEntryPanel::End) { return false; }
	bReplayPending = true; // Consume once before EndControl's callbacks or any deferred travel.
	TGuardValue<bool> RequestGuard(bRequestInFlight, true);
	if (APawn* ControlledPawn = GetPawn())
	{
		if (UDYInteractionComponent* Interaction = ControlledPawn->FindComponentByClass<UDYInteractionComponent>()) { Interaction->EndActiveControl(); }
	}
	if (bEndingPlay || !IsValid(this) || !GetWorld()) { return false; }
	RefreshMenu();
	ReplayHandle = GetWorld()->GetTimerManager().SetTimerForNextTick(
		FTimerDelegate::CreateWeakLambda(this, [this]() { PerformReplay(); }));
	return true;
}

void ADYDevEntryPlayerController::PerformReplay()
{
	const FName ReplayMap = GetCurrentDevEntryMap();
	if (bEndingPlay || !bReplayPending || ReplayMap.IsNone()) { return; }
	if (GEngine)
	{
		TravelFailureHandle = GEngine->OnTravelFailure().AddUObject(this, &ADYDevEntryPlayerController::HandleTravelFailure);
	}
	UGameplayStatics::OpenLevel(this, ReplayMap, true);
}

void ADYDevEntryPlayerController::HandleTravelFailure(UWorld* World, ETravelFailure::Type Failure, const FString& Error)
{
	if (bEndingPlay || !bReplayPending || World != GetWorld()) { return; }
	if (GEngine) { GEngine->OnTravelFailure().Remove(TravelFailureHandle); }
	TravelFailureHandle.Reset();
	bReplayPending = false;
	UE_LOG(LogDengYingShanHai, Error, TEXT("Dev same-map replay failed; existing finale retained: %s"), *Error);
	RefreshMenu();
}

void ADYDevEntryPlayerController::RequestQuitExperience()
{
	if (!bEndingPlay && IsLocalPlayerController() && IsEntryLoopWorld())
	{
		UKismetSystemLibrary::QuitGame(this, this, EQuitPreference::Quit, false);
	}
}
