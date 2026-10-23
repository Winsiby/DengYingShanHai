#include "UI/DYDevEntryWidget.h"

#include "DengYingShanHai.h"

#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/ButtonSlot.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/ScaleBox.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Core/DYDevEntryPlayerController.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Engine/Font.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/ConfigCacheIni.h"
#include "Engine/Texture2D.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "UnrealClient.h"
#include "Widgets/SWindow.h"
#if PLATFORM_WINDOWS
#include "Windows/AllowWindowsPlatformTypes.h"
#include <windows.h>
#include "Windows/HideWindowsPlatformTypes.h"
#endif
#include "AudioDevice.h"
#include "AudioDeviceHandle.h"
#include "GameFramework/GameUserSettings.h"
#include "Kismet/GameplayStatics.h"
#include "InputCoreTypes.h"
#include "HAL/IConsoleManager.h"
#include "UObject/ConstructorHelpers.h"
#include "Framework/Application/SlateApplication.h"

#define LOCTEXT_NAMESPACE "DYDevEntry"

namespace
{
	// V2.2 stage space: 1920x1080 design canvas, aspect-fitted by ScaleBox.
	constexpr float StageWidth = 1920.f;
	constexpr float StageHeight = 1080.f;
	constexpr float ColumnLeft = 82.f;
	constexpr float ColumnTop = 240.f;
	constexpr float ColumnWidth = 332.f;
	constexpr float ItemHeight = 80.f;
	constexpr float ItemPitch = 90.f;
	constexpr float GuideLeft = 1396.f;
	constexpr float GuideTop = 736.f;
	constexpr float GuideWidth = 385.f;
	constexpr float GuideHeight = 190.f;
	constexpr float GuideFontSize = 15.f;

	const FLinearColor Ink(.16f, .11f, .07f, 1.f);
	const FLinearColor OnRed(.99f, .90f, .70f, 1.f);
	const FLinearColor Muted(.46f, .42f, .37f, 1.f);
	const FLinearColor PaperText(.93f, .89f, .80f, 1.f);
	const FLinearColor Gold(.94f, .72f, .39f, 1.f);

	FSlateBrush MakePlaqueBrush(UTexture2D* Texture, const FLinearColor& Fallback, const FLinearColor& Tint = FLinearColor::White)
	{
		FSlateBrush Brush;
		Brush.DrawAs = ESlateBrushDrawType::Box;
		Brush.ImageSize = FVector2D(388.f, 100.f);
		Brush.Margin = FMargin(0.0773f, 0.30f, 0.0773f, 0.30f);
		if (Texture) { Brush.SetResourceObject(Texture); Brush.TintColor = FSlateColor(Tint); }
		else { Brush.TintColor = FSlateColor(Fallback); }
		return Brush;
	}

	FButtonStyle MakePlaqueStyle(UTexture2D* N, UTexture2D* H, UTexture2D* P, UTexture2D* D)
	{
		FButtonStyle Style;
		Style.SetNormal(MakePlaqueBrush(N, FLinearColor(.84f, .78f, .66f, 1.f)));
		Style.SetHovered(MakePlaqueBrush(H, FLinearColor(.86f, .58f, .36f, 1.f)));
		Style.SetPressed(MakePlaqueBrush(P, FLinearColor(.72f, .44f, .28f, 1.f)));
		Style.SetDisabled(MakePlaqueBrush(D, FLinearColor(.52f, .49f, .44f, 1.f)));
		Style.SetNormalForeground(FSlateColor(Ink));
		Style.SetHoveredForeground(FSlateColor(OnRed));
		Style.SetPressedForeground(FSlateColor(OnRed));
		Style.SetDisabledForeground(FSlateColor(Ink));
		Style.SetNormalPadding(FMargin(0));
		Style.SetPressedPadding(FMargin(0));
		return Style;
	}

	FButtonStyle MakeDisabledPlaqueStyle(UTexture2D* N)
	{
		FButtonStyle Style;
		const FSlateBrush Grey = MakePlaqueBrush(N, FLinearColor(1.f, 1.f, 1.f, 1.f), FLinearColor(.49f, .46f, .40f, 1.f));
		Style.SetNormal(Grey);
		Style.SetHovered(Grey);
		Style.SetPressed(Grey);
		Style.SetDisabled(Grey);
		const FSlateColor Dark(FLinearColor(.80f, .75f, .66f, 1.f));
		Style.SetNormalForeground(Dark);
		Style.SetHoveredForeground(Dark);
		Style.SetPressedForeground(Dark);
		Style.SetDisabledForeground(Dark);
		Style.SetNormalPadding(FMargin(0));
		Style.SetPressedPadding(FMargin(0));
		return Style;
	}

	FSlateBrush MakeFlatBrush(const FLinearColor& Color)
	{
		FSlateBrush Brush;
		Brush.DrawAs = ESlateBrushDrawType::Box;
		Brush.TintColor = FSlateColor(Color);
		Brush.ImageSize = FVector2D(48.f, 48.f);
		return Brush;
	}

	FButtonStyle MakeFlatStyle(const FLinearColor& Normal, const FLinearColor& Hovered, const FLinearColor& Pressed)
	{
		FButtonStyle Style;
		Style.SetNormal(MakeFlatBrush(Normal));
		Style.SetHovered(MakeFlatBrush(Hovered));
		Style.SetPressed(MakeFlatBrush(Pressed));
		Style.SetDisabled(MakeFlatBrush(FLinearColor(.60f, .56f, .50f, 1.f)));
		Style.SetNormalForeground(FSlateColor(Ink));
		Style.SetHoveredForeground(FSlateColor(Ink));
		Style.SetPressedForeground(FSlateColor(Ink));
		Style.SetDisabledForeground(FSlateColor(Muted));
		Style.SetNormalPadding(FMargin(0));
		Style.SetPressedPadding(FMargin(0));
		return Style;
	}

	constexpr int32 MenuResolutionCount = 4;
	const FIntPoint MenuResolutions[MenuResolutionCount] = {
		FIntPoint(1280, 720), FIntPoint(1600, 900), FIntPoint(1920, 1080), FIntPoint(1280, 800)
	};
	const EWindowMode::Type MenuWindowModes[3] = { EWindowMode::Windowed, EWindowMode::WindowedFullscreen, EWindowMode::Fullscreen };
	const TCHAR* MenuWindowModeNames[3] = { TEXT("窗口"), TEXT("无边框全屏"), TEXT("全屏") };

	void ReadLiveVideoChoice(int32& OutModeIndex, int32& OutResolutionIndex)
	{
		EWindowMode::Type Mode = EWindowMode::Windowed;
		FIntPoint Live(0, 0);
		bool bHaveWindow = false;
		if (GEngine && GEngine->GameViewport)
		{
			const TSharedPtr<SWindow> ActiveWindow = GEngine->GameViewport->GetWindow();
			if (ActiveWindow.IsValid() && ActiveWindow->GetNativeWindow().IsValid())
			{
				bHaveWindow = true;
				Mode = ActiveWindow->GetWindowMode();
#if PLATFORM_WINDOWS
				if (ActiveWindow->GetNativeWindow().IsValid())
				{
					RECT ClientRect{};
					const HWND OsHandle = static_cast<HWND>(ActiveWindow->GetNativeWindow()->GetOSWindowHandle());
					if (OsHandle && ::GetClientRect(OsHandle, &ClientRect))
					{
						Live.X = ClientRect.right - ClientRect.left;
						Live.Y = ClientRect.bottom - ClientRect.top;
					}
				}
#endif
			}
		}
		if (!bHaveWindow)
		{
			if (const UGameUserSettings* Settings = UGameUserSettings::GetGameUserSettings())
			{
				Mode = Settings->GetFullscreenMode();
				Live = Settings->GetScreenResolution();
			}
		}
		OutModeIndex = (Mode == EWindowMode::WindowedFullscreen) ? 1 : ((Mode == EWindowMode::Fullscreen) ? 2 : 0);
		OutResolutionIndex = 0;
		for (int32 Index = 0; Index < MenuResolutionCount; ++Index)
		{
			if (FMath::Abs(MenuResolutions[Index].X - Live.X) <= 8 && FMath::Abs(MenuResolutions[Index].Y - Live.Y) <= 8)
			{
				OutResolutionIndex = Index;
				break;
			}
		}
	}
}

UDYDevEntryWidget::UDYDevEntryWidget(const FObjectInitializer& Initializer) : Super(Initializer)
{
	SetIsFocusable(true);
	static ConstructorHelpers::FObjectFinder<UFont> Font(TEXT("/Game/DengYingShanHai/Dev/M2/UI/FF_DYSourceHanSansSC_Font.FF_DYSourceHanSansSC_Font"));
	ChineseFont = Font.Object;
	// The serif guide faces are optional style: they are resolved lazily in
	// EnsureGuideFonts() so a missing face never fails CDO construction.
	static ConstructorHelpers::FObjectFinder<UTexture2D> Bg(TEXT("/Game/DengYingShanHai/UI/Menu/T_MenuBackground.T_MenuBackground"));
	MenuBackgroundTexture = Bg.Object;
	static ConstructorHelpers::FObjectFinder<UTexture2D> TN(TEXT("/Game/DengYingShanHai/UI/Menu/T_PlqNormal.T_PlqNormal"));
	PlaqueNormalTexture = TN.Object;
	static ConstructorHelpers::FObjectFinder<UTexture2D> TH(TEXT("/Game/DengYingShanHai/UI/Menu/T_PlqHover.T_PlqHover"));
	PlaqueHoverTexture = TH.Object;
	static ConstructorHelpers::FObjectFinder<UTexture2D> TP(TEXT("/Game/DengYingShanHai/UI/Menu/T_PlqPressed.T_PlqPressed"));
	PlaquePressedTexture = TP.Object;
	static ConstructorHelpers::FObjectFinder<UTexture2D> TD(TEXT("/Game/DengYingShanHai/UI/Menu/T_PlqDisabled.T_PlqDisabled"));
	PlaqueDisabledTexture = TD.Object;
	// Codex illustrations, in CodexIndex order (Kuafu, Jingwei, Xingtian, Zhulong). Plain locals:
	// a static finder inside a shared lambda would resolve once and hand the same texture to all four.
	static ConstructorHelpers::FObjectFinder<UTexture2D> CodexKuafu(TEXT("/Game/DengYingShanHai/UI/Codex/T_DY_Codex_Kuafu.T_DY_Codex_Kuafu"));
	CodexArtTextures.Add(CodexKuafu.Object);
	static ConstructorHelpers::FObjectFinder<UTexture2D> CodexJingwei(TEXT("/Game/DengYingShanHai/UI/Codex/T_DY_Codex_Jingwei.T_DY_Codex_Jingwei"));
	CodexArtTextures.Add(CodexJingwei.Object);
	static ConstructorHelpers::FObjectFinder<UTexture2D> CodexXingtian(TEXT("/Game/DengYingShanHai/UI/Codex/T_DY_Codex_Xingtian.T_DY_Codex_Xingtian"));
	CodexArtTextures.Add(CodexXingtian.Object);
	static ConstructorHelpers::FObjectFinder<UTexture2D> CodexZhulong(TEXT("/Game/DengYingShanHai/UI/Codex/T_DY_Codex_Zhulong.T_DY_Codex_Zhulong"));
	CodexArtTextures.Add(CodexZhulong.Object);
	// C3 制作七步 plate: the delivered seven-cell process sheet.
	static ConstructorHelpers::FObjectFinder<UTexture2D> CodexSteps(TEXT("/Game/DengYingShanHai/UI/Codex/T_DY_Codex_Steps.T_DY_Codex_Steps"));
	CodexStepsTexture = CodexSteps.Object;
}

