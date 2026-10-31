#include "UI/DYInteractionHUDWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/ProgressBar.h"
#include "Components/SizeBox.h"
#include "Core/DYEntryWalkTypes.h"
#include "Engine/Font.h"
#include "GameFramework/Pawn.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "TimerManager.h"
#include "DengYingShanHai.h"

#define LOCTEXT_NAMESPACE "DYPlayerHUD"

UDYInteractionHUDWidget::UDYInteractionHUDWidget(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
	SetIsFocusable(false);
}

FText UDYInteractionHUDWidget::GetPromptText(bool bHasFocus, bool bIsControlling)
{
	if (bIsControlling) { return LOCTEXT("Manipulate", "A / D　调整　　E　放开　　R　复位"); }
	if (bHasFocus) { return LOCTEXT("Focus", "E　操纵"); }
	return LOCTEXT("Explore", "对准灯具或皮影");
}

FText UDYInteractionHUDWidget::GetEntryWalkHint()
{
	return LOCTEXT("EntryWalk", "沿灯径向灯火深处走去，入戏台");
}

FText UDYInteractionHUDWidget::GetEntryArrivalHint()
{
	return LOCTEXT("EntryArrival", "入戏台");
}

FText UDYInteractionHUDWidget::GetStatusText(EDYStageFeedbackDisplay Display)
{
	switch (Display)
	{
	case EDYStageFeedbackDisplay::Adjust: return LOCTEXT("Adjust", "继续调整");
	case EDYStageFeedbackDisplay::Near: return LOCTEXT("Near", "影形渐合");
	case EDYStageFeedbackDisplay::Holding: return LOCTEXT("Holding", "保持此刻");
	case EDYStageFeedbackDisplay::Interrupted: return LOCTEXT("Interrupted", "影形未稳，再试一次");
	case EDYStageFeedbackDisplay::Complete: return LOCTEXT("Complete", "本幕已成");
	default: return FText::GetEmpty();
	}
}

FText UDYInteractionHUDWidget::GetAlignmentStatusText(const FDYPlayerAlignmentDisplay& Snapshot, EDYStageFeedbackDisplay Display)
{
	if (!Snapshot.bEnabled || !Snapshot.bHasValidSample || Display == EDYStageFeedbackDisplay::Complete) { return GetStatusText(Display); }
	if (Display == EDYStageFeedbackDisplay::Interrupted) { return LOCTEXT("AlignmentInterrupted", "贴合被打断，轻调后再保持"); }
	if (Snapshot.bJointReady)
	{
		return Snapshot.bPuppetRequired ? LOCTEXT("BothReady", "灯偶已到位，松开 A / D，保持此刻")
			: LOCTEXT("LightOnlyReady", "灯已就位，松开 A / D，保持此刻");
	}
	if (Snapshot.bPuppetRequired && Snapshot.bPuppetReady && !Snapshot.bLightReady) { return LOCTEXT("PuppetReady", "偶已就位，继续调灯"); }
	if (Snapshot.bLightReady && Snapshot.bPuppetRequired && !Snapshot.bPuppetReady) { return LOCTEXT("LightReady", "灯已就位，继续调偶"); }
	return Snapshot.bPuppetRequired ? LOCTEXT("AdjustBoth", "继续调整灯与偶") : LOCTEXT("AdjustLight", "继续调整灯");
}

FText UDYInteractionHUDWidget::GetAlignmentReadinessText(const FDYPlayerAlignmentDisplay& Snapshot)
{
	if (!Snapshot.bEnabled || !Snapshot.bHasValidSample) { return FText::GetEmpty(); }
	const FText Light = Snapshot.bLightReady ? LOCTEXT("LightCheck", "灯：已就位") : LOCTEXT("LightPending", "灯：待调整");
	const FText Puppet = Snapshot.bPuppetReady ? LOCTEXT("PuppetCheck", "偶：已就位") : LOCTEXT("PuppetPending", "偶：待调整");
	if (Snapshot.bLightRequired && Snapshot.bPuppetRequired) { return FText::Format(LOCTEXT("ReadinessPair", "{0}　 · 　{1}"), Light, Puppet); }
	if (Snapshot.bLightRequired) { return Light; }
	return Snapshot.bPuppetRequired ? Puppet : FText::GetEmpty();
}

