#include "UI/DYInteractionHUD.h"

#include "Core/DYStageGameMode.h"
#include "DengYingShanHai.h"
#include "GameFramework/PlayerController.h"
#include "Interaction/DYInteractionComponent.h"
#include "Stage/DYStagePresentation.h"
#include "UI/DYInteractionHUDWidget.h"

ADYInteractionHUD::ADYInteractionHUD()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ADYInteractionHUD::BeginPlay()
{
	Super::BeginPlay();
	APlayerController* PC = GetOwningPlayerController();
	if (!PC || !PC->IsLocalController()) { return; }
	BoundController = PC;
	PC->OnPossessedPawnChanged.AddUniqueDynamic(this, &ADYInteractionHUD::HandlePawnChanged);
	BindPawn(PC->GetPawn());
	BindGameMode(GetWorld() ? GetWorld()->GetAuthGameMode<ADYStageGameMode>() : nullptr);
	if (WidgetClass)
	{
		View = CreateWidget<UDYInteractionHUDWidget>(PC, WidgetClass);
		if (View)
		{
			View->OnNativeDestruct.AddUObject(this, &ADYInteractionHUD::HandleWidgetDestruct);
			View->AddToPlayerScreen();
			RefreshView();
		}
	}
	if (!View) { UE_LOG(LogDengYingShanHai, Warning, TEXT("Player HUD WidgetClass is missing; gameplay/input remains unchanged.")); }
}

void ADYInteractionHUD::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	HandleWidgetDestruct(View);
	if (View)
	{
		View->OnNativeDestruct.RemoveAll(this);
		View->RemoveFromParent();
		View = nullptr;
	}
	Super::EndPlay(EndPlayReason);
}

void ADYInteractionHUD::HandleWidgetDestruct(UUserWidget* RemovedWidget)
{
	if (APlayerController* PC = BoundController.Get())
	{
		PC->OnPossessedPawnChanged.RemoveDynamic(this, &ADYInteractionHUD::HandlePawnChanged);
	}
	BoundController.Reset();
	BindPawn(nullptr);
	UnbindGameMode();
}

void ADYInteractionHUD::BindGameMode(ADYStageGameMode* Mode)
{
	UnbindGameMode();
	if (!IsValid(Mode) || Mode->GetWorld() != GetWorld()) { return; }
	BoundMode = Mode;
	RegistrationHandle = Mode->OnStagePresentationChanged.AddUObject(this, &ADYInteractionHUD::AttachPresentation);
	AttachPresentation(Mode->GetPlayerStagePresentation());
}

void ADYInteractionHUD::UnbindGameMode()
{
	AttachPresentation(nullptr);
	if (ADYStageGameMode* Mode = BoundMode.Get()) { Mode->OnStagePresentationChanged.Remove(RegistrationHandle); }
	RegistrationHandle.Reset();
	BoundMode.Reset();
}

void ADYInteractionHUD::AttachPresentation(ADYStagePresentation* Presentation)
{
	if (ADYStagePresentation* Previous = BoundPresentation.Get())
	{
		Previous->OnPlayerFeedbackDisplayChanged().Remove(DisplayHandle);
		Previous->OnPlayerActDisplayChanged().Remove(ActDisplayHandle);
		Previous->OnPlayerAlignmentDisplayChanged().Remove(AlignmentDisplayHandle);
	}
	DisplayHandle.Reset();
	ActDisplayHandle.Reset();
	AlignmentDisplayHandle.Reset();
	BoundPresentation.Reset();
	Feedback = EDYStageFeedbackDisplay::Hidden;
	ActDisplay = FDYActSequenceSnapshot();
	AlignmentDisplay = FDYPlayerAlignmentDisplay();
	if (!IsValid(Presentation) || Presentation->GetWorld() != GetWorld())
	{
		RefreshView();
		return;
	}
	BoundPresentation = Presentation;
	DisplayHandle = Presentation->OnPlayerFeedbackDisplayChanged().AddUObject(this, &ADYInteractionHUD::HandleDisplay);
	ActDisplayHandle = Presentation->OnPlayerActDisplayChanged().AddUObject(this, &ADYInteractionHUD::HandleActDisplay);
	AlignmentDisplayHandle = Presentation->OnPlayerAlignmentDisplayChanged().AddUObject(this, &ADYInteractionHUD::HandleAlignmentDisplay);
	// Late HUDs read the settled cosmetic state; they never replay puzzle synchronization.
	Feedback = Presentation->GetPlayerFeedbackDisplay();
	ActDisplay = Presentation->GetPlayerActDisplay();
	AlignmentDisplay = Presentation->GetPlayerAlignmentDisplay();
	RefreshView();
}

