#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "DYDevEntryWidget.generated.h"

class UFont;
class UTextBlock;
class UButton;
class UBorder;
class UCanvasPanelSlot;

/** Derived menu display only; never a second experience state machine. */
UENUM(BlueprintType)
enum class EDYDevEntryPanel : uint8 { Waiting, Start, Hidden, End, Reloading };

/** Native Dev prototype view. Blueprint may author font/style; no puzzle references. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API UDYDevEntryWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	UDYDevEntryWidget(const FObjectInitializer& ObjectInitializer);
	void ApplyPanel(EDYDevEntryPanel Panel);
	bool HasReadyView() const;
	UWidget* GetPrimaryFocusWidget() const;
	static FText GetTitle(EDYDevEntryPanel Panel);
	static FText GetPrimaryLabel(EDYDevEntryPanel Panel);
	static FText GetBody(EDYDevEntryPanel Panel);
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry|Style") TObjectPtr<UFont> ChineseFont;
private:
	void BuildView();
	void RefreshView();
	UFUNCTION() void HandlePrimaryClick();
	UFUNCTION() void HandleQuitClick();
	UPROPERTY(Transient) TObjectPtr<UBorder> Backdrop;
	UPROPERTY(Transient) TObjectPtr<UCanvasPanelSlot> CardSlot;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> Title;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> Body;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> PrimaryLabel;
	UPROPERTY(Transient) TObjectPtr<UButton> PrimaryButton;
	UPROPERTY(Transient) TObjectPtr<UButton> QuitButton;
	EDYDevEntryPanel CurrentPanel = EDYDevEntryPanel::Waiting;
#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYEntryLoopTestSeam;
#endif
};