bool UDYInteractionHUDWidget::ShouldShowHoldProgress(const FDYPlayerAlignmentDisplay& Snapshot, EDYStageFeedbackDisplay Display)
{
	return Snapshot.bEnabled && Snapshot.bHasValidSample && Snapshot.bHolding
		&& Snapshot.bJointReady && Display == EDYStageFeedbackDisplay::Holding;
}

FText UDYInteractionHUDWidget::GetActStatusText(const FDYActSequenceSnapshot& Snapshot, EDYStageFeedbackDisplay Display)
{
	if (Snapshot.bSequenceEnabled)
	{
		switch (Snapshot.Phase)
		{
		case EDYActSequencePhase::AwaitingTransition:
			return LOCTEXT("AwaitingActTransition", "本幕已成 · 下幕请重新调整灯与皮影");
		case EDYActSequencePhase::AwaitingFinale:
			switch (Snapshot.ChapterIndex)
			{
			case 1: return LOCTEXT("AwaitingJingweiFinale", "石影已合，静待填海成洲");
			case 2: return LOCTEXT("AwaitingXingtianFinale", "干戚已成，静待本幕落定");
			case 3: return LOCTEXT("AwaitingZhulongFinale", "昼夜相合，静待四幕落定");
			default: return LOCTEXT("AwaitingForest", "影形已合，静待杖落成林");
			}
		case EDYActSequencePhase::Complete:
			return LOCTEXT("SequenceComplete", "复演已成");
		default:
			break;
		}
	}
	return GetStatusText(Display);
}

TSharedRef<SWidget> UDYInteractionHUDWidget::RebuildWidget()
{
	if (!ChineseFont)
	{
		if (GetWorld() && GetWorld()->IsGameWorld())
		{
			UE_LOG(LogDengYingShanHai, Warning, TEXT("Player HUD is missing its project Chinese Font; no system fallback is used."));
		}
		return Super::RebuildWidget();
	}
	// A native UMG prototype tree, not AHUD Canvas. Blueprint defaults author font,
	// title and style; there are deliberately no guessed Blueprint event graphs.
	if (WidgetTree && !Prompt) { BuildNativePrototype(); }
	RefreshView();
	return Super::RebuildWidget();
}