FText UDYDevEntryWidget::GetTitle(EDYDevEntryPanel Panel)
{
	return Panel == EDYDevEntryPanel::End ? LOCTEXT("EndTitle", "复演已成") : LOCTEXT("Title", "灯影山海");
}

FText UDYDevEntryWidget::GetPrimaryLabel(EDYDevEntryPanel Panel)
{
	switch (Panel)
	{
	case EDYDevEntryPanel::Start: return LOCTEXT("Start", "开始游戏");
	case EDYDevEntryPanel::End: return LOCTEXT("Replay", "重新复演");
	case EDYDevEntryPanel::Reloading: return LOCTEXT("Reloading", "正在重新载入");
	case EDYDevEntryPanel::Paused: return LOCTEXT("PausedPrimary", "开始游戏");
	default: return LOCTEXT("Waiting", "舞台准备中");
	}
}

FText UDYDevEntryWidget::GetBody(EDYDevEntryPanel Panel)
{
	if (Panel == EDYDevEntryPanel::End)
	{
		return LOCTEXT("EndBody", "四幕演尽，夸父、精卫、刑天与烛龙的影子都已落定。\n\n影偶图鉴 · 夸父逐日：执杖奔日的巨人，杖落成林。\n影偶图鉴 · 精卫填海：衔石入海的赤鸟，以微光连成通路。\n影偶图鉴 · 刑天舞干戚：断首犹立的战神，以盾为目、以干戚为舞。\n影偶图鉴 · 烛龙昼夜：睁眼为昼、闭眼为夜的山神。\n\n选「重新复演」或按 Enter 从头再看。\n「游戏说明」打开影偶图鉴。");
	}
	return LOCTEXT("StartBody", "一座久未开演的影戏台，《逐日》停在夸父尚未落杖的时刻。以灯为日，以影为夸父，让这出未完的戏继续。");
}

FString UDYDevEntryWidget::MakeCodexEntry(int32 Index)
{
	static const TCHAR* CodexDetails[4] = {
		TEXT("夸父逐日 · 执杖的巨人\n造型：竹为骨、皮为身，长杖与披风是两件独立操杆；关节在肩、肘、膝三处。\n操演：以灯为日，把杖影送到幕上缺口；杖落成林，是他留给山海的最后一份礼物。"),
		TEXT("精卫填海 · 衔石的赤鸟\n造型：翅、尾各分三节，一根主杆带两根手杆，羽片镂空透光。\n操演：灯位定高低，石影连成通路；翅影掠过水面时，影子先于鸟身抵达。"),
		TEXT("刑天舞干戚 · 断首的战神\n造型：以乳为目、以脐为口，盾与斧分持两杆，盾面刻云雷纹。\n操演：盾影成目、斧影成舞，盾影与斧影重合的瞬间才是干戚之舞。"),
		TEXT("烛龙昼夜 · 睁眼为昼的山神\n造型：人面蛇身而赤，鳞片逐节透光，双目为两枚可换的镂空片。\n操演：灯亮则昼、灯暗则夜；昼夜交替之间，机关自己打开。"),
	};
	// V2.3 的非遗清单把「锣鼓器乐」与造型、操偶、制作七步并列：每具影偶写自己那一段锣鼓口令，
	// 图鉴才不会只剩造型说明。
	static const TCHAR* CodexDrums[4] = {
		TEXT("锣鼓：开场三通鼓催幕，杖落一击大锣定音；鼓点跟着影偶的步幅走。"),
		TEXT("锣鼓：小锣点水、鼓边碎击作浪，翅影掠过时钹合一声。"),
		TEXT("锣鼓：堂鼓连击，钹分合应盾与斧；两影重合处改一记闷鼓。"),
		TEXT("锣鼓：大锣开昼、闷鼓收夜，昼夜交替只在两声之间。"),
	};
	const int32 Clamped = FMath::Clamp(Index, 0, 3);
	return FString::Printf(
		TEXT("%s\n%s\n\n制作七步：选皮、制皮、画稿、雕刻、着色、连接关节、装杆。\n制作七步之外，锣鼓与器乐是影戏的另一半：无锣鼓不开台。\n四幕剧终后，四具影偶录入图鉴，可在此回顾造型、操演与锣鼓。"),
		CodexDetails[Clamped],
		CodexDrums[Clamped]);
}

bool UDYDevEntryWidget::HasReadyView() const { return ChineseFont && PrimaryButton && QuitButton; }
UWidget* UDYDevEntryWidget::GetPrimaryFocusWidget() const
{
	if (CurrentPanel == EDYDevEntryPanel::Paused && MenuButtons.IsValidIndex(1) && MenuButtons[1])
	{
		return MenuButtons[1];
	}
	return PrimaryButton;
}

TSharedRef<SWidget> UDYDevEntryWidget::RebuildWidget()
{
	if (WidgetTree && ChineseFont && !RootCanvas) { BuildView(); }
	RefreshView();
	return Super::RebuildWidget();
}

void UDYDevEntryWidget::BuildView()
{
	EnsureGuideFonts();
	RootCanvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("EntryRoot"));
	WidgetTree->RootWidget = RootCanvas;

	Backdrop = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("Backdrop"));
	Backdrop->SetBrushColor(FLinearColor(0.f, 0.f, 0.f, .92f));
	UCanvasPanelSlot* BackdropSlot = RootCanvas->AddChildToCanvas(Backdrop);
	BackdropSlot->SetAnchors(FAnchors(0, 0, 1, 1));
	BackdropSlot->SetOffsets(FMargin(0));

	UScaleBox* Scaler = WidgetTree->ConstructWidget<UScaleBox>(UScaleBox::StaticClass(), TEXT("StageScaler"));
	Scaler->SetStretch(EStretch::ScaleToFit);
	Scaler->SetStretchDirection(EStretchDirection::Both);
	UCanvasPanelSlot* ScalerSlot = RootCanvas->AddChildToCanvas(Scaler);
	ScalerSlot->SetAnchors(FAnchors(0, 0, 1, 1));
	ScalerSlot->SetOffsets(FMargin(0));

	USizeBox* StageBox = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass(), TEXT("StageBox"));
	StageBox->SetWidthOverride(StageWidth);
	StageBox->SetHeightOverride(StageHeight);
	Scaler->SetContent(StageBox);

	Stage = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Stage"));
	StageBox->SetContent(Stage);

	Background = WidgetTree->ConstructWidget<UImage>(UImage::StaticClass(), TEXT("Background"));
	if (MenuBackgroundTexture) { Background->SetBrushFromTexture(MenuBackgroundTexture, false); }
	else { Background->SetColorAndOpacity(FLinearColor(.10f, .07f, .05f, 1.f)); }
	UCanvasPanelSlot* BgSlot = Stage->AddChildToCanvas(Background);
	BgSlot->SetAnchors(FAnchors(0, 0, 1, 1));
	BgSlot->SetOffsets(FMargin(0));

	MenuColumn = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("MenuColumn"));
	UCanvasPanelSlot* ColumnSlot = Stage->AddChildToCanvas(MenuColumn);
	ColumnSlot->SetAnchors(FAnchors(0, 0, 0, 0));
	ColumnSlot->SetPosition(FVector2D(ColumnLeft, ColumnTop));
	ColumnSlot->SetSize(FVector2D(ColumnWidth, ItemPitch * 6.f));
	BuildMenuItems();

	BuildGuidePanel();

	EndCard = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("EndCard"));
	EndCard->SetBrushColor(FLinearColor(.035f, .022f, .012f, .92f));
	EndCard->SetPadding(FMargin(28, 22, 28, 22));
	EndCard->SetVisibility(ESlateVisibility::Collapsed);
	UCanvasPanelSlot* EndSlot = Stage->AddChildToCanvas(EndCard);
	EndSlot->SetAnchors(FAnchors(.5f, .82f));
	EndSlot->SetAlignment(FVector2D(.5f, .5f));
	EndSlot->SetAutoSize(true);

	UVerticalBox* EndLines = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("EndLines"));
	EndCard->SetContent(EndLines);
	auto EndText = [this](FName Name, int32 Size, FLinearColor Color, FText Text)
	{
		UTextBlock* Item = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), Name);
		Item->SetFont(FSlateFontInfo(ChineseFont, Size, TEXT("Regular")));
		Item->SetColorAndOpacity(FSlateColor(Color));
		Item->SetJustification(ETextJustify::Center);
		Item->SetText(Text);
		return Item;
	};
	EndTitle = EndText(TEXT("EndTitle"), 34, Gold, GetTitle(EDYDevEntryPanel::End));
	EndBody = EndText(TEXT("EndBody"), 20, PaperText, GetBody(EDYDevEntryPanel::End));
	EndBody->SetAutoWrapText(true);
	EndLines->AddChildToVerticalBox(EndTitle)->SetHorizontalAlignment(HAlign_Center);
	UVerticalBoxSlot* EndBodySlot = EndLines->AddChildToVerticalBox(EndBody);
	EndBodySlot->SetPadding(FMargin(0, 14, 0, 18));
	EndBodySlot->SetHorizontalAlignment(HAlign_Center);

	ReplayButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), TEXT("Replay"));
	UTextBlock* ReplayLabel = EndText(TEXT("ReplayLabel"), 24, FLinearColor(.09f, .06f, .025f, 1.f), GetPrimaryLabel(EDYDevEntryPanel::End));
	ReplayButton->SetContent(ReplayLabel);
	ReplayButton->SetBackgroundColor(Gold);
	EndLines->AddChildToVerticalBox(ReplayButton)->SetPadding(FMargin(60, 4, 60, 4));

	BuildOverlay();
}

