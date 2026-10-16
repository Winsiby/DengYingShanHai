#include "UI/DYDevEntryWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Core/DYDevEntryPlayerController.h"
#include "Engine/Font.h"
#include "UObject/ConstructorHelpers.h"

#define LOCTEXT_NAMESPACE "DYDevEntry"

UDYDevEntryWidget::UDYDevEntryWidget(const FObjectInitializer& Initializer) : Super(Initializer)
{
	SetIsFocusable(true);
	static ConstructorHelpers::FObjectFinder<UFont> Font(TEXT("/Game/DengYingShanHai/Dev/M2/UI/FF_DYSourceHanSansSC_Font.FF_DYSourceHanSansSC_Font"));
	ChineseFont = Font.Object;
}

FText UDYDevEntryWidget::GetTitle(EDYDevEntryPanel Panel)
{
	return Panel == EDYDevEntryPanel::End ? LOCTEXT("EndTitle", "复演已成") : LOCTEXT("Title", "灯影山海");
}

FText UDYDevEntryWidget::GetPrimaryLabel(EDYDevEntryPanel Panel)
{
	switch (Panel)
	{
	case EDYDevEntryPanel::Start: return LOCTEXT("Start", "开始复演");
	case EDYDevEntryPanel::End: return LOCTEXT("Replay", "重新复演");
	case EDYDevEntryPanel::Reloading: return LOCTEXT("Reloading", "正在重新载入");
	default: return LOCTEXT("Waiting", "舞台准备中");
	}
}

FText UDYDevEntryWidget::GetBody(EDYDevEntryPanel Panel)
{
	if (Panel == EDYDevEntryPanel::End) { return LOCTEXT("EndBody", "杖落成林，未完的戏终于演到此刻。\n画面将保留；重新复演会重新载入本场。 "); }
	return LOCTEXT("StartBody", "一座久未开演的影戏台，《逐日》停在夸父尚未落杖的时刻。\n以灯为日，以影为夸父，让这出未完的戏继续。");
}

bool UDYDevEntryWidget::HasReadyView() const { return ChineseFont && PrimaryButton && QuitButton; }
UWidget* UDYDevEntryWidget::GetPrimaryFocusWidget() const { return PrimaryButton; }

TSharedRef<SWidget> UDYDevEntryWidget::RebuildWidget()
{
	if (WidgetTree && ChineseFont && !PrimaryButton) { BuildView(); }
	RefreshView();
	return Super::RebuildWidget();
}

void UDYDevEntryWidget::BuildView()
{
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("EntryRoot"));
	WidgetTree->RootWidget = Root;
	Backdrop = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("Backdrop"));
	Root->AddChildToCanvas(Backdrop)->SetAnchors(FAnchors(0, 0, 1, 1));
	CastChecked<UCanvasPanelSlot>(Backdrop->Slot)->SetOffsets(FMargin(0));
	UBorder* Card = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("MenuCard"));
	Card->SetBrushColor(FLinearColor(.035f, .022f, .012f, .94f));
	Card->SetPadding(FMargin(28));
	CardSlot = Root->AddChildToCanvas(Card);
	CardSlot->SetAlignment(FVector2D(.5, .5));
	CardSlot->SetAutoSize(true);
	UVerticalBox* Lines = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("Lines"));
	Card->SetContent(Lines);
	auto Text = [this](FName Name, int32 Size, FLinearColor Color)
	{
		UTextBlock* Item = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), Name);
		Item->SetFont(FSlateFontInfo(ChineseFont, Size, TEXT("Regular")));
		Item->SetColorAndOpacity(FSlateColor(Color));
		Item->SetJustification(ETextJustify::Center);
		return Item;
	};
	const FLinearColor Gold(.94f, .72f, .39f, 1), Paper(.93f, .89f, .80f, 1);
	Title = Text(TEXT("Title"), 34, Gold);
	Body = Text(TEXT("Body"), 20, Paper);
	Lines->AddChildToVerticalBox(Title)->SetHorizontalAlignment(HAlign_Center);
	Lines->AddChildToVerticalBox(Body)->SetPadding(FMargin(0, 18, 0, 18));
	PrimaryButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), TEXT("Primary"));
	constexpr int32 ButtonFontSize = 24;
	PrimaryLabel = Text(TEXT("PrimaryLabel"), ButtonFontSize, FLinearColor(.09f, .06f, .025f, 1));
	PrimaryButton->SetContent(PrimaryLabel);
	PrimaryButton->SetBackgroundColor(Gold);
	Lines->AddChildToVerticalBox(PrimaryButton)->SetPadding(FMargin(70, 4, 70, 8));
	QuitButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), TEXT("Quit"));
	UTextBlock* Quit = Text(TEXT("QuitLabel"), ButtonFontSize, FLinearColor(.12f, .08f, .045f, 1));
	Quit->SetText(LOCTEXT("Quit", "退出游戏"));
	QuitButton->SetContent(Quit);
	Lines->AddChildToVerticalBox(QuitButton)->SetPadding(FMargin(70, 4, 70, 8));
	UTextBlock* Footer = Text(TEXT("Footer"), 16, Paper);
	Footer->SetText(LOCTEXT("DevFooter", "单人制作 · Dev 流程验证 · 尚非正式美术"));
	Lines->AddChildToVerticalBox(Footer)->SetPadding(FMargin(0, 16, 0, 0));
}