void UDYInteractionHUDWidget::BuildNativePrototype()
{
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("DYRoot"));
	WidgetTree->RootWidget = Root;
	SetVisibility(ESlateVisibility::HitTestInvisible);

	auto MakeText = [this](FName Name, int32 Size, FLinearColor Color)
	{
		UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), Name);
		Text->SetFont(FSlateFontInfo(ChineseFont, Size, TEXT("Regular")));
		Text->SetColorAndOpacity(FSlateColor(Color));
		Text->SetJustification(ETextJustify::Center);
		Text->SetShadowColorAndOpacity(FLinearColor(0.0f, 0.0f, 0.0f, 0.85f));
		Text->SetShadowOffset(FVector2D(1.0, 1.0));
		return Text;
	};
	TitleText = MakeText(TEXT("DYActTitle"), BodyFontSize + 2, AccentColor);
	UCanvasPanelSlot* TitleSlot = Root->AddChildToCanvas(TitleText);
	TitleSlot->SetAnchors(FAnchors(0.5f, 0.0f));
	TitleSlot->SetAlignment(FVector2D(0.5, 0.0));
	TitleSlot->SetPosition(FVector2D(0.0, 26.0));
	TitleSlot->SetAutoSize(true);

	UBorder* Back = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("DYPromptBack"));
	Back->SetBrushColor(FLinearColor(0.035f, 0.022f, 0.012f, 0.92f));
	Back->SetPadding(FMargin(24.0f, 10.0f));
	PromptBack = Back;
	UCanvasPanelSlot* BackSlot = Root->AddChildToCanvas(Back);
	BackSlot->SetAnchors(FAnchors(0.5f, 1.0f));
	BackSlot->SetAlignment(FVector2D(0.5, 1.0));
	BackSlot->SetPosition(FVector2D(0.0, -26.0));
	BackSlot->SetAutoSize(true);
	UVerticalBox* Lines = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("DYLines"));
	Back->SetContent(Lines);
	Prompt = MakeText(TEXT("DYPrompt"), BodyFontSize, PaperColor);
	Status = MakeText(TEXT("DYStatus"), BodyFontSize, AccentColor);
	Lines->AddChildToVerticalBox(Prompt)->SetHorizontalAlignment(HAlign_Center);
	UVerticalBoxSlot* StatusSlot = Lines->AddChildToVerticalBox(Status);
	StatusSlot->SetHorizontalAlignment(HAlign_Center);
	StatusSlot->SetPadding(FMargin(0.0f, 4.0f, 0.0f, 0.0f));
	Readiness = MakeText(TEXT("DYReadiness"), BodyFontSize - 2, PaperColor);
	UVerticalBoxSlot* ReadinessSlot = Lines->AddChildToVerticalBox(Readiness);
	ReadinessSlot->SetHorizontalAlignment(HAlign_Center);
	ReadinessSlot->SetPadding(FMargin(0.0f, 4.0f, 0.0f, 0.0f));
	HoldProgressBox = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass(), TEXT("DYHoldProgressBox"));
	HoldProgressBox->SetWidthOverride(260.0f);
	HoldProgressBox->SetHeightOverride(7.0f);
	HoldProgress = WidgetTree->ConstructWidget<UProgressBar>(UProgressBar::StaticClass(), TEXT("DYHoldProgress"));
	HoldProgress->SetFillColorAndOpacity(AccentColor);
	HoldProgressBox->SetContent(HoldProgress);
	UVerticalBoxSlot* BarSlot = Lines->AddChildToVerticalBox(HoldProgressBox);
	BarSlot->SetHorizontalAlignment(HAlign_Center);
	BarSlot->SetPadding(FMargin(0.0f, 7.0f, 0.0f, 0.0f));

	const FVector2D Positions[] = {{-1.0, -12.0}, {-1.0, 3.0}, {-12.0, -1.0}, {3.0, -1.0}, {-1.0, -1.0}};
	const FVector2D Sizes[] = {{2.0, 9.0}, {2.0, 9.0}, {9.0, 2.0}, {9.0, 2.0}, {2.0, 2.0}};
	for (int32 Index = 0; Index < UE_ARRAY_COUNT(Positions); ++Index)
	{
		UBorder* Arm = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), *FString::Printf(TEXT("DYCrosshair%d"), Index));
		Arm->SetPadding(FMargin(0.0f));
		UCanvasPanelSlot* ArmSlot = Root->AddChildToCanvas(Arm);
		ArmSlot->SetAnchors(FAnchors(0.5f, 0.5f));
		ArmSlot->SetPosition(Positions[Index]);
		ArmSlot->SetSize(Sizes[Index]);
		Crosshair.Add(Arm);
	}

}

void UDYInteractionHUDWidget::ShowHint(const FText& InText, float Seconds)
{
	if (InText.IsEmpty() || Seconds <= 0.0f) { HideHint(); return; }
	// The separate mid-screen plaque never drew on the packaged build (its canvas
	// slot measured 0x0 even with a fixed size), so the guidance reuses the bottom
	// plaque that the stage instrumentation already proves renders.
	bHintOverride = true;
	HintOverrideText = InText;
	RefreshView();
	if (FPlatformMisc::GetEnvironmentVariable(TEXT("DY_ENTRY_PROBE")).Equals(TEXT("1")))
	{
		// Shipping drops UE_LOG to nowhere; the packaged-game probe file is the only evidence channel.
		const FString ProbePath = FPaths::ProjectSavedDir() / TEXT("EntryWalkProbe.log");
		const FVector2D HintSize = PromptBack ? PromptBack->GetTickSpaceGeometry().GetLocalSize() : FVector2D::ZeroVector;
		const FVector2D HintPos = PromptBack ? PromptBack->GetTickSpaceGeometry().GetAbsolutePosition() : FVector2D::ZeroVector;
		const FString FontName = (Status && Status->GetFont().FontObject) ? Status->GetFont().FontObject->GetName() : FString(TEXT("none"));
		const FString Line = FString::Printf(TEXT("ShowHint text=%s back=%d status=%d world=%d size=%.0fx%.0f at=%.0f,%.0f font=%s"),
			*InText.ToString().Left(16), PromptBack ? static_cast<int32>(PromptBack->GetVisibility()) : -1,
			Status ? static_cast<int32>(Status->GetVisibility()) : -1, GetWorld() ? 1 : 0,
			HintSize.X, HintSize.Y, HintPos.X, HintPos.Y, *FontName) + LINE_TERMINATOR;
		FFileHelper::SaveStringToFile(Line, *ProbePath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,
			&IFileManager::Get(), EFileWrite::FILEWRITE_Append);
	}
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(HintHandle);
		World->GetTimerManager().SetTimer(HintHandle, FTimerDelegate::CreateUObject(this, &UDYInteractionHUDWidget::HideHint), Seconds, false);
	}
}