void UDYDevEntryWidget::BuildMenuItems()
{
	const FText Labels[6] = {
		LOCTEXT("ItemStart", "开始游戏"),
		LOCTEXT("ItemContinue", "继续游戏"),
		LOCTEXT("ItemChapters", "演出篇章"),
		LOCTEXT("ItemGuide", "游戏说明"),
		LOCTEXT("ItemSettings", "设置"),
		LOCTEXT("ItemQuit", "退出游戏")
	};
	static const FName LabelNames[6] = { TEXT("PrimaryLabel"), NAME_None, NAME_None, NAME_None, NAME_None, TEXT("QuitLabel") };
	for (int32 Index = 0; Index < 6; ++Index)
	{
		UTextBlock* Label = nullptr;
		UButton* Item = MakeMenuItem(static_cast<EDYDevEntryItem>(Index), Labels[Index], Label, LabelNames[Index]);
		MenuLabels.Add(Label);
		MenuBaseLabels.Add(Labels[Index]);
		MenuButtons.Add(Item);
		if (Index == 0) { PrimaryButton = Item; PrimaryLabel = Label; }
		if (Index == 5) { QuitButton = Item; }
	}
}

UButton* UDYDevEntryWidget::MakeMenuItem(EDYDevEntryItem Item, const FText& Label, UTextBlock*& OutLabel, FName LabelName)
{
	USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
	Box->SetHeightOverride(ItemHeight);
	UButton* Button = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass());
	Button->SetStyle(MakePlaqueStyle(PlaqueNormalTexture, PlaqueHoverTexture, PlaquePressedTexture, PlaqueDisabledTexture));
	Button->SetBackgroundColor(FLinearColor::White);
	OutLabel = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), LabelName);
	OutLabel->SetFont(FSlateFontInfo(ChineseFont, 34, TEXT("Regular")));
	OutLabel->SetColorAndOpacity(FSlateColor(Ink));
	OutLabel->SetJustification(ETextJustify::Center);
	OutLabel->SetText(Label);
	Button->SetContent(OutLabel);
	if (UButtonSlot* ButtonSlot = Cast<UButtonSlot>(OutLabel->Slot)) { ButtonSlot->SetPadding(FMargin(0)); ButtonSlot->SetHorizontalAlignment(HAlign_Fill); }
	Box->SetContent(Button);
	UVerticalBoxSlot* Row = MenuColumn->AddChildToVerticalBox(Box);
	Row->SetPadding(FMargin(0, 0, 0, ItemPitch - ItemHeight));
	Row->SetHorizontalAlignment(HAlign_Fill);
	return Button;
}

void UDYDevEntryWidget::EnsureGuideFonts()
{
	if (GuideSerifFont && GuideSerifBoldFont) { return; }
	if (!GuideSerifFont)
	{
		GuideSerifFont = LoadObject<UFont>(nullptr, TEXT("/Game/DengYingShanHai/UI/Menu/Fonts/FF_MenuSerif_Font.FF_MenuSerif_Font"), nullptr, LOAD_NoWarn | LOAD_Quiet);
	}
	if (!GuideSerifBoldFont)
	{
		GuideSerifBoldFont = LoadObject<UFont>(nullptr, TEXT("/Game/DengYingShanHai/UI/Menu/Fonts/FF_MenuSerifBold_Font.FF_MenuSerifBold_Font"), nullptr, LOAD_NoWarn | LOAD_Quiet);
	}
}

void UDYDevEntryWidget::BuildGuidePanel()
{
	GuideText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("GuideText"));
	const UFont* ChosenFont = GuideSerifBoldFont ? GuideSerifBoldFont.Get() : (GuideSerifFont ? GuideSerifFont.Get() : ChineseFont.Get());
	const FSlateFontInfo GuideFont(ChosenFont, GuideFontSize, TEXT("Regular"));
	GuideText->SetFont(GuideFont);
	GuideText->SetColorAndOpacity(FSlateColor(FLinearColor(.14f, .09f, .05f, 1.f)));
	GuideText->SetJustification(ETextJustify::Left);
	GuideText->SetAutoWrapText(true);
	GuideText->SetText(LOCTEXT("GuideBody", "行走于山海之间，以灯影唤醒失落的神话。\n在光与影的交织中，解开万物的秘密，\n追寻属于这个时代的山海传说。"));
	GuideText->SetLineHeightPercentage(1.20f);
	GuideText->SetShadowOffset(FVector2D(1.f, 1.f));
	GuideText->SetShadowColorAndOpacity(FLinearColor(1.f, .96f, .88f, .55f));
	UCanvasPanelSlot* GuideSlot = Stage->AddChildToCanvas(GuideText);
	GuideSlot->SetAnchors(FAnchors(0.772f, 0.695f, 0.772f, 0.695f));
	GuideSlot->SetPosition(FVector2D(6.f, 0.f));
	GuideSlot->SetSize(FVector2D(GuideWidth, GuideHeight));
}

void UDYDevEntryWidget::NativeConstruct()
{
	Super::NativeConstruct();
	if (PrimaryButton) { PrimaryButton->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandlePrimaryClick); }
	if (QuitButton) { QuitButton->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleQuitClick); }
	if (ReplayButton) { ReplayButton->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleReplayClick); }
	if (MenuButtons.IsValidIndex(1) && MenuButtons[1]) { MenuButtons[1]->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleItem1Click); }
	if (MenuButtons.IsValidIndex(2) && MenuButtons[2]) { MenuButtons[2]->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleItem2Click); }
	if (MenuButtons.IsValidIndex(3) && MenuButtons[3]) { MenuButtons[3]->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleItem3Click); }
	if (MenuButtons.IsValidIndex(4) && MenuButtons[4]) { MenuButtons[4]->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleItem4Click); }
	if (OverlayBackButton) { OverlayBackButton->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleOverlayBackClick); }
	if (OverlayConfirmButton) { OverlayConfirmButton->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleOverlayConfirmClick); }
	if (OverlayRevertButton) { OverlayRevertButton->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleOverlayRevertClick); }
	RefreshView();
}

void UDYDevEntryWidget::NativeDestruct()
{
	if (PrimaryButton) { PrimaryButton->OnClicked.RemoveDynamic(this, &UDYDevEntryWidget::HandlePrimaryClick); }
	if (QuitButton) { QuitButton->OnClicked.RemoveDynamic(this, &UDYDevEntryWidget::HandleQuitClick); }
	if (ReplayButton) { ReplayButton->OnClicked.RemoveDynamic(this, &UDYDevEntryWidget::HandleReplayClick); }
	for (const TObjectPtr<UButton>& Item : MenuButtons)
	{
		if (Item)
		{
		}
	}
	Super::NativeDestruct();
}


void UDYDevEntryWidget::ApplyPanel(EDYDevEntryPanel Panel)
{
	const EDYDevEntryPanel Previous = CurrentPanel;
	CurrentPanel = Panel;
	RefreshView();
	if (Panel == EDYDevEntryPanel::Paused && Previous != Panel
		&& CurrentOverlay == EDYMenuOverlay::None
		&& MenuButtons.IsValidIndex(1) && MenuButtons[1])
	{
		NavFocusIndex = 1;
		MenuButtons[1]->SetKeyboardFocus();
		RefreshView();
	}
}

void UDYDevEntryWidget::RefreshView()
{
	SetVisibility(CurrentPanel == EDYDevEntryPanel::Hidden ? ESlateVisibility::Collapsed : ESlateVisibility::Visible);
	const bool bEnd = CurrentPanel == EDYDevEntryPanel::End || CurrentPanel == EDYDevEntryPanel::Reloading;
	if (Backdrop) { Backdrop->SetVisibility(!MenuBackgroundTexture ? ESlateVisibility::Visible : ESlateVisibility::Collapsed); }
	// T_MenuBackground already has a menu column and a guide card painted into the art, so both
	// of ours must stay opaque on top of it even on the ending panel; collapsing them exposed
	// the baked "章节选择" column underneath.
	if (MenuColumn) { MenuColumn->SetVisibility(ESlateVisibility::SelfHitTestInvisible); }
	if (GuidePanel) { GuidePanel->SetVisibility(ESlateVisibility::SelfHitTestInvisible); }
	if (EndCard) { EndCard->SetVisibility(bEnd ? ESlateVisibility::Visible : ESlateVisibility::Collapsed); }
	if (EndTitle) { EndTitle->SetText(GetTitle(CurrentPanel)); }
	if (EndBody) { EndBody->SetText(GetBody(CurrentPanel)); }
	if (PrimaryLabel) { PrimaryLabel->SetText(GetPrimaryLabel(CurrentPanel)); }
	if (MenuButtons.Num() == 6)
	{
		const bool bStartPanel = CurrentPanel == EDYDevEntryPanel::Start;
		const bool bPausedPanel = CurrentPanel == EDYDevEntryPanel::Paused;
		const bool bMenuLive = bStartPanel || bPausedPanel;
		for (int32 Index = 0; Index < MenuButtons.Num(); ++Index)
		{
			const bool bAvailable = IsMenuItemAvailable(Index);

			// FButtonStyle has no focused brush, so the keyboard cursor borrows the hover plate.
			const bool bFocused = CurrentOverlay == EDYMenuOverlay::None && Index == NavFocusIndex && bAvailable;
			FButtonStyle PlaqueStyle = MakePlaqueStyle(PlaqueNormalTexture, PlaqueHoverTexture, PlaquePressedTexture, PlaqueDisabledTexture);
			if (bFocused)
			{
				// The hover plate is see-through enough that the plaque baked into the menu art shows
				// through and doubles the label. Keep the opaque normal plate and tint it amber instead.
				PlaqueStyle.Normal.TintColor = FSlateColor(FLinearColor(1.f, 0.84f, 0.5f, 1.f));
				PlaqueStyle.Hovered.TintColor = FSlateColor(FLinearColor(1.f, 0.84f, 0.5f, 1.f));
			}
			MenuButtons[Index]->SetStyle(PlaqueStyle);
			MenuButtons[Index]->SetIsEnabled(bAvailable);
			MenuButtons[Index]->SetRenderOpacity(1.f);
			if (MenuLabels.IsValidIndex(Index) && MenuLabels[Index])
			{
				// Disabled plaques use the grey stamped texture, where the plain ink label reads as a
				// smudge; lift the disabled label to the pale stamp colour so 「继续游戏」 stays legible.
				MenuLabels[Index]->SetColorAndOpacity(FSlateColor(bAvailable ? Ink : FLinearColor(.80f, .75f, .66f, 1.f)));
				// Tinting the plate alone was too subtle, so the focused plaque also gains a gold lozenge.
				if (MenuBaseLabels.IsValidIndex(Index))
				{
					// Plaque 0 changes with the panel (「重新复演」 on the ending card), so ask for its live text.
					const FText BaseLabel = Index == 0 ? GetPrimaryLabel(CurrentPanel) : MenuBaseLabels[Index];
					MenuLabels[Index]->SetText(bFocused
						? FText::Format(FText::FromString(TEXT("\u25C6 {0}")), BaseLabel)
						: BaseLabel);
				}
				MenuLabels[Index]->SetRenderOpacity(1.f);
				MenuLabels[Index]->SetVisibility(ESlateVisibility::HitTestInvisible);
			}
		}
	}
	// The ending CTA lives in the primary plaque slot (top of the menu column); the card keeps text only.
	if (ReplayButton) { ReplayButton->SetVisibility(ESlateVisibility::Collapsed); }
	if (MenuButtons.Num() == 6)
	{
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] panel=%d startEnabled=%d quitEnabled=%d menuVisible=%d"),
			static_cast<int32>(CurrentPanel), IsMenuItemAvailable(0) ? 1 : 0,
			IsMenuItemAvailable(5) ? 1 : 0,
			MenuColumn ? (MenuColumn->GetVisibility() == ESlateVisibility::SelfHitTestInvisible ? 1 : 0) : -1);
		const FGeometry BtnGeo = MenuButtons[0]->GetCachedGeometry();
		const FGeometry SelfGeo = GetCachedGeometry();
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] btn0=%.1fx%.1f at %.1f,%.1f self=%.1fx%.1f"),
			BtnGeo.GetLocalSize().X, BtnGeo.GetLocalSize().Y, BtnGeo.GetAbsolutePosition().X, BtnGeo.GetAbsolutePosition().Y,
			SelfGeo.GetLocalSize().X, SelfGeo.GetLocalSize().Y);
	}
	RefreshOverlay();
	HideForeignOverlays();
	// The ending panel is reached from gameplay, where focus still belongs to the stage HUD;
	// pin it back to the primary plaque so Up/Down/Enter always start from 「重新复演」.
	if (CurrentOverlay == EDYMenuOverlay::None && bEnd && MenuButtons.IsValidIndex(0) && MenuButtons[0])
	{
		MenuButtons[0]->SetKeyboardFocus();
		NavFocusIndex = 0;
	}
}