void UDYDevEntryWidget::NativeConstruct()
{
	Super::NativeConstruct();
	if (PrimaryButton) { PrimaryButton->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandlePrimaryClick); }
	if (QuitButton) { QuitButton->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleQuitClick); }
	RefreshView();
}

void UDYDevEntryWidget::NativeDestruct()
{
	if (PrimaryButton) { PrimaryButton->OnClicked.RemoveDynamic(this, &UDYDevEntryWidget::HandlePrimaryClick); }
	if (QuitButton) { QuitButton->OnClicked.RemoveDynamic(this, &UDYDevEntryWidget::HandleQuitClick); }
	Super::NativeDestruct();
}

void UDYDevEntryWidget::ApplyPanel(EDYDevEntryPanel Panel) { CurrentPanel = Panel; RefreshView(); }

void UDYDevEntryWidget::RefreshView()
{
	SetVisibility(CurrentPanel == EDYDevEntryPanel::Hidden ? ESlateVisibility::Collapsed : ESlateVisibility::Visible);
	if (Title) { Title->SetText(GetTitle(CurrentPanel)); }
	if (Body) { Body->SetText(GetBody(CurrentPanel)); }
	if (PrimaryLabel) { PrimaryLabel->SetText(GetPrimaryLabel(CurrentPanel)); }
	if (PrimaryButton) { PrimaryButton->SetIsEnabled(CurrentPanel == EDYDevEntryPanel::Start || CurrentPanel == EDYDevEntryPanel::End); }
	const bool bEnd = CurrentPanel == EDYDevEntryPanel::End || CurrentPanel == EDYDevEntryPanel::Reloading;
	if (Backdrop) { Backdrop->SetBrushColor(FLinearColor(0, 0, 0, bEnd ? 0.0f : .58f)); }
	if (CardSlot) { CardSlot->SetAnchors(FAnchors(.5f, bEnd ? .83f : .5f)); }
}

void UDYDevEntryWidget::HandlePrimaryClick()
{
	if (ADYDevEntryPlayerController* PC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer()))
	{
		if (CurrentPanel == EDYDevEntryPanel::Start) { PC->RequestStartExperience(); }
		else if (CurrentPanel == EDYDevEntryPanel::End) { PC->RequestReplayExperience(); }
	}
}

void UDYDevEntryWidget::HandleQuitClick()
{
	if (ADYDevEntryPlayerController* PC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer())) { PC->RequestQuitExperience(); }
}

#undef LOCTEXT_NAMESPACE