void UDYInteractionHUDWidget::SetPerformancePresentation(bool bActive)
{
	if (bPerformancePresentation == bActive) { return; }
	bPerformancePresentation = bActive;
	PerformanceCaptionText = FText::GetEmpty();
	// A stale walk/status timer must not bring its line back after a show starts.
	if (UWorld* World = GetWorld()) { World->GetTimerManager().ClearTimer(HintHandle); }
	bHintOverride = false;
	HintOverrideText = FText::GetEmpty();
	RefreshView();
}

void UDYInteractionHUDWidget::ShowPerformanceCaption(const FText& InText)
{
	SetPerformancePresentation(true);
	PerformanceCaptionText = InText;
	RefreshView();
}

void UDYInteractionHUDWidget::SetEntryWalkGuide(bool bActive, const FText& InText)
{
	bEntryWalkGuide = bActive && !InText.IsEmpty();
	EntryWalkGuideText = InText;
	// Entry guidance borrows the bottom plaque: it is the one element already proven
	// to draw on the packaged build. The widget itself stays visible so UMG keeps
	// laying the canvas out (a hidden root reports 0x0 geometry).
	bHintOverride = false;
	RefreshView();
}

void UDYInteractionHUDWidget::SetStageHudVisible(bool bVisible)
{
	if (bStageHudVisible == bVisible) { return; }
	bStageHudVisible = bVisible;
	RefreshView();
}

void UDYInteractionHUDWidget::HideHint()
{
	if (UWorld* World = GetWorld()) { World->GetTimerManager().ClearTimer(HintHandle); }
	if (bHintOverride)
	{
		bHintOverride = false;
		HintOverrideText = FText::GetEmpty();
		RefreshView();
	}
	if (FPlatformMisc::GetEnvironmentVariable(TEXT("DY_ENTRY_PROBE")).Equals(TEXT("1")))
	{
		const FString ProbePath = FPaths::ProjectSavedDir() / TEXT("EntryWalkProbe.log");
		FFileHelper::SaveStringToFile(FString(TEXT("HideHint") ) + LINE_TERMINATOR, *ProbePath,
			FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), EFileWrite::FILEWRITE_Append);
	}
}

void UDYInteractionHUDWidget::ApplySnapshot(bool bHasFocus, bool bIsControlling, EDYStageFeedbackDisplay Display)
{
	bFocused = bHasFocus;
	bControlling = bIsControlling;
	Feedback = Display;
	RefreshView();
}

bool UDYInteractionHUDWidget::ShouldShowChapterCard(const FDYActSequenceSnapshot& Snapshot, int32 LastShownChapterIndex)
{
	// Only the four-act campaign has more than one chapter; the single-act fixtures and
	// the dev sequences keep the plain step title.
	return Snapshot.bSequenceEnabled && Snapshot.ChapterCount > 1 && Snapshot.ChapterIndex >= 0
		&& Snapshot.ChapterIndex != LastShownChapterIndex && !Snapshot.ChapterTitle.IsEmpty();
}

FText UDYInteractionHUDWidget::MakeChapterCardText(const FDYActSequenceSnapshot& Snapshot)
{
	if (!Snapshot.bSequenceEnabled || Snapshot.ChapterCount <= 1) { return FText::GetEmpty(); }
	return Snapshot.ChapterTitle;
}

bool UDYInteractionHUDWidget::IsStageReached() const
{
	const APawn* Pawn = GetOwningPlayerPawn();
	return Pawn != nullptr && Pawn->GetActorLocation().X > DYEntryWalk::TheaterThresholdX;
}

void UDYInteractionHUDWidget::ShowChapterCard(const FText& InText)
{
	if (InText.IsEmpty()) { return; }
	bChapterCardActive = true;
	ChapterCardText = InText;
	if (FPlatformMisc::GetEnvironmentVariable(TEXT("DY_ENTRY_PROBE")).Equals(TEXT("1")))
	{
		const FString ProbePath = FPaths::ProjectSavedDir() / TEXT("EntryWalkProbe.log");
		const FString Line = FString::Printf(TEXT("ChapterCard text=%s chapter=%d/%d stage=%d walk=%d"),
			*InText.ToString().Left(16), ActDisplay.ChapterIndex, ActDisplay.ChapterCount,
			bStageHudVisible ? 1 : 0, bEntryWalkGuide ? 1 : 0) + LINE_TERMINATOR;
		FFileHelper::SaveStringToFile(Line, *ProbePath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,
			&IFileManager::Get(), EFileWrite::FILEWRITE_Append);
	}
	RefreshView();
}