void ADYInteractionHUD::HandleDisplay(EDYStageFeedbackDisplay Display)
{
	const ADYStagePresentation* Presentation = BoundPresentation.Get();
	Feedback = IsValid(Presentation) ? Presentation->GetPlayerFeedbackDisplay() : EDYStageFeedbackDisplay::Hidden;
	AlignmentDisplay = IsValid(Presentation) ? Presentation->GetPlayerAlignmentDisplay() : FDYPlayerAlignmentDisplay();
	RefreshView();
}

void ADYInteractionHUD::HandleActDisplay(const FDYActSequenceSnapshot& Snapshot)
{
	// A prior cosmetic listener may have reset/replaced Presentation during this
	// multicast. Read its current settled value, not the superseded event payload.
	const ADYStagePresentation* Presentation = BoundPresentation.Get();
	ActDisplay = IsValid(Presentation) ? Presentation->GetPlayerActDisplay() : FDYActSequenceSnapshot();
	AlignmentDisplay = IsValid(Presentation) ? Presentation->GetPlayerAlignmentDisplay() : FDYPlayerAlignmentDisplay();
	RefreshView();
}

void ADYInteractionHUD::HandleAlignmentDisplay(const FDYPlayerAlignmentDisplay& Snapshot)
{
	const ADYStagePresentation* Presentation = BoundPresentation.Get();
	AlignmentDisplay = IsValid(Presentation) ? Presentation->GetPlayerAlignmentDisplay() : FDYPlayerAlignmentDisplay();
	RefreshView();
}

void ADYInteractionHUD::BindPawn(APawn* Pawn)
{
	if (UDYInteractionComponent* Old = BoundInteraction.Get())
	{
		Old->OnFocusChanged.RemoveDynamic(this, &ADYInteractionHUD::HandleFocusChanged);
		Old->OnControlStateChanged.RemoveDynamic(this, &ADYInteractionHUD::HandleControlChanged);
	}
	BoundInteraction.Reset();
	if (IsValid(Pawn) && Pawn->GetWorld() == GetWorld())
	{
		UDYInteractionComponent* Interaction = Pawn->FindComponentByClass<UDYInteractionComponent>();
		if (Interaction)
		{
			BoundInteraction = Interaction;
			Interaction->OnFocusChanged.AddUniqueDynamic(this, &ADYInteractionHUD::HandleFocusChanged);
			Interaction->OnControlStateChanged.AddUniqueDynamic(this, &ADYInteractionHUD::HandleControlChanged);
		}
	}
	RefreshInteraction();
}

void ADYInteractionHUD::HandlePawnChanged(APawn* OldPawn, APawn* NewPawn) { BindPawn(NewPawn); }
void ADYInteractionHUD::HandleFocusChanged(AActor* Previous, AActor* Current) { RefreshInteraction(); }
void ADYInteractionHUD::HandleControlChanged(AActor* Controlled, bool bIsControlling) { RefreshInteraction(); }

void ADYInteractionHUD::RefreshInteraction()
{
	UDYInteractionComponent* Interaction = BoundInteraction.Get();
	bFocused = Interaction && Interaction->GetFocusedActor();
	bControlling = Interaction && Interaction->IsControlling();
	RefreshView();
}

void ADYInteractionHUD::RefreshView()
{
	if (View)
	{
		View->ApplyActSnapshot(ActDisplay);
		View->ApplyAlignmentSnapshot(AlignmentDisplay);
		View->ApplySnapshot(bFocused, bControlling, Feedback);
	}
}