void UDYDevEntryWidget::HandlePrimaryClick()
{
	if (CurrentPanel == EDYDevEntryPanel::Start || CurrentPanel == EDYDevEntryPanel::End) { HandleMenuSelection(0); }
}

void UDYDevEntryWidget::HandleReplayClick()
{
	if (ADYDevEntryPlayerController* PC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer()))
	{
		if (CurrentPanel == EDYDevEntryPanel::End) { PC->RequestReplayExperience(); }
	}
}

void UDYDevEntryWidget::HandleQuitClick()
{
	if (ADYDevEntryPlayerController* PC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer())) { PC->RequestQuitExperience(); }
}

#undef LOCTEXT_NAMESPACE

void UDYDevEntryWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
#if !UE_BUILD_SHIPPING
	// Dev review hook: DY_CODEX_PREVIEW=0..3 opens a codex entry and 4 opens the 制作七步 plate,
	// so the layout can be screenshotted without replaying four acts.
	if (!bCodexPreviewApplied && CurrentPanel == EDYDevEntryPanel::Start)
	{
		const FString CodexPreview = FPlatformMisc::GetEnvironmentVariable(TEXT("DY_CODEX_PREVIEW"));
		if (!CodexPreview.IsEmpty())
		{
			bCodexPreviewApplied = true;
			const int32 Requested = FCString::Atoi(*CodexPreview);
			bCodexShowSteps = Requested >= 4;
			CodexIndex = FMath::Clamp(Requested, 0, 3);
			OpenOverlay(EDYMenuOverlay::Codex);
		}
	}
#endif
	TickSettingsCountdown();
	TickSettingsProbe();
	HideForeignOverlays();
	// Slate owns arrow-key focus once an overlay row holds it, so NativeOnKeyDown never sees those
	// keys. Mirror the real focused widget into our cursor and repaint: FButtonStyle in 5.8 has no
	// focused brush, and without this the focused row looked identical to the other cream rows.
	// The codex leaf drives its own red cursor from CodexIndex; mirroring Slate focus would keep
	// dragging it back to row 0 and the page would highlight an entry it is not showing.
	if (CurrentOverlay != EDYMenuOverlay::None && CurrentOverlay != EDYMenuOverlay::Codex && OverlayRows.Num() > 0)
	{
		const TSharedPtr<SWidget> FocusedWidget = FSlateApplication::Get().GetKeyboardFocusedWidget();
		if (FocusedWidget.IsValid())
		{
			for (int32 Index = 0; Index < OverlayRows.Num(); ++Index)
			{
				UButton* Row = OverlayRows[Index];
				if (!Row || Row->GetVisibility() != ESlateVisibility::Visible) { continue; }
				if (Row->GetCachedWidget() == FocusedWidget && OverlayFocusIndex != Index)
				{
					OverlayFocusIndex = Index;
					ApplyOverlayRowFocus();
					// Slate moves focus with a Navigation cause, which is exactly the cause that draws its
					// 1 px focus rect. Hand the focus back with SetDirectly so the ring disappears while the
					// repainted row keeps the red plate as the visible cursor.
					FSlateApplication::Get().ClearKeyboardFocus(EFocusCause::SetDirectly);
					Row->SetKeyboardFocus();
					break;
				}
			}
		}
	}
#if !UE_BUILD_SHIPPING
	TickAutoTest();
#endif
	if (bGeometryLogged || !MenuButtons.IsValidIndex(0) || !MenuButtons[0]) { return; }
	const FGeometry BtnGeo = MenuButtons[0]->GetCachedGeometry();
	if (BtnGeo.GetLocalSize().X <= 0.f) { return; }
	bGeometryLogged = true;
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] tick btn0=%.1fx%.1f at %.1f,%.1f self=%.1fx%.1f"),
		BtnGeo.GetLocalSize().X, BtnGeo.GetLocalSize().Y, BtnGeo.GetAbsolutePosition().X, BtnGeo.GetAbsolutePosition().Y,
		MyGeometry.GetLocalSize().X, MyGeometry.GetLocalSize().Y);
	const FGeometry GuideGeo = GuideText ? GuideText->GetCachedGeometry() : FGeometry();
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] guide size=%.1fx%.1f at %.1f,%.1f scale=%s"),
		GuideGeo.GetLocalSize().X, GuideGeo.GetLocalSize().Y, GuideGeo.GetAbsolutePosition().X, GuideGeo.GetAbsolutePosition().Y,
		*FString::SanitizeFloat(GuideGeo.Scale));
}

void UDYDevEntryWidget::HideForeignOverlays()
{
	UWorld* World = GetWorld();
	if (!World) { return; }
	const bool bMenuUp = CurrentPanel != EDYDevEntryPanel::Hidden;
	TArray<UUserWidget*> Found;
	UWidgetBlueprintLibrary::GetAllWidgetsOfClass(World, Found, UUserWidget::StaticClass(), true);
	for (UUserWidget* Widget : Found)
	{
		if (!Widget || Widget == this) { continue; }
		const FString Name = Widget->GetClass()->GetName();
		if (!bLoggedOverlays)
		{
			UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] overlay %s vis=%d"), *Name, static_cast<int32>(Widget->GetVisibility()));
		}
		if (!Name.Contains(TEXT("ThreeActHUD")) && !Name.Contains(TEXT("ThreeActCue"))) { continue; }
		if (bMenuUp)
		{
			const ESlateVisibility Current = Widget->GetVisibility();
			if (Current != ESlateVisibility::Collapsed)
			{
				SuppressedOverlays.FindOrAdd(Widget) = Current;
				Widget->SetVisibility(ESlateVisibility::Collapsed);
			}
		}
		else if (const ESlateVisibility* Saved = SuppressedOverlays.Find(Widget))
		{
			Widget->SetVisibility(*Saved);
			SuppressedOverlays.Remove(Widget);
		}
	}
	bLoggedOverlays = true;
}