void UDYInteractionHUDWidget::StartChapterCardCountdown()
{
	UWorld* World = GetWorld();
	if (World == nullptr) { return; }
	bChapterCardCountdown = true;
	World->GetTimerManager().ClearTimer(ChapterCardHandle);
	World->GetTimerManager().SetTimer(ChapterCardHandle,
		FTimerDelegate::CreateUObject(this, &UDYInteractionHUDWidget::HideChapterCard), ChapterCardSeconds, false);
}

void UDYInteractionHUDWidget::HideChapterCard()
{
	if (UWorld* World = GetWorld()) { World->GetTimerManager().ClearTimer(ChapterCardHandle); }
	bChapterCardCountdown = false;
	if (!bChapterCardActive) { return; }
	bChapterCardActive = false;
	ChapterCardText = FText::GetEmpty();
	RefreshView();
	if (FPlatformMisc::GetEnvironmentVariable(TEXT("DY_ENTRY_PROBE")).Equals(TEXT("1")))
	{
		const FString ProbePath = FPaths::ProjectSavedDir() / TEXT("EntryWalkProbe.log");
		FFileHelper::SaveStringToFile(FString(TEXT("ChapterCardHidden")) + LINE_TERMINATOR, *ProbePath,
			FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), EFileWrite::FILEWRITE_Append);
	}
}

void UDYInteractionHUDWidget::ApplyActSnapshot(const FDYActSequenceSnapshot& Snapshot)
{
	ActDisplay = Snapshot;
	if (ShouldShowChapterCard(ActDisplay, LastChapterCardIndex))
	{
		LastChapterCardIndex = ActDisplay.ChapterIndex;
		ShowChapterCard(MakeChapterCardText(ActDisplay));
	}
	RefreshView();
}

void UDYInteractionHUDWidget::ApplyAlignmentSnapshot(const FDYPlayerAlignmentDisplay& Snapshot)
{
	AlignmentDisplay = Snapshot;
	RefreshView();
}

