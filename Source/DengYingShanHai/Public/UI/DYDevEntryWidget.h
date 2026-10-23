#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "DYDevEntryWidget.generated.h"

class UFont;
class UTextBlock;
class UButton;
class UBorder;
class UImage;
class UCanvasPanel;
class UCanvasPanelSlot;
class USizeBox;
class UScaleBox;
class UVerticalBox;
class UHorizontalBox;
class UTexture2D;

/** Derived menu display only; never a second experience state machine. */
UENUM(BlueprintType)
enum class EDYDevEntryPanel : uint8 { Waiting, Start, Hidden, End, Reloading, Paused };

/** Native overlay cards reachable from the frozen six-entry menu (read-only or settings). */
enum class EDYMenuOverlay : uint8 { None, Chapters, Guide, Settings, Codex };

/** Six entries of the V2.2 main menu, in visual order. */
enum class EDYDevEntryItem : uint8 { Start, Continue, Chapters, Guide, Settings, Quit, Count };

/** Native Dev prototype view. Blueprint may author font/style; no puzzle references. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API UDYDevEntryWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	UDYDevEntryWidget(const FObjectInitializer& ObjectInitializer);
	void ApplyPanel(EDYDevEntryPanel Panel);
	void CloseOverlay();
	bool HasReadyView() const;
	UWidget* GetPrimaryFocusWidget() const;
	static FText GetTitle(EDYDevEntryPanel Panel);
	static FText GetPrimaryLabel(EDYDevEntryPanel Panel);
	static FText GetBody(EDYDevEntryPanel Panel);
	/** 影偶图鉴正文（造型 / 操演 / 锣鼓 / 制作七步）。抽成纯函数，便于自动化断言非遗五项都在。 */
	static FString MakeCodexEntry(int32 Index);
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;
	virtual FReply NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent) override;
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UFont> ChineseFont;

	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UFont> GuideSerifFont;

	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UFont> GuideSerifBoldFont;
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UTexture2D> MenuBackgroundTexture;
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UTexture2D> PlaqueNormalTexture;
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UTexture2D> PlaqueHoverTexture;
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UTexture2D> PlaquePressedTexture;
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UTexture2D> PlaqueDisabledTexture;
private:
	/** Optional serif guide faces; a missing face falls back to ChineseFont instead of failing the CDO. */
	void EnsureGuideFonts();
	void BuildView();
	void BuildMenuItems();
	void BuildGuidePanel();
	void BuildOverlay();
	void OpenOverlay(EDYMenuOverlay Kind);
	void RefreshOverlay();
	void RefreshSettingsRows();
	/** Overlay rows are UButtons, and FButtonStyle has no focused brush in 5.8: repaint the row under the keyboard cursor ourselves. */
	void ApplyOverlayRowFocus();
	void ApplyVolumePreview();
	void ApplyVideoPreview();
	void CommitSettings();
	void RevertSettings();
	void TickSettingsCountdown();
	void WriteSettingsProbe(double Elapsed, const TCHAR* Phase);
	bool IsMenuItemAvailable(int32 Index) const;
	void HandleMenuSelection(int32 Index);
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
	void RefreshView();
	bool bGeometryLogged = false;
	void HideForeignOverlays();
	bool bLoggedOverlays = false;
	UButton* MakeMenuItem(EDYDevEntryItem Item, const FText& Label, UTextBlock*& OutLabel, FName LabelName);
	UFUNCTION() void HandlePrimaryClick();
	UFUNCTION() void HandleItem1Click();
	UFUNCTION() void HandleItem2Click();
	UFUNCTION() void HandleItem3Click();
	UFUNCTION() void HandleItem4Click();
	UFUNCTION() void HandleOverlayRow0Click();
	UFUNCTION() void HandleOverlayRow1Click();
	UFUNCTION() void HandleOverlayRow2Click();
	UFUNCTION() void HandleOverlayRow3Click();
	/** Codex leaf row 4: swap the entry text for the seven-step 制作图版. */
	UFUNCTION() void HandleOverlayRow4Click();
	/** Chapter list rows start the selected act chapter directly. */
	void StartChapterFromOverlay(int32 ChapterIndex);
	/** 图鉴只在剧终（End 面板）解锁；条目切换只改本页正文。 */
	bool IsCodexUnlocked() const;
	void ShowCodexEntry(int32 Index);
	UFUNCTION() void HandleOverlayBackClick();
	UFUNCTION() void HandleOverlayConfirmClick();
	UFUNCTION() void HandleOverlayRevertClick();
	UFUNCTION() void HandleQuitClick();
	UFUNCTION() void HandleReplayClick();
	UPROPERTY(Transient) TObjectPtr<UCanvasPanel> RootCanvas;
	UPROPERTY(Transient) TObjectPtr<UCanvasPanel> Stage;
	UPROPERTY(Transient) TObjectPtr<UImage> Background;
	UPROPERTY(Transient) TObjectPtr<UBorder> Backdrop;
	UPROPERTY(Transient) TObjectPtr<UBorder> GuidePanel;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> GuideText;
	UPROPERTY(Transient) TObjectPtr<UVerticalBox> MenuColumn;
	UPROPERTY(Transient) TObjectPtr<UBorder> EndCard;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> EndTitle;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> EndBody;
	UPROPERTY(Transient) TObjectPtr<UButton> PrimaryButton;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> PrimaryLabel;
	UPROPERTY(Transient) TObjectPtr<UButton> QuitButton;
	UPROPERTY(Transient) TObjectPtr<UButton> ReplayButton;
	UPROPERTY(Transient) TArray<TObjectPtr<UButton>> MenuButtons;
	UPROPERTY(Transient) TArray<TObjectPtr<UTextBlock>> MenuLabels;
	UPROPERTY(Transient) TArray<FText> MenuBaseLabels;
	EDYDevEntryPanel CurrentPanel = EDYDevEntryPanel::Waiting;

	UPROPERTY(Transient) TObjectPtr<UCanvasPanel> OverlayRoot;
	UPROPERTY(Transient) TObjectPtr<UBorder> OverlayCard;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> OverlayTitle;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> OverlayBody;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> OverlayHint;
	UPROPERTY(Transient) TArray<TObjectPtr<UButton>> OverlayRows;
	UPROPERTY(Transient) TArray<TObjectPtr<UTextBlock>> OverlayRowLabels;
	UPROPERTY(Transient) TObjectPtr<UButton> OverlayBackButton;
	UPROPERTY(Transient) TObjectPtr<UButton> OverlayConfirmButton;
	UPROPERTY(Transient) TObjectPtr<UButton> OverlayRevertButton;
	/** Codex illustration: the delivered concept sheet, cropped to the figure, shown left of the entry text. */
	UPROPERTY(Transient) TObjectPtr<USizeBox> CodexArtBox;
	UPROPERTY(Transient) TObjectPtr<UImage> CodexArt;
	/** Index order matches CodexIndex: Kuafu, Jingwei, Xingtian, Zhulong. Hard references keep them cooked. */
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TArray<TObjectPtr<UTexture2D>> CodexArtTextures;
	/** C3 制作七步 plate: the seven-cell process sheet, shown when codex row 4 is picked. */
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UTexture2D> CodexStepsTexture;
	EDYMenuOverlay CurrentOverlay = EDYMenuOverlay::None;
	int32 CodexIndex = 0;
	/** Codex leaf mode: false = one puppet entry, true = the 制作七步 plate. */
	bool bCodexShowSteps = false;
	/** Dev-only guard so the DY_CODEX_PREVIEW screenshot hook opens the leaf exactly once. */
	bool bCodexPreviewApplied = false;
	// Tracked by NativeOnKeyDown so Up/Down keeps stepping instead of snapping back to the first plaque.
	int32 NavFocusIndex = 0;
	/** Keyboard cursor inside 演出篇章 / 设置 / 影偶图鉴 rows. */
	int32 OverlayFocusIndex = 0;
	int32 VolumeStep = 10;
	int32 WindowModeIndex = 2;
	int32 ResolutionIndex = 2;
	int32 SavedVolumeStep = 10;
	int32 SavedWindowModeIndex = 2;
	int32 SavedResolutionIndex = 2;
	double SettingsDeadlineSeconds = 0.0;
	int32 SettingsProbeStep = 0;
	double SettingsProbeStart = 0.0;
	bool bSettingsProbeRead = false;
	int32 SettingsProbeMode = 0;
	int32 LastCountdownSecond = -1;
	bool bSettingsDirty = false;
	bool bSettingsInitialized = false;
	TMap<TWeakObjectPtr<UUserWidget>, ESlateVisibility> SuppressedOverlays;
#if !UE_BUILD_SHIPPING
	void TickAutoTest();
#endif
	void TickSettingsProbe();
#if !UE_BUILD_SHIPPING
	int32 AutoTestStep = 0;
	double AutoTestStartSeconds = 0.0;
#endif
#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYEntryLoopTestSeam;
#endif
};