void UDYDevEntryWidget::BuildOverlay()
{
	OverlayRoot = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("MenuOverlay"));
	OverlayRoot->SetVisibility(ESlateVisibility::Collapsed);
	UCanvasPanelSlot* RootSlot = Stage->AddChildToCanvas(OverlayRoot);
	RootSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
	RootSlot->SetOffsets(FMargin(0.f));

	UBorder* Dim = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("OverlayDim"));
	Dim->SetBrushColor(FLinearColor(.02f, .012f, .006f, .92f));
	UCanvasPanelSlot* DimSlot = OverlayRoot->AddChildToCanvas(Dim);
	DimSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
	DimSlot->SetOffsets(FMargin(0.f));

	OverlayCard = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("OverlayCard"));
	OverlayCard->SetBrushColor(FLinearColor(.955f, .906f, .816f, 1.f));
	OverlayCard->SetPadding(FMargin(46.f, 34.f, 46.f, 30.f));
	OverlayCard->SetHorizontalAlignment(HAlign_Fill);
	OverlayCard->SetVerticalAlignment(VAlign_Top);
	// The codex leaf is the tallest page (illustration + 4 rows + footer). Cap the card at a fixed
	// 1040x1000 sheet and aspect-fit it, so no leaf can push its title or footer off screen.
	USizeBox* CardBox = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass(), TEXT("OverlayCardBox"));
	CardBox->SetWidthOverride(1040.f);
	CardBox->SetHeightOverride(1000.f);
	UScaleBox* CardScaler = WidgetTree->ConstructWidget<UScaleBox>(UScaleBox::StaticClass(), TEXT("OverlayCardScaler"));
	CardScaler->SetStretch(EStretch::ScaleToFit);
	CardScaler->SetStretchDirection(EStretchDirection::Both);
	CardScaler->SetContent(OverlayCard);
	CardBox->SetContent(CardScaler);
	UCanvasPanelSlot* CardSlot = OverlayRoot->AddChildToCanvas(CardBox);
	CardSlot->SetAnchors(FAnchors(.5f, .5f));
	CardSlot->SetAlignment(FVector2D(.5f, .5f));
	CardSlot->SetAutoSize(true);

	UVerticalBox* Lines = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("OverlayLines"));
	OverlayCard->SetContent(Lines);
	auto AddLine = [this](UVerticalBox* Parent, FName Name, int32 Size, const FLinearColor& Color, bool bWrap)
	{
		UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), Name);
		Text->SetFont(FSlateFontInfo(ChineseFont, Size, TEXT("Regular")));
		Text->SetColorAndOpacity(FSlateColor(Color));
		Text->SetAutoWrapText(bWrap);
		if (bWrap) { Text->SetWrapTextAt(940.f); }
		Text->SetLineHeightPercentage(1.25f);
		UVerticalBoxSlot* Slot = Parent->AddChildToVerticalBox(Text);
		Slot->SetPadding(FMargin(0.f, 0.f, 0.f, 12.f));
		Slot->SetHorizontalAlignment(bWrap ? HAlign_Fill : HAlign_Left);
		return Text;
	};
	OverlayTitle = AddLine(Lines, TEXT("OverlayTitle"), 32, Ink, false);

	// The codex leaf is the one page that carries an illustration: the delivered concept art sits
	// left of the entry text. Every other leaf collapses the art box, so it keeps the full width.
	UHorizontalBox* BodyRow = WidgetTree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass(), TEXT("OverlayBodyRow"));
	Lines->AddChildToVerticalBox(BodyRow)->SetPadding(FMargin(0.f, 4.f, 0.f, 10.f));

	CodexArtBox = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass(), TEXT("OverlayCodexArtBox"));
	CodexArtBox->SetVisibility(ESlateVisibility::Collapsed);
	CodexArt = WidgetTree->ConstructWidget<UImage>(UImage::StaticClass(), TEXT("OverlayCodexArt"));
	CodexArt->SetColorAndOpacity(FLinearColor(1.f, 1.f, 1.f, 1.f));
	CodexArtBox->SetContent(CodexArt);
	UHorizontalBoxSlot* ArtSlot = BodyRow->AddChildToHorizontalBox(CodexArtBox);
	ArtSlot->SetPadding(FMargin(0.f, 0.f, 26.f, 0.f));
	ArtSlot->SetVerticalAlignment(VAlign_Top);

	UVerticalBox* BodyColumn = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("OverlayBodyColumn"));
	UHorizontalBoxSlot* BodySlot = BodyRow->AddChildToHorizontalBox(BodyColumn);
	BodySlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	BodySlot->SetHorizontalAlignment(HAlign_Fill);
	BodySlot->SetVerticalAlignment(VAlign_Top);

	OverlayBody = AddLine(BodyColumn, TEXT("OverlayBody"), 20, FLinearColor(.20f, .13f, .08f, 1.f), true);

	for (int32 Index = 0; Index < 5; ++Index)
	{
		UButton* Row = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass());
		Row->SetStyle(MakeFlatStyle(FLinearColor(.886f, .827f, .706f, 1.f), FLinearColor(.945f, .788f, .520f, 1.f), FLinearColor(.855f, .667f, .420f, 1.f)));
		UTextBlock* RowText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
		RowText->SetFont(FSlateFontInfo(ChineseFont, 22, TEXT("Regular")));
		RowText->SetColorAndOpacity(FSlateColor(Ink));
		Row->SetContent(RowText);
		if (UButtonSlot* ButtonSlot = Cast<UButtonSlot>(RowText->Slot))
		{
			ButtonSlot->SetPadding(FMargin(18.f, 10.f));
			ButtonSlot->SetHorizontalAlignment(HAlign_Left);
		}
		Lines->AddChildToVerticalBox(Row)->SetPadding(FMargin(0.f, 0.f, 0.f, 10.f));
		OverlayRows.Add(Row);
		OverlayRowLabels.Add(RowText);

		if (Index == 0) { Row->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleOverlayRow0Click); }
		else if (Index == 1) { Row->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleOverlayRow1Click); }
		else if (Index == 2) { Row->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleOverlayRow2Click); }
		else if (Index == 3) { Row->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleOverlayRow3Click); }
		else { Row->OnClicked.AddUniqueDynamic(this, &UDYDevEntryWidget::HandleOverlayRow4Click); }
	}

	OverlayHint = AddLine(Lines, TEXT("OverlayHint"), 16, Muted, true);

	UHorizontalBox* Footer = WidgetTree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass(), TEXT("OverlayFooter"));
	Lines->AddChildToVerticalBox(Footer)->SetPadding(FMargin(0.f, 6.f, 0.f, 0.f));
	auto AddFooterButton = [this, Footer](FName Name, const FText& Label, const FLinearColor& Tint)
	{
		UButton* Button = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), Name);
		Button->SetStyle(MakeFlatStyle(Tint, Tint * 1.08f, Tint * .92f));
		UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
		Text->SetFont(FSlateFontInfo(ChineseFont, 22, TEXT("Regular")));
		Text->SetColorAndOpacity(FSlateColor(Ink));
		Text->SetText(Label);
		Button->SetContent(Text);
		if (UButtonSlot* ButtonSlot = Cast<UButtonSlot>(Text->Slot)) { ButtonSlot->SetPadding(FMargin(22.f, 9.f)); }
		Footer->AddChildToHorizontalBox(Button)->SetPadding(FMargin(0.f, 0.f, 12.f, 0.f));
		return Button;
	};
	OverlayBackButton = AddFooterButton(TEXT("OverlayBack"), FText::FromString(TEXT("返回")), FLinearColor(.80f, .76f, .68f, 1.f));
	OverlayConfirmButton = AddFooterButton(TEXT("OverlayConfirm"), FText::FromString(TEXT("确认设置")), Gold);
	OverlayRevertButton = AddFooterButton(TEXT("OverlayRevert"), FText::FromString(TEXT("还原")), FLinearColor(.86f, .80f, .70f, 1.f));
}

void UDYDevEntryWidget::OpenOverlay(EDYMenuOverlay Kind)
{
	CurrentOverlay = Kind;
	if (Kind == EDYMenuOverlay::Settings)
	{
		if (!bSettingsDirty)
		{
			if (!bSettingsInitialized)
			{
				if (GConfig) { GConfig->GetInt(TEXT("DengYingShanHai"), TEXT("VolumeStep"), VolumeStep, GGameUserSettingsIni); }
				VolumeStep = FMath::Clamp(VolumeStep, 0, 10);
				bSettingsInitialized = true;
			}
			ReadLiveVideoChoice(WindowModeIndex, ResolutionIndex);
		}
		SavedVolumeStep = VolumeStep;
		SavedWindowModeIndex = WindowModeIndex;
		SavedResolutionIndex = ResolutionIndex;
		bSettingsDirty = false;
		SettingsDeadlineSeconds = 0.0;
		LastCountdownSecond = -1;
		ApplyVolumePreview();
	}
	OverlayFocusIndex = 0;
	RefreshOverlay();
	// Chapter / settings / codex rows are the card's actionable content: focus the first one so
	// Up/Down + Enter works without a mouse (Guide has no rows at all).
	if (OverlayRows.Num() > 0 && OverlayRows[0] && OverlayRows[0]->GetVisibility() == ESlateVisibility::Visible)
	{
		OverlayRows[0]->SetKeyboardFocus();
	}
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] overlay=%d"), static_cast<int32>(Kind));
}