void UDYInteractionHUDWidget::RefreshView()
{
	const FText& CurrentTitle = ActDisplay.bSequenceEnabled && !ActDisplay.ActTitle.IsEmpty() ? ActDisplay.ActTitle : ActTitle;
	// The chapter card borrows the title line for a few seconds, but only once the stage
	// HUD is actually on screen: the entry walk must stay free of chapter titles.
	const bool bShowChapterCard = bChapterCardActive && !ChapterCardText.IsEmpty() && bStageHudVisible
		&& !bEntryWalkGuide && !bPerformancePresentation && IsStageReached();
	if (bShowChapterCard && !bChapterCardCountdown) { StartChapterCardCountdown(); }
	const FText& DisplayTitle = bShowChapterCard ? ChapterCardText : CurrentTitle;
	if (TitleText)
	{
		TitleText->SetText(DisplayTitle);
		TitleText->SetFont(FSlateFontInfo(ChineseFont, bShowChapterCard ? BodyFontSize + 8 : BodyFontSize + 2, TEXT("Regular")));
	}
	if (Prompt) { Prompt->SetText(GetPromptText(bFocused, bControlling)); }
	// The entry walk owns the screen: the play instrumentation would otherwise read
	// as a puzzle instruction while the player is still in the 山海 exterior.
	const ESlateVisibility StageVisibility = (bStageHudVisible && !bEntryWalkGuide && !bPerformancePresentation) ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed;
	if (TitleText) { TitleText->SetVisibility(StageVisibility); }
	if (PromptBack) { PromptBack->SetVisibility(StageVisibility); }
	// Restored every pass so the hint override below never leaves the prompt hidden.
	if (Prompt) { Prompt->SetVisibility(ESlateVisibility::HitTestInvisible); }
	if (Status)
	{
		FText Line = GetActStatusText(ActDisplay, Feedback);
		const bool bPlaying = !ActDisplay.bSequenceEnabled || ActDisplay.Phase == EDYActSequencePhase::Playing;
		if (bPlaying && AlignmentDisplay.bEnabled) { Line = GetAlignmentStatusText(AlignmentDisplay, Feedback); }
		// Preserve the legacy single-act wording; sequence transitions/finale have
		// their own explicit text and must not report a whole-play finish early.
		const bool bPlainActComplete = !ActDisplay.bSequenceEnabled || ActDisplay.Phase == EDYActSequencePhase::Playing;
		if (bPlainActComplete && Feedback == EDYStageFeedbackDisplay::Complete && !CurrentTitle.IsEmpty())
		{
			Line = FText::Format(LOCTEXT("ActComplete", "{0} · 成"), CurrentTitle);
		}
		Status->SetFont(FSlateFontInfo(ChineseFont, bPerformancePresentation ? BodyFontSize + 2 : BodyFontSize, TEXT("Regular")));
		Status->SetColorAndOpacity(FSlateColor(bPerformancePresentation ? PaperColor : AccentColor));
		Status->SetText(Line);
		Status->SetVisibility(!bStageHudVisible || Line.IsEmpty() ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
	}
	if (bHintOverride)
	{
		// Entry guidance borrows the bottom plaque: it is the one element already
		// proven to draw on the packaged build.
		if (PromptBack) { PromptBack->SetVisibility(ESlateVisibility::HitTestInvisible); }
		if (Prompt) { Prompt->SetVisibility(ESlateVisibility::Collapsed); }
		if (Status)
		{
			Status->SetText(HintOverrideText);
			Status->SetVisibility(HintOverrideText.IsEmpty() ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
		}
	}
	if (bEntryWalkGuide)
	{
		if (TitleText) { TitleText->SetVisibility(ESlateVisibility::Collapsed); }
		if (PromptBack) { PromptBack->SetVisibility(ESlateVisibility::HitTestInvisible); }
		if (Prompt) { Prompt->SetVisibility(ESlateVisibility::Collapsed); }
		if (Status)
		{
			Status->SetText(EntryWalkGuideText);
			Status->SetVisibility(ESlateVisibility::HitTestInvisible);
		}
		if (Readiness) { Readiness->SetVisibility(ESlateVisibility::Collapsed); }
		if (HoldProgressBox) { HoldProgressBox->SetVisibility(ESlateVisibility::Collapsed); }
	}
	if (bPerformancePresentation)
	{
		if (TitleText) { TitleText->SetVisibility(ESlateVisibility::Collapsed); }
		if (PromptBack) { PromptBack->SetVisibility(PerformanceCaptionText.IsEmpty() ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible); }
		if (Prompt) { Prompt->SetVisibility(ESlateVisibility::Collapsed); }
		if (Status)
		{
			Status->SetText(PerformanceCaptionText);
			Status->SetVisibility(PerformanceCaptionText.IsEmpty() ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
		}
	}
	const bool bAlignmentVisible = bStageHudVisible && !bEntryWalkGuide && !bPerformancePresentation && AlignmentDisplay.bEnabled && AlignmentDisplay.bHasValidSample
		&& (!ActDisplay.bSequenceEnabled || ActDisplay.Phase == EDYActSequencePhase::Playing)
		&& Feedback != EDYStageFeedbackDisplay::Hidden && Feedback != EDYStageFeedbackDisplay::Complete;
	if (Readiness)
	{
		Readiness->SetText(bAlignmentVisible ? GetAlignmentReadinessText(AlignmentDisplay) : FText::GetEmpty());
		Readiness->SetVisibility(bAlignmentVisible ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
		Readiness->SetColorAndOpacity(FSlateColor(AlignmentDisplay.bJointReady ? AccentColor : PaperColor));
	}
	if (HoldProgress && HoldProgressBox)
	{
		const bool bShowBar = bAlignmentVisible && ShouldShowHoldProgress(AlignmentDisplay, Feedback);
		HoldProgress->SetPercent(bShowBar && FMath::IsFinite(AlignmentDisplay.HoldFraction) ? static_cast<float>(FMath::Clamp(AlignmentDisplay.HoldFraction, 0.0, 1.0)) : 0.0f);
		HoldProgressBox->SetVisibility(bShowBar ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	}
	const FLinearColor Color = bFocused && !bControlling ? FLinearColor(0.15f, 1.0f, 0.35f, 1.0f) : PaperColor;
	for (UBorder* Arm : Crosshair)
	{
		if (!Arm) { continue; }
		Arm->SetBrushColor(Color);
		Arm->SetVisibility(StageVisibility);
	}
}

#undef LOCTEXT_NAMESPACE
