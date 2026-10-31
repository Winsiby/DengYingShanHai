#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Engine/TimerHandle.h"
#include "Puzzles/DYActSequenceTypes.h"
#include "Stage/DYStageFeedbackTypes.h"
#include "DYInteractionHUDWidget.generated.h"

class UFont;
class UTextBlock;
class UBorder;
class UProgressBar;
class USizeBox;

/** Passive UMG view. No Director, timers, input, actor discovery or answer data. */
UCLASS(Blueprintable, meta = (DisableNativeTick))
class DENGYINGSHANHAI_API UDYInteractionHUDWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	explicit UDYInteractionHUDWidget(const FObjectInitializer& ObjectInitializer);
	void ApplySnapshot(bool bHasFocus, bool bIsControlling, EDYStageFeedbackDisplay Display);
	void ApplyActSnapshot(const FDYActSequenceSnapshot& Snapshot);
	void ApplyAlignmentSnapshot(const FDYPlayerAlignmentDisplay& Snapshot);
	/** Transient guidance line (entry walk). Cosmetic only; never a puzzle hint or flow state. */
	void ShowHint(const FText& InText, float Seconds);
	/** Explicit show state from the performance component; independent of transient walk hints. */
	void SetPerformancePresentation(bool bActive);
	void ShowPerformanceCaption(const FText& InText);
	bool IsPerformancePresentationActive() const { return bPerformancePresentation; }
	/** Entry walk shows only the transient hint; stage instrumentation returns on arrival. */
	void SetStageHudVisible(bool bVisible);
	/** Keeps the widget itself visible (so UMG still lays it out) while showing only the walk copy. */
	void SetEntryWalkGuide(bool bActive, const FText& InText);
	/** Entry-walk guidance copy; one string so the menu and HUD never diverge. */
	static FText GetEntryWalkHint();
	static FText GetEntryArrivalHint();
	static FText GetAlignmentStatusText(const FDYPlayerAlignmentDisplay& Snapshot, EDYStageFeedbackDisplay Display);
	static FText GetAlignmentReadinessText(const FDYPlayerAlignmentDisplay& Snapshot);
	static bool ShouldShowHoldProgress(const FDYPlayerAlignmentDisplay& Snapshot, EDYStageFeedbackDisplay Display);
	static FText GetPromptText(bool bHasFocus, bool bIsControlling);
	static FText GetStatusText(EDYStageFeedbackDisplay Display);
	static FText GetActStatusText(const FDYActSequenceSnapshot& Snapshot, EDYStageFeedbackDisplay Display);
	/** Chapter interlude card: a display-only read of the chapter fields already in the snapshot. */
	static bool ShouldShowChapterCard(const FDYActSequenceSnapshot& Snapshot, int32 LastShownChapterIndex);
	static FText MakeChapterCardText(const FDYActSequenceSnapshot& Snapshot);

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;

	/** Explicit project font; never a system-installed font or editor fallback. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|UI")
	TObjectPtr<UFont> ChineseFont;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|UI")
	FText ActTitle;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|UI", meta = (ClampMin = "12", ClampMax = "40"))
	int32 BodyFontSize = 22;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|UI")
	FLinearColor PaperColor = FLinearColor(0.93f, 0.89f, 0.80f, 1.0f);
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|UI")
	FLinearColor AccentColor = FLinearColor(0.87f, 0.62f, 0.28f, 1.0f);

private:
	void BuildNativePrototype();
	void RefreshView();
	UPROPERTY(Transient) TObjectPtr<UTextBlock> TitleText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> Prompt;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> Status;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> Readiness;
	UPROPERTY(Transient) TObjectPtr<UProgressBar> HoldProgress;
	UPROPERTY(Transient) TObjectPtr<USizeBox> HoldProgressBox;
	UPROPERTY(Transient) TObjectPtr<UBorder> PromptBack;
	FTimerHandle HintHandle;
	/** Chapter card state. The card waits for the stage HUD so the entry walk never shows it. */
	/** The card belongs to the stage; the exterior corridor and menu-picked chapters wait for arrival. */
	bool IsStageReached() const;
	void ShowChapterCard(const FText& InText);
	void StartChapterCardCountdown();
	void HideChapterCard();
	FTimerHandle ChapterCardHandle;
	FText ChapterCardText;
	int32 LastChapterCardIndex = INDEX_NONE;
	bool bChapterCardActive = false;
	bool bChapterCardCountdown = false;
	static constexpr float ChapterCardSeconds = 2.8f;
	bool bPerformancePresentation = false;
	FText PerformanceCaptionText;
	/** While set, the bottom plaque shows entry guidance instead of stage instrumentation. */
	bool bHintOverride = false;
	FText HintOverrideText;
	void HideHint();
	FDYPlayerAlignmentDisplay AlignmentDisplay;
	bool bStageHudVisible = true;
	bool bEntryWalkGuide = false;
	FText EntryWalkGuideText;
	UPROPERTY(Transient) TArray<TObjectPtr<UBorder>> Crosshair;
	FDYActSequenceSnapshot ActDisplay;
	bool bFocused = false;
	bool bControlling = false;
	EDYStageFeedbackDisplay Feedback = EDYStageFeedbackDisplay::Hidden;
};