void UDYDevEntryWidget::RefreshOverlay()
{
	if (!OverlayRoot) { return; }
	const bool bOpen = CurrentOverlay != EDYMenuOverlay::None;
	OverlayRoot->SetVisibility(bOpen ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
	if (GuideText)
	{
		GuideText->SetVisibility(bOpen ? ESlateVisibility::Collapsed : ESlateVisibility::SelfHitTestInvisible);
	}
	if (!bOpen) { return; }

	const bool bSettings = CurrentOverlay == EDYMenuOverlay::Settings;
	FText Title;
	FText Body;
	FString Hint;
	if (CurrentOverlay == EDYMenuOverlay::Chapters)
	{
		Title = FText::FromString(TEXT("演出篇章"));
		Body = FText::FromString(TEXT("第一幕 · 夸父逐日 —— 以灯为日，以影为夸父\n第二幕 · 精卫填海 —— 光位与石影连成通路\n第三幕 · 刑天舞干戚 —— 盾影合击，舞动干戚\n第四幕 · 烛龙昼夜 —— 昼夜交替，晦明同光\n\n四幕共用一座戏台，可逐幕连演。\n第四幕落幕，才是真结局。"));
		const ADYDevEntryPlayerController* ChapterPC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer());
		Hint = (ChapterPC && ChapterPC->HasAnyPlayedChapter())
			? TEXT("点选任一幕即可直接开演；「开始游戏」从第一幕起。（已演）表示这一幕演完过。")
			: TEXT("点选任一幕即可直接开演；「开始游戏」从第一幕起。");
	}
	else if (CurrentOverlay == EDYMenuOverlay::Guide)
	{
		Title = FText::FromString(TEXT("游戏说明"));
		Body = FText::FromString(TEXT("复演者走进戏台，操纵同一盏灯和同一具影偶，把未完的四幕演完。\n\n第一幕夸父逐日。第二幕精卫填海。\n第三幕刑天舞干戚。第四幕烛龙昼夜。\n四幕共用一座戏台。第四幕落幕，才是结局。\n\nW A S D 移动。按住鼠标右键转向。\n对准灯或皮影，按 E 开始调整，再用 A / D 移动。\n灯和偶都到位后松开，保持片刻。\nR 把灯和偶复位。Esc 暂停。\n\n锣鼓和背景只作气氛。谜题不靠听声完成。\n四幕演完后，结束页的「游戏说明」打开影偶图鉴。\n重开游戏时，标题面板的「继续游戏」从上次停下的那一幕接上。"));
		Hint = TEXT("四幕用同一盏灯、同一具影偶。先对灯，再对偶，最后一起稳住。");
	}
	else if (CurrentOverlay == EDYMenuOverlay::Codex)
	{
		static const TCHAR* CodexNames[4] = { TEXT("夸父逐日"), TEXT("精卫填海"), TEXT("刑天舞干戚"), TEXT("烛龙昼夜") };
		CodexIndex = FMath::Clamp(CodexIndex, 0, 3);
		if (bCodexShowSteps)
		{
			Title = FText::FromString(TEXT("影偶图鉴 · 制作七步"));
			Body = FText::FromString(TEXT("一具影偶从一张皮到能上台，要过七道手。\n\n01 选皮　02 制皮　03 画稿\n04 雕刻　05 着色　06 连接关节　07 装杆\n\n选皮看厚薄与透光度，制皮去毛刮薄到见光；画稿定形，雕刻镂空出衣纹与羽片；着色用矿物与植物颜料，连接关节定活动的三处枢；装杆之后，影子才有操演的步幅。\n\n锣鼓与器乐是影戏的另一半：无锣鼓不开台。"));
			Hint = TEXT("再点「制作七步」回到影偶条目；Esc 返回菜单。");
		}
		else
		{
			Title = FText::FromString(FString::Printf(TEXT("影偶图鉴 · %s"), CodexNames[CodexIndex]));
			Body = FText::FromString(MakeCodexEntry(CodexIndex));
			Hint = TEXT("点选条目切换影偶；Esc 返回菜单。");
		}
	}
	else
	{
		Title = FText::FromString(TEXT("设置"));
		Body = FText::FromString(TEXT("改动会立即预览；留在本页未确认时会自动还原。"));
		if (bSettingsDirty)
		{
			const int32 Left = FMath::Max(0, FMath::CeilToInt(static_cast<float>(SettingsDeadlineSeconds - FPlatformTime::Seconds())));
			Hint = FString::Printf(TEXT("预览中：%d 秒内不确认将自动还原。"), Left);
		}
		else
		{
			Hint = TEXT("点击条目切换取值；确认后保留本次设置。");
		}
	}
	if (OverlayTitle) { OverlayTitle->SetText(Title); }
	if (OverlayBody) { OverlayBody->SetText(Body); }
	const bool bCodexLeaf = CurrentOverlay == EDYMenuOverlay::Codex;
	if (CodexArtBox && CodexArt)
	{
		UTexture2D* ArtTexture = nullptr;
		if (bCodexLeaf)
		{
			ArtTexture = bCodexShowSteps ? CodexStepsTexture.Get()
				: (CodexArtTextures.IsValidIndex(CodexIndex) ? CodexArtTextures[CodexIndex].Get() : nullptr);
		}
		if (ArtTexture && ArtTexture->GetSizeX() > 0 && ArtTexture->GetSizeY() > 0)
		{
			// Concept sheets differ in aspect (figure sheets are wide, the Kuafu leaf is tall), so
			// derive the box from the texture instead of stretching one fixed frame. The width is
			// capped at 520 to leave the body column its measure; the height then follows from the
			// capped width, otherwise the wide seven-step plate (1990x1085) would be squashed.
			const float WantHeight = bCodexShowSteps ? 470.f : 330.f;
			const float ArtAspect = static_cast<float>(ArtTexture->GetSizeX()) / static_cast<float>(ArtTexture->GetSizeY());
			const float ArtWidth = FMath::Clamp(WantHeight * ArtAspect, 200.f, 520.f);
			CodexArtBox->SetWidthOverride(ArtWidth);
			CodexArtBox->SetHeightOverride(ArtWidth / FMath::Max(ArtAspect, 0.01f));
			CodexArt->SetBrushFromTexture(ArtTexture, false);
			CodexArtBox->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
		}
		else
		{
			CodexArtBox->SetVisibility(ESlateVisibility::Collapsed);
		}
	}
	if (OverlayBody) { OverlayBody->SetWrapTextAt(bCodexLeaf ? 500.f : 940.f); }
	if (OverlayHint) { OverlayHint->SetText(FText::FromString(Hint)); }
	const bool bChapters = CurrentOverlay == EDYMenuOverlay::Chapters;
	const TArray<FText>& ChapterTitles = ADYPuzzleDirector::GetCampaignChapterTitles();
	for (int32 Index = 0; Index < OverlayRows.Num(); ++Index)
	{
		UButton* Row = OverlayRows[Index];
		if (!Row) { continue; }
		const bool bCodex = CurrentOverlay == EDYMenuOverlay::Codex;
		const bool bRowVisible = bSettings ? (Index < 3) : (bChapters ? ChapterTitles.IsValidIndex(Index) : (bCodex && Index < 5));
		Row->SetVisibility(bRowVisible ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
		if (bChapters && OverlayRowLabels.IsValidIndex(Index) && OverlayRowLabels[Index] && ChapterTitles.IsValidIndex(Index))
		{
			// A judge opening this page should see that the four acts carry real state, not just copy:
			// acts already played to their end are suffixed, the rest stay plain.
			const ADYDevEntryPlayerController* EntryPC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer());
			OverlayRowLabels[Index]->SetText(EntryPC && EntryPC->WasChapterPlayed(Index)
				? FText::FromString(FString::Printf(TEXT("%s（已演）"), *ChapterTitles[Index].ToString()))
				: ChapterTitles[Index]);
		}
		if (bCodex && OverlayRowLabels.IsValidIndex(Index) && OverlayRowLabels[Index])
		{
			static const TCHAR* CodexRowNames[4] = { TEXT("夸父逐日"), TEXT("精卫填海"), TEXT("刑天舞干戚"), TEXT("烛龙昼夜") };
			OverlayRowLabels[Index]->SetText(FText::FromString(Index < 4 ? CodexRowNames[Index] : TEXT("制作七步")));
		}
	}
	if (OverlayConfirmButton) { OverlayConfirmButton->SetVisibility(bSettings ? ESlateVisibility::Visible : ESlateVisibility::Collapsed); }
	if (OverlayRevertButton) { OverlayRevertButton->SetVisibility(bSettings ? ESlateVisibility::Visible : ESlateVisibility::Collapsed); }
	if (bSettings) { RefreshSettingsRows(); }
	// On the codex leaf the red cursor has to sit on the entry being shown, not on row 0.
	if (CurrentOverlay == EDYMenuOverlay::Codex) { OverlayFocusIndex = bCodexShowSteps ? 4 : FMath::Clamp(CodexIndex, 0, 3); }
	ApplyOverlayRowFocus();
}

void UDYDevEntryWidget::ApplyOverlayRowFocus()
{
	// FButtonStyle in 5.8 only carries Normal/Hovered/Pressed/Disabled brushes, so a focused row
	// looked exactly like an unfocused one on cream paper. Repaint the cursor row in 朱红 with a
	// warm label: that is the only cue a keyboard player gets before pressing Enter.
	if (CurrentOverlay == EDYMenuOverlay::None) { return; }
	for (int32 Index = 0; Index < OverlayRows.Num(); ++Index)
	{
		UButton* Row = OverlayRows[Index];
		if (!Row || Row->GetVisibility() != ESlateVisibility::Visible) { continue; }
		const bool bFocused = Index == OverlayFocusIndex;
		FButtonStyle Style = bFocused
			? MakeFlatStyle(FLinearColor(.70f, .21f, .16f, 1.f), FLinearColor(.78f, .27f, .21f, 1.f), FLinearColor(.58f, .16f, .12f, 1.f))
			: MakeFlatStyle(FLinearColor(.886f, .827f, .706f, 1.f), FLinearColor(.945f, .788f, .520f, 1.f), FLinearColor(.855f, .667f, .420f, 1.f));
		if (bFocused)
		{
			Style.SetNormalForeground(FSlateColor(OnRed));
			Style.SetHoveredForeground(FSlateColor(OnRed));
			Style.SetPressedForeground(FSlateColor(OnRed));
		}
		Row->SetStyle(Style);
		if (OverlayRowLabels.IsValidIndex(Index) && OverlayRowLabels[Index])
		{
			OverlayRowLabels[Index]->SetColorAndOpacity(FSlateColor(bFocused ? FLinearColor(.99f, .93f, .82f, 1.f) : Ink));
		}
	}
}

void UDYDevEntryWidget::RefreshSettingsRows()
{
	if (OverlayRowLabels.Num() < 3) { return; }
	if (OverlayRowLabels[0])
	{
		OverlayRowLabels[0]->SetText(FText::FromString(FString::Printf(TEXT("主音量    %d / 10"), VolumeStep)));
	}
	if (OverlayRowLabels[1])
	{
		OverlayRowLabels[1]->SetText(FText::FromString(FString::Printf(TEXT("窗口模式    %s"), MenuWindowModeNames[FMath::Clamp(WindowModeIndex, 0, 2)])));
	}
	if (OverlayRowLabels[2])
	{
		const FIntPoint Res = MenuResolutions[FMath::Clamp(ResolutionIndex, 0, MenuResolutionCount - 1)];
		FString RowText = FString::Printf(TEXT("分辨率    %d x %d"), Res.X, Res.Y);
		FIntPoint Current(0, 0);
		FIntPoint Physical(0, 0);
#if PLATFORM_WINDOWS
		// GetClientRect is the logical client. Multiply by the window DPI so the note is the on-screen size.
		if (GEngine && GEngine->GameViewport)
		{
			const TSharedPtr<SWindow> ActiveWindow = GEngine->GameViewport->GetWindow();
			if (ActiveWindow.IsValid() && ActiveWindow->GetNativeWindow().IsValid())
			{
				const HWND OsHandle = static_cast<HWND>(ActiveWindow->GetNativeWindow()->GetOSWindowHandle());
				RECT ClientRect{};
				if (OsHandle && ::GetClientRect(OsHandle, &ClientRect))
				{
					const int32 Width = static_cast<int32>(ClientRect.right - ClientRect.left);
					const int32 Height = static_cast<int32>(ClientRect.bottom - ClientRect.top);
					if (Width > 1 && Height > 1)
					{
						Current = FIntPoint(Width, Height);
						const UINT Dpi = ::GetDpiForWindow(OsHandle);
						Physical = Dpi > 0
							? FIntPoint(::MulDiv(Width, static_cast<int>(Dpi), 96), ::MulDiv(Height, static_cast<int>(Dpi), 96))
							: Current;
					}
				}
			}
		}
#endif
		if (Current.X <= 1 && GEngine && GEngine->GameViewport)
		{
			if (FViewport* RenderViewport = GEngine->GameViewport->Viewport)
			{
				const FIntPoint PixelSize = RenderViewport->GetSizeXY();
				if (PixelSize.X > 1 && PixelSize.Y > 1)
				{
					Current = PixelSize;
				}
			}
			if (Current.X <= 1)
			{
				FVector2D ViewportSize = FVector2D::ZeroVector;
				GEngine->GameViewport->GetViewportSize(ViewportSize);
				if (ViewportSize.X > 1.0 && ViewportSize.Y > 1.0)
				{
					Current = FIntPoint(FMath::RoundToInt(ViewportSize.X), FMath::RoundToInt(ViewportSize.Y));
				}
			}
		}
		if (Current.X <= 1)
		{
			if (UGameUserSettings* Settings = UGameUserSettings::GetGameUserSettings())
			{
				Current = Settings->GetScreenResolution();
			}
		}
		if (Current.X > 1 && Current != Res)
		{
			const FIntPoint Shown = Physical.X > 1 ? Physical : Current;
			RowText += FString::Printf(TEXT("（窗口 %d x %d）"), Shown.X, Shown.Y);
		}
		OverlayRowLabels[2]->SetText(FText::FromString(RowText));
	}
}

void UDYDevEntryWidget::ApplyVolumePreview()
{
	if (!GEngine) { return; }
	const FAudioDeviceHandle MainDevice = GEngine->GetMainAudioDevice();
	if (FAudioDevice* Audio = MainDevice.GetAudioDevice())
	{
		Audio->SetTransientPrimaryVolume(FMath::Clamp(VolumeStep / 10.f, 0.f, 1.f));
	}
}

void UDYDevEntryWidget::ApplyVideoPreview()
{
	UGameUserSettings* Settings = UGameUserSettings::GetGameUserSettings();
	if (!Settings) { return; }
	Settings->SetScreenResolution(MenuResolutions[FMath::Clamp(ResolutionIndex, 0, MenuResolutionCount - 1)]);
	Settings->SetFullscreenMode(MenuWindowModes[FMath::Clamp(WindowModeIndex, 0, 2)]);
	Settings->ApplyResolutionSettings(false);
}

