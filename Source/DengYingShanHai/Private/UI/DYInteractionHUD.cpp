#include "UI/DYInteractionHUD.h"

#include "CanvasItem.h"
#include "Core/DYStageGameMode.h"
#include "DengYingShanHai.h"
#include "GameFramework/PlayerController.h"
#include "Interaction/DYInteractionComponent.h"
#include "Stage/DYStagePresentation.h"
#include "UI/DYInteractionHUDWidget.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"

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
	// The entry walk needs one line of text before the play HUD is ever laid out;
	// AHUD canvas drawing does not depend on the UMG root being sized.
	EntryGuideFont = LoadObject<UFont>(nullptr, TEXT("/Game/DengYingShanHai/Dev/M2/UI/FF_DYSourceHanSansSC_Font.FF_DYSourceHanSansSC_Font"), nullptr, LOAD_NoWarn | LOAD_Quiet);
}

void ADYInteractionHUD::ShowTransientHint(const FText& InText, float Seconds)
{
	if (View) { View->ShowHint(InText, Seconds); }
}

void ADYInteractionHUD::SetStageHudVisible(bool bVisible)
{
	if (View) { View->SetStageHudVisible(bVisible); }
}

void ADYInteractionHUD::SetEntryWalkGuide(bool bActive, const FText& InText)
{
	bEntryGuideActive = bActive && !InText.IsEmpty();
	EntryGuideText = InText;
	if (View) { View->SetEntryWalkGuide(bActive, InText); }
}

void ADYInteractionHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!bEntryGuideActive || EntryGuideText.IsEmpty() || !Canvas) { return; }
	UFont* Font = EntryGuideFont ? EntryGuideFont.Get() : (GEngine ? GEngine->GetLargeFont() : nullptr);
	if (!Font) { return; }
	const FString Line = EntryGuideText.ToString();
	const float Scale = 1.60f;
	float TextW = 0.0f;
	float TextH = 0.0f;
	GetTextSize(Line, TextW, TextH, Font, Scale);
	if (TextW <= 0.0f) { return; }
	const float PadX = 46.0f;
	const float PadY = 24.0f;
	const float X = (Canvas->ClipX - TextW) * 0.5f;
	const float Y = Canvas->ClipY - TextH - 132.0f;
	DrawRect(FLinearColor(0.045f, 0.035f, 0.028f, 0.74f), X - PadX, Y - PadY, TextW + PadX * 2.0f, TextH + PadY * 2.0f);
	// One warm rule under the line: the canvas plaque has no UMG border, and the
	// accent keeps it reading as part of the same paper-and-gold language.
	DrawRect(FLinearColor(0.85f, 0.62f, 0.28f, 0.85f), X + TextW * 0.18f, Y + TextH + 14.0f, TextW * 0.64f, 2.0f);
	DrawText(Line, FLinearColor(0.96f, 0.93f, 0.86f, 1.0f), X, Y, Font, Scale, false);
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
