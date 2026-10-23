#include "UI/DYDevInteractionHUD.h"

#include "Core/DYStageGameMode.h"
#include "DengYingShanHai.h"
#include "Interaction/DYInteractionComponent.h"
#include "Player/DYStageOperatorPawn.h"
#include "Stage/DYStagePresentation.h"

#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "GameFramework/PlayerController.h"
#include "Misc/PackageName.h"

namespace DYDevHUD
{
	// Crosshair geometry, in pixels, centred on the viewport.
	constexpr float CrosshairArmLength = 9.0f;
	constexpr float CrosshairThickness = 1.6f;
	constexpr float CrosshairGap = 3.0f;

	constexpr float PromptOffsetY = 26.0f;
	// The Dev status line sits below the interaction prompt so neither overlaps the
	// crosshair nor the lamp on stage.
	constexpr float DevStatusOffsetY = 48.0f;
	constexpr float PromptFontScale = 1.1f;

	const FLinearColor UnfocusedColor(1.0f, 1.0f, 1.0f, 0.75f);
	const FLinearColor FocusedColor(0.15f, 1.0f, 0.35f, 1.0f);
	const FLinearColor TextColor(1.0f, 1.0f, 1.0f, 0.9f);
}

ADYDevInteractionHUD::ADYDevInteractionHUD()
{
	// Purely reactive: the HUD reads state during DrawHUD and keeps no timer or tick.
	PrimaryActorTick.bCanEverTick = false;
}

UDYInteractionComponent* ADYDevInteractionHUD::ResolveInteractionComponent() const
{
	const APlayerController* PlayerController = GetOwningPlayerController();
	const APawn* Pawn = PlayerController ? PlayerController->GetPawn() : nullptr;
	const ADYStageOperatorPawn* Operator = Cast<ADYStageOperatorPawn>(Pawn);
	return Operator ? Operator->GetInteractionComponent() : nullptr;
}

void ADYDevInteractionHUD::DrawHUD()
{
	Super::DrawHUD();

	if (!Canvas)
	{
		return;
	}

	const UDYInteractionComponent* Interaction = ResolveInteractionComponent();
	// Both values come straight from the component; the HUD makes no decision of its own.
	const bool bHasCandidate = Interaction != nullptr && Interaction->GetFocusedActor() != nullptr;
	const bool bIsControlling = Interaction != nullptr && Interaction->IsControlling();

	DrawCentreCrosshair(bHasCandidate, bIsControlling);
	DrawInteractionPrompt(bHasCandidate, bIsControlling);
	DrawDevStatusLine();
}

void ADYDevInteractionHUD::BeginPlay()
{
	Super::BeginPlay();

	// The GameMode owns the only reference to this world's Presentation. Binding to its
	// notification covers both orders: if the Presentation registered first we adopt the
	// reference it already holds, and if it registers later the notification arrives here.
	UWorld* World = GetWorld();
	ADYStageGameMode* GameMode = World ? World->GetAuthGameMode<ADYStageGameMode>() : nullptr;
	BindToGameMode(GameMode);
}

void ADYDevInteractionHUD::BindToGameMode(ADYStageGameMode* GameMode)
{
	UnbindGameMode();
	if (!IsDevContentWorld())
	{
		return;
	}
	if (IsValid(GameMode) && GameMode->GetWorld() == GetWorld())
	{
		BoundGameMode = GameMode;
		PresentationChangedHandle = GameMode->OnStagePresentationChanged.AddUObject(
			this, &ADYDevInteractionHUD::HandlePresentationChanged);
		AttachToPresentation(GameMode->GetStagePresentation());
	}
	else
	{
		UE_LOG(
			LogDengYingShanHai,
			Warning,
			TEXT("Dev interaction HUD has no stage GameMode; the Dev status line stays hidden."));
	}
}

void ADYDevInteractionHUD::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	UnbindGameMode();
	Super::EndPlay(EndPlayReason);
}

void ADYDevInteractionHUD::UnbindGameMode()
{
	DetachFromPresentation();

	if (PresentationChangedHandle.IsValid())
	{
		if (ADYStageGameMode* GameMode = BoundGameMode.Get())
		{
			GameMode->OnStagePresentationChanged.Remove(PresentationChangedHandle);
		}
		PresentationChangedHandle.Reset();
	}

	BoundGameMode.Reset();
}

void ADYDevInteractionHUD::HandlePresentationChanged(ADYStagePresentation* InPresentation)
{
	AttachToPresentation(InPresentation);
}

void ADYDevInteractionHUD::AttachToPresentation(ADYStagePresentation* InPresentation)
{
	// Drop any previous binding first so a switch cannot leave a stale listener behind.
	DetachFromPresentation();

	if (!IsValid(InPresentation) || InPresentation->GetWorld() != GetWorld() || !IsDevContentWorld())
	{
		return;
	}

	InPresentation->OnFeedbackDisplayChanged().AddUObject(
		this, &ADYDevInteractionHUD::HandleFeedbackDisplayChanged);
	BoundPresentation = InPresentation;

	// Late join reads the current snapshot instead of calling any synchronise entry
	// point, so no activation cue or environment reset is replayed.
	HandleFeedbackDisplayChanged(InPresentation->GetFeedbackDisplay());
}