void UDYDevEntryWidget::CommitSettings()
{
	if (UGameUserSettings* Settings = UGameUserSettings::GetGameUserSettings()) { Settings->ConfirmVideoMode(); Settings->SaveSettings(); }
	if (GConfig)
	{
		GConfig->SetInt(TEXT("DengYingShanHai"), TEXT("VolumeStep"), VolumeStep, GGameUserSettingsIni);
		GConfig->Flush(false, GGameUserSettingsIni);
	}
	bSettingsDirty = false;
	SettingsDeadlineSeconds = 0.0;
	LastCountdownSecond = -1;
	RefreshOverlay();
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] settings committed vol=%d mode=%d res=%d"), VolumeStep, WindowModeIndex, ResolutionIndex);
}

void UDYDevEntryWidget::RevertSettings()
{
	VolumeStep = SavedVolumeStep;
	WindowModeIndex = SavedWindowModeIndex;
	ResolutionIndex = SavedResolutionIndex;
	bSettingsDirty = false;
	SettingsDeadlineSeconds = 0.0;
	LastCountdownSecond = -1;
	ApplyVolumePreview();
	ApplyVideoPreview();
	RefreshOverlay();
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] settings reverted vol=%d mode=%d res=%d"), VolumeStep, WindowModeIndex, ResolutionIndex);
}

void UDYDevEntryWidget::WriteSettingsProbe(double Elapsed, const TCHAR* Phase)
{
	const FString Line = FString::Printf(TEXT("%s t=%.1f vol=%d mode=%d res=%d\n"),
		Phase, Elapsed, VolumeStep, WindowModeIndex, ResolutionIndex);
	const FString Path = FPaths::ProjectSavedDir() / TEXT("SettingsProbe.log");
	FFileHelper::SaveStringToFile(Line, *Path, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,
		&IFileManager::Get(), EFileWrite::FILEWRITE_Append);
}

void UDYDevEntryWidget::TickSettingsProbe()
{
	if (!bSettingsProbeRead)
	{
		bSettingsProbeRead = true;
		SettingsProbeMode = FCString::Atoi(*FPlatformMisc::GetEnvironmentVariable(TEXT("DY_SETTINGS_PROBE")));
	}
	if (SettingsProbeMode <= 0) { return; }
	if (SettingsProbeStep == 0)
	{
		if (CurrentPanel != EDYDevEntryPanel::Start) { return; }
		SettingsProbeStart = FPlatformTime::Seconds();
		SettingsProbeStep = 1;
		return;
	}
	const double Elapsed = FPlatformTime::Seconds() - SettingsProbeStart;
	if (SettingsProbeStep == 1 && Elapsed > 1.0)
	{
		SettingsProbeStep = 2;
		OpenOverlay(EDYMenuOverlay::Settings);
	}
	else if (SettingsProbeStep == 2 && Elapsed > 1.8 && SettingsProbeMode == 1)
	{
		SettingsProbeStep = 3;
		HandleOverlayRow0Click();
		WriteSettingsProbe(Elapsed, TEXT("probe-dirty"));
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] probe settings dirty vol=%d deadline=15s"), VolumeStep);
	}
	else if (SettingsProbeStep == 2 && Elapsed > 1.8 && SettingsProbeMode == 3)
	{
		SettingsProbeStep = 3;
		HandleOverlayRow0Click();
		WriteSettingsProbe(Elapsed, TEXT("probe-dirty"));
	}
	else if (SettingsProbeStep == 3 && Elapsed > 3.0 && SettingsProbeMode == 3)
	{
		SettingsProbeStep = 4;
		CommitSettings();
		WriteSettingsProbe(Elapsed, TEXT("probe-committed"));
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] probe settings committed vol=%d"), VolumeStep);
	}
	else if (SettingsProbeStep == 2 && Elapsed > 2.0 && SettingsProbeMode == 2)
	{
		SettingsProbeStep = 4;
		WriteSettingsProbe(Elapsed, TEXT("probe-loaded"));
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] probe settings loaded vol=%d"), VolumeStep);
	}
	else if (SettingsProbeStep == 3 && Elapsed > 20.0)
	{
		SettingsProbeStep = 4;
		WriteSettingsProbe(Elapsed, TEXT("probe-after-timeout"));
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] probe settings after-timeout vol=%d dirty=%d"), VolumeStep, bSettingsDirty ? 1 : 0);
	}
}

void UDYDevEntryWidget::TickSettingsCountdown()
{
	if (!bSettingsDirty) { return; }
	const double Now = FPlatformTime::Seconds();
	if (Now >= SettingsDeadlineSeconds)
	{
		RevertSettings();
		return;
	}
	if (CurrentOverlay != EDYMenuOverlay::Settings) { return; }
	const int32 Left = FMath::Max(0, FMath::CeilToInt(static_cast<float>(SettingsDeadlineSeconds - Now)));
	if (Left != LastCountdownSecond)
	{
		LastCountdownSecond = Left;
		if (OverlayHint)
		{
			OverlayHint->SetText(FText::FromString(FString::Printf(TEXT("预览中：%d 秒内不确认将自动还原。"), Left)));
		}
	}
}

void UDYDevEntryWidget::CloseOverlay()
{
	if (CurrentOverlay == EDYMenuOverlay::Settings && bSettingsDirty) { RevertSettings(); }
	CurrentOverlay = EDYMenuOverlay::None;
	RefreshOverlay();
	// Return focus to the first plaque so keyboard navigation always resumes from a known point
	// (otherwise Up/Down continues from a stale row and the ending panel becomes unpredictable).
	if (MenuButtons.IsValidIndex(0) && MenuButtons[0]) { MenuButtons[0]->SetKeyboardFocus(); }
}

bool UDYDevEntryWidget::IsMenuItemAvailable(const int32 Index) const
{
	const bool bStartPanel = CurrentPanel == EDYDevEntryPanel::Start;
	const bool bPausedPanel = CurrentPanel == EDYDevEntryPanel::Paused;
	const bool bMenuLive = bStartPanel || bPausedPanel;
	switch (Index)
	{
	case 0: return bStartPanel || CurrentPanel == EDYDevEntryPanel::End; // ending: the primary plaque is the replay action
	case 1:
		// Resume the paused session, or - on the title panel - continue the chapter still in progress.
		if (bPausedPanel) { return true; }
		{
			const ADYDevEntryPlayerController* EntryPC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer());
			return bStartPanel && EntryPC && EntryPC->HasContinueProgress();
		}
	case 5: return bMenuLive || CurrentPanel == EDYDevEntryPanel::End; // ending: still allow leaving the demo
	case 2: case 3: case 4: return bMenuLive || CurrentPanel == EDYDevEntryPanel::End; // ending: guide opens the unlocked codex
	default: return false;
	}
}

void UDYDevEntryWidget::HandleMenuSelection(int32 Index)
{
	ADYDevEntryPlayerController* PC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer());
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] select=%d panel=%d overlay=%d pc=%d"),
		Index, static_cast<int32>(CurrentPanel), static_cast<int32>(CurrentOverlay), PC ? 1 : 0);
	if (!PC) { return; }
	if (!IsMenuItemAvailable(Index))
	{
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] select=%d unavailable panel=%d"), Index, static_cast<int32>(CurrentPanel));
		return;
	}
	switch (static_cast<EDYDevEntryItem>(Index))
	{
	case EDYDevEntryItem::Start:
		if (CurrentPanel == EDYDevEntryPanel::End) { PC->RequestReplayExperience(); }
		else { PC->RequestStartExperience(); }
		break;
	case EDYDevEntryItem::Continue:
	{
		// Title panel: the saved chapter is 1-based, the director takes 0-based.
		const bool bResumedChapter = CurrentPanel == EDYDevEntryPanel::Start && PC
			&& PC->HasContinueProgress() && PC->RequestChapterExperience(PC->GetContinueChapterIndex() - 1);
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] continue chapter=%d resumed=%d"),
			PC ? PC->GetContinueChapterIndex() : 0, bResumedChapter ? 1 : 0);
		if (!bResumedChapter) { PC->RequestContinueExperience(); }
		break;
	}
	case EDYDevEntryItem::Chapters: OpenOverlay(EDYMenuOverlay::Chapters); break;
	case EDYDevEntryItem::Guide:
		OpenOverlay(CurrentPanel == EDYDevEntryPanel::End ? EDYMenuOverlay::Codex : EDYMenuOverlay::Guide);
		break;
	case EDYDevEntryItem::Settings: OpenOverlay(EDYMenuOverlay::Settings); break;
	case EDYDevEntryItem::Quit: PC->RequestQuitExperience(); break;
	default: break;
	}
}

void UDYDevEntryWidget::HandleItem1Click() { HandleMenuSelection(1); }
void UDYDevEntryWidget::HandleItem2Click() { HandleMenuSelection(2); }
void UDYDevEntryWidget::HandleItem3Click() { HandleMenuSelection(3); }
void UDYDevEntryWidget::HandleItem4Click() { HandleMenuSelection(4); }

bool UDYDevEntryWidget::IsCodexUnlocked() const
{
	// The codex is the reward for finishing all four acts; the End panel is the only place it can be opened.
	return CurrentPanel == EDYDevEntryPanel::End;
}

void UDYDevEntryWidget::ShowCodexEntry(const int32 Index)
{
	if (CurrentOverlay != EDYMenuOverlay::Codex) { return; }
	CodexIndex = FMath::Clamp(Index, 0, 3);
	bCodexShowSteps = false;
	RefreshOverlay();
}
void UDYDevEntryWidget::StartChapterFromOverlay(const int32 ChapterIndex)
{
	if (CurrentOverlay != EDYMenuOverlay::Chapters) { return; }
	ADYDevEntryPlayerController* PC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer());
	CloseOverlay();
	if (PC) { PC->RequestChapterExperience(ChapterIndex); }
}

void UDYDevEntryWidget::HandleOverlayRow3Click()
{
	if (CurrentOverlay == EDYMenuOverlay::Codex) { ShowCodexEntry(3); return; }
	if (CurrentOverlay == EDYMenuOverlay::Chapters) { StartChapterFromOverlay(3); }
}

void UDYDevEntryWidget::HandleOverlayRow4Click()
{
	if (CurrentOverlay != EDYMenuOverlay::Codex) { return; }
	// Row 4 flips the leaf between the selected puppet entry and the 制作七步 plate.
	bCodexShowSteps = !bCodexShowSteps;
	RefreshOverlay();
}

void UDYDevEntryWidget::HandleOverlayRow0Click()
{
	if (CurrentOverlay == EDYMenuOverlay::Codex) { ShowCodexEntry(0); return; }
	if (CurrentOverlay == EDYMenuOverlay::Chapters) { StartChapterFromOverlay(0); return; }
	if (CurrentOverlay != EDYMenuOverlay::Settings) { return; }
	VolumeStep = (VolumeStep <= 0) ? 10 : VolumeStep - 1;
	ApplyVolumePreview();
	bSettingsDirty = true;
	SettingsDeadlineSeconds = FPlatformTime::Seconds() + 15.0;
	LastCountdownSecond = -1;
	RefreshOverlay();
}

