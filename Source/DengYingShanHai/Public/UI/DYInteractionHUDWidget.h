#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
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
	static FText GetAlignmentStatusText(const FDYPlayerAlignmentDisplay& Snapshot, EDYStageFeedbackDisplay Display);
	static FText GetAlignmentReadinessText(const FDYPlayerAlignmentDisplay& Snapshot);
	static bool ShouldShowHoldProgress(const FDYPlayerAlignmentDisplay& Snapshot, EDYStageFeedbackDisplay Display);
	static FText GetPromptText(bool bHasFocus, bool bIsControlling);
	static FText GetStatusText(EDYStageFeedbackDisplay Display);
	static FText GetActStatusText(const FDYActSequenceSnapshot& Snapshot, EDYStageFeedbackDisplay Display);

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
	FDYPlayerAlignmentDisplay AlignmentDisplay;
	UPROPERTY(Transient) TArray<TObjectPtr<UBorder>> Crosshair;
	FDYActSequenceSnapshot ActDisplay;
	bool bFocused = false;
	bool bControlling = false;
	EDYStageFeedbackDisplay Feedback = EDYStageFeedbackDisplay::Hidden;
};