void ADYDevInteractionHUD::DetachFromPresentation()
{
	if (ADYStagePresentation* Previous = BoundPresentation.Get())
	{
		Previous->OnFeedbackDisplayChanged().RemoveAll(this);
	}
	BoundPresentation = nullptr;
	HandleFeedbackDisplayChanged(EDYStageFeedbackDisplay::Hidden);
}

void ADYDevInteractionHUD::HandleFeedbackDisplayChanged(const EDYStageFeedbackDisplay NewDisplay)
{
	CachedFeedbackDisplay = NewDisplay;
}

bool ADYDevInteractionHUD::IsDevContentWorld() const
{
#if UE_BUILD_SHIPPING
	return false;
#else
	// Uses the same product helper as the Presentation gate, and reads the WORLD's
	// package rather than the HUD's own, so a PIE-duplicated Dev map still matches.
	const UWorld* World = GetWorld();
	const UPackage* Package = World ? World->GetPackage() : nullptr;
	return Package && IsDevContentPackage(Package->GetName());
#endif
}

const TCHAR* ADYDevInteractionHUD::GetPlaceholderText(const EDYStageFeedbackDisplay Display)
{
	switch (Display)
	{
	case EDYStageFeedbackDisplay::Adjust:
		return TEXT("Keep adjusting");
	case EDYStageFeedbackDisplay::Near:
		return TEXT("Getting closer");
	case EDYStageFeedbackDisplay::Holding:
		return TEXT("Hold steady");
	case EDYStageFeedbackDisplay::Interrupted:
		return TEXT("Interrupted - try again");
	case EDYStageFeedbackDisplay::Complete:
		return TEXT("Complete");
	case EDYStageFeedbackDisplay::Hidden:
	default:
		return TEXT("");
	}
}

void ADYDevInteractionHUD::DrawDevStatusLine()
{
	using namespace DYDevHUD;

	if (!Canvas || CachedFeedbackDisplay == EDYStageFeedbackDisplay::Hidden)
	{
		return;
	}

	UFont* Font = GEngine ? GEngine->GetSmallFont() : nullptr;
	const TCHAR* Line = GetPlaceholderText(CachedFeedbackDisplay);
	if (!Font || !Line || FCString::Strlen(Line) == 0)
	{
		return;
	}

	float TextWidth = 0.0f;
	float TextHeight = 0.0f;
	GetTextSize(Line, TextWidth, TextHeight, Font, PromptFontScale);

	const float CentreX = Canvas->ClipX * 0.5f;
	const float CentreY = Canvas->ClipY * 0.5f;

	// ASCII placeholder only: the Dev font in this build has not been verified to
	// carry CJK glyphs, and the formal UI replaces this readout.
	DrawText(
		Line,
		TextColor,
		CentreX - TextWidth * 0.5f,
		CentreY + DevStatusOffsetY - TextHeight * 0.5f,
		Font,
		PromptFontScale);
}

void ADYDevInteractionHUD::DrawCentreCrosshair(const bool bHasCandidate, const bool bIsControlling)
{
	using namespace DYDevHUD;

	const float CentreX = Canvas->ClipX * 0.5f;
	const float CentreY = Canvas->ClipY * 0.5f;

	// Green means the candidate can actually be taken. While controlling, the crosshair
	// stays white so the colour never implies a second, different interaction.
	const FLinearColor Color = (bHasCandidate && !bIsControlling) ? FocusedColor : UnfocusedColor;

	const float Inner = CrosshairGap;
	const float Arm = CrosshairArmLength;
	const float T = CrosshairThickness;

	DrawRect(Color, CentreX - T * 0.5f, CentreY - Inner - Arm, T, Arm);
	DrawRect(Color, CentreX - T * 0.5f, CentreY + Inner, T, Arm);
	DrawRect(Color, CentreX - Inner - Arm, CentreY - T * 0.5f, Arm, T);
	DrawRect(Color, CentreX + Inner, CentreY - T * 0.5f, Arm, T);
	DrawRect(Color, CentreX - 1.0f, CentreY - 1.0f, 2.0f, 2.0f);
}

void ADYDevInteractionHUD::DrawInteractionPrompt(const bool bHasCandidate, const bool bIsControlling)
{
	using namespace DYDevHUD;

	UFont* Font = GEngine ? GEngine->GetSmallFont() : nullptr;
	if (!Font)
	{
		return;
	}

	// ASCII-only for now: the Dev font in this build is the engine default and has not
	// been verified to carry CJK glyphs. The formal art UI replaces this string.
	const TCHAR* Line = nullptr;
	if (bIsControlling)
	{
		Line = TEXT("A / D  adjust      E  release      R  reset");
	}
	else if (bHasCandidate)
	{
		Line = TEXT("[E]  interact");
	}
	else
	{
		Line = TEXT("Aim at the lamp");
	}

	const FLinearColor Color = bHasCandidate ? FocusedColor : TextColor;

	// AHUD::GetTextSize is public, so the line can be centred without guessing metrics.
	float TextWidth = 0.0f;
	float TextHeight = 0.0f;
	GetTextSize(Line, TextWidth, TextHeight, Font, PromptFontScale);

	const float CentreX = Canvas->ClipX * 0.5f;
	const float CentreY = Canvas->ClipY * 0.5f;

	DrawText(
		Line,
		Color,
		CentreX - TextWidth * 0.5f,
		CentreY + PromptOffsetY - TextHeight * 0.5f,
		Font,
		PromptFontScale);
}