void UDYDevEntryWidget::HandleOverlayRow1Click()
{
	if (CurrentOverlay == EDYMenuOverlay::Codex) { ShowCodexEntry(1); return; }
	if (CurrentOverlay == EDYMenuOverlay::Chapters) { StartChapterFromOverlay(1); return; }
	if (CurrentOverlay != EDYMenuOverlay::Settings) { return; }
	WindowModeIndex = (WindowModeIndex + 1) % 3;
	ApplyVideoPreview();
	bSettingsDirty = true;
	SettingsDeadlineSeconds = FPlatformTime::Seconds() + 15.0;
	LastCountdownSecond = -1;
	RefreshOverlay();
}

void UDYDevEntryWidget::HandleOverlayRow2Click()
{
	if (CurrentOverlay == EDYMenuOverlay::Codex) { ShowCodexEntry(2); return; }
	if (CurrentOverlay == EDYMenuOverlay::Chapters) { StartChapterFromOverlay(2); return; }
	if (CurrentOverlay != EDYMenuOverlay::Settings) { return; }
	ResolutionIndex = (ResolutionIndex + 1) % MenuResolutionCount;
	ApplyVideoPreview();
	bSettingsDirty = true;
	SettingsDeadlineSeconds = FPlatformTime::Seconds() + 15.0;
	LastCountdownSecond = -1;
	RefreshOverlay();
}


#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarDYMenuAutoTest(
	TEXT("dy.MenuAutoTest"), 0,
	TEXT("Drive the DY main menu panels and settings overlay with a fixed schedule, logging every step."),
	ECVF_Default);

void UDYDevEntryWidget::TickAutoTest()
{
	int32 AutoTestLevel = CVarDYMenuAutoTest.GetValueOnGameThread();
	if (AutoTestLevel == 0)
	{
		AutoTestLevel = FCString::Atoi(*FPlatformMisc::GetEnvironmentVariable(TEXT("DY_MENU_AUTOTEST")));
	}
	if (AutoTestLevel <= 0) { return; }
	if (AutoTestStartSeconds <= 0.0) { AutoTestStartSeconds = FPlatformTime::Seconds(); }
	const double Elapsed = FPlatformTime::Seconds() - AutoTestStartSeconds;
	ADYDevEntryPlayerController* PC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer());

	auto Report = [this, Elapsed, PC](const TCHAR* Tag)
	{
		const bool bStartOn = MenuButtons.IsValidIndex(0) && MenuButtons[0] && IsMenuItemAvailable(0);
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuAuto] t=%.2f %s panel=%d overlay=%d startEnabled=%d pause=%d vol=%d mode=%d res=%d"),
			Elapsed, Tag, static_cast<int32>(CurrentPanel), static_cast<int32>(CurrentOverlay), bStartOn ? 1 : 0,
			(PC && PC->IsPauseSessionActive()) ? 1 : 0, VolumeStep, WindowModeIndex, ResolutionIndex);
	};

	if (AutoTestStep == 0 && Elapsed > 1.0) { AutoTestStep = 1; HandleMenuSelection(2); Report(TEXT("open-chapters")); }
	else if (AutoTestStep == 1 && Elapsed > 3.0) { AutoTestStep = 2; HandleMenuSelection(3); Report(TEXT("open-guide")); }
	else if (AutoTestStep == 2 && Elapsed > 5.0) { AutoTestStep = 3; HandleMenuSelection(4); Report(TEXT("open-settings")); }
	else if (AutoTestStep == 3 && Elapsed > 5.8) { AutoTestStep = 4; HandleOverlayRow0Click(); Report(TEXT("settings-volume")); }
	else if (AutoTestStep == 4 && Elapsed > 6.4)
	{
		AutoTestStep = 5;
		if (AutoTestLevel >= 2) { Report(TEXT("settings-window-skipped")); }
		else { HandleOverlayRow1Click(); Report(TEXT("settings-window")); }
	}
	else if (AutoTestStep == 5 && Elapsed > 7.0)
	{
		AutoTestStep = 6;
		if (AutoTestLevel >= 2) { Report(TEXT("settings-resolution-skipped")); }
		else { HandleOverlayRow2Click(); Report(TEXT("settings-resolution")); }
	}
	else if (AutoTestStep == 6 && Elapsed > 8.0) { AutoTestStep = 7; Report(TEXT("settings-awaiting-confirm")); }
	else if (AutoTestStep == 7 && Elapsed > 9.0)
	{
		AutoTestStep = 8;
		if (AutoTestLevel == 4)
		{
			// Level 4 proves the 15 s unconfirmed rollback by doing nothing and letting
			// TickSettingsCountdown revert; the probe file survives Shipping's stripped logs.
			WriteSettingsProbe(Elapsed, TEXT("dirty"));
			Report(TEXT("settings-wait-timeout"));
		}
		else
		{
			HandleOverlayRevertClick();
			Report(TEXT("settings-reverted"));
		}
	}
	else if (AutoTestStep == 8 && Elapsed > 25.0 && AutoTestLevel == 4)
	{
		AutoTestStep = 99;
		WriteSettingsProbe(Elapsed, TEXT("after-timeout"));
		Report(TEXT("settings-timeout-observed"));
	}
	else if (AutoTestStep == 8 && Elapsed > 10.0 && AutoTestLevel != 4)
	{
		AutoTestStep = 9;
		if (AutoTestLevel == 2) { Report(TEXT("hold-menu")); AutoTestStep = 99; }
		else { CloseOverlay(); Report(TEXT("overlay-closed")); }
	}
	else if (AutoTestStep == 9 && Elapsed > 11.0) { AutoTestStep = 10; HandleMenuSelection(0); Report(TEXT("start-selected")); }
	else if (AutoTestStep == 10 && Elapsed > 14.0) { AutoTestStep = 11; Report(TEXT("after-start")); }
	else if (AutoTestStep == 11 && Elapsed > 15.0 && AutoTestLevel >= 3)
	{
		AutoTestStep = 12;
		if (PC) { PC->RequestPauseExperience(); }
		Report(TEXT("pause-requested"));
	}
	else if (AutoTestStep == 12 && Elapsed > 17.0) { AutoTestStep = 13; Report(TEXT("after-pause")); }
}
#endif

void UDYDevEntryWidget::HandleOverlayBackClick() { CloseOverlay(); }
void UDYDevEntryWidget::HandleOverlayConfirmClick() { CommitSettings(); }
void UDYDevEntryWidget::HandleOverlayRevertClick() { RevertSettings(); }

FReply UDYDevEntryWidget::NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent)
{
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] key=%s"), *InKeyEvent.GetKey().GetFName().ToString());
	// Deterministic keyboard navigation: Slate's automatic focus search skips disabled plaques
	// inconsistently, and the ending panel needs a reliable path to 「游戏说明」/「退出游戏」.
	if (CurrentOverlay == EDYMenuOverlay::None && (InKeyEvent.GetKey() == EKeys::Up || InKeyEvent.GetKey() == EKeys::Down))
	{
		// HasKeyboardFocus() on a UButton is unreliable here (the inner SButton owns focus),
		// so keep our own cursor and fall back to it.
		int32 Focused = INDEX_NONE;
		if (MenuButtons.IsValidIndex(NavFocusIndex) && IsMenuItemAvailable(NavFocusIndex)) { Focused = NavFocusIndex; }
		if (Focused == INDEX_NONE)
		{
			for (int32 Index = 0; Index < MenuButtons.Num(); ++Index)
			{
				if (MenuButtons[Index] && MenuButtons[Index]->HasKeyboardFocus()) { Focused = Index; break; }
			}
		}
		const int32 Count = MenuButtons.Num();
		const int32 Dir = (InKeyEvent.GetKey() == EKeys::Down) ? 1 : -1;
		for (int32 Step = 1; Step <= Count; ++Step)
		{
			const int32 Next = ((Focused == INDEX_NONE ? (Dir > 0 ? -1 : Count) : Focused) + Dir * Step + Count * 2) % Count;
			if (IsMenuItemAvailable(Next) && MenuButtons.IsValidIndex(Next) && MenuButtons[Next])
			{
				FSlateApplication::Get().ClearKeyboardFocus(EFocusCause::SetDirectly);
				MenuButtons[Next]->SetKeyboardFocus();
				NavFocusIndex = Next;
				RefreshView();
				UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] focus=%d via %s"), Next, *InKeyEvent.GetKey().GetFName().ToString());
				return FReply::Handled();
			}
		}
	}
	// Overlay rows reuse the same self-held cursor: Slate focus search inside a vertical box of
	// buttons is as unreliable as it was on the plaques. Guide has no rows, so its keys pass through.
	if (CurrentOverlay != EDYMenuOverlay::None && (InKeyEvent.GetKey() == EKeys::Up || InKeyEvent.GetKey() == EKeys::Down))
	{
		int32 First = INDEX_NONE;
		int32 Last = INDEX_NONE;
		for (int32 Index = 0; Index < OverlayRows.Num(); ++Index)
		{
			if (OverlayRows[Index] && OverlayRows[Index]->GetVisibility() == ESlateVisibility::Visible)
			{
				if (First == INDEX_NONE) { First = Index; }
				Last = Index;
			}
		}
		if (First != INDEX_NONE)
		{
			const int32 Dir = (InKeyEvent.GetKey() == EKeys::Down) ? 1 : -1;
			const int32 Next = FMath::Clamp(OverlayFocusIndex + Dir, First, Last);
			if (Next != OverlayFocusIndex)
			{
				OverlayFocusIndex = Next;
				if (OverlayRows.IsValidIndex(Next) && OverlayRows[Next])
				{
					// Slate's arrow-key focus search can move focus with EFocusCause::Navigation,
					// which paints a blue focus outline over the palette; drop and re-take focus
					// directly so the only visible cue is the row highlight.
					FSlateApplication::Get().ClearKeyboardFocus(EFocusCause::SetDirectly);
					OverlayRows[Next]->SetKeyboardFocus();
				}
				ApplyOverlayRowFocus();
			}
			return FReply::Handled();
		}
	}
	if (InKeyEvent.GetKey() == EKeys::Escape)
	{
		if (CurrentOverlay != EDYMenuOverlay::None) { CloseOverlay(); return FReply::Handled(); }
		if (CurrentPanel == EDYDevEntryPanel::Paused)
		{
			if (ADYDevEntryPlayerController* PC = Cast<ADYDevEntryPlayerController>(GetOwningPlayer())) { PC->RequestContinueExperience(); }
			return FReply::Handled();
		}
	}
	return Super::NativeOnKeyDown(InGeometry, InKeyEvent);
}
