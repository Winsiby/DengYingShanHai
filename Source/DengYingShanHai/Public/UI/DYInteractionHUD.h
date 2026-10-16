#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "Puzzles/DYActSequenceTypes.h"
#include "Stage/DYStageFeedbackTypes.h"
#include "DYInteractionHUD.generated.h"

class ADYStageGameMode;
class ADYStagePresentation;
class UDYInteractionComponent;
class UDYInteractionHUDWidget;
class UUserWidget;

/** Local-PC cosmetic adapter. No polling, puzzle evaluation, view-target or input ownership. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYInteractionHUD : public AHUD
{
	GENERATED_BODY()
public:
	ADYInteractionHUD();
protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	UPROPERTY(EditDefaultsOnly, Category = "DY|UI")
	TSubclassOf<UDYInteractionHUDWidget> WidgetClass;
private:
	void BindGameMode(ADYStageGameMode* Mode);
	void UnbindGameMode();
	void AttachPresentation(ADYStagePresentation* Presentation);
	void HandleDisplay(EDYStageFeedbackDisplay Display);
	void HandleActDisplay(const FDYActSequenceSnapshot& Snapshot);
	void HandleAlignmentDisplay(const FDYPlayerAlignmentDisplay& Snapshot);
	void BindPawn(APawn* Pawn);
	void RefreshInteraction();
	void RefreshView();
	UFUNCTION() void HandlePawnChanged(APawn* OldPawn, APawn* NewPawn);
	UFUNCTION() void HandleFocusChanged(AActor* Previous, AActor* Current);
	UFUNCTION() void HandleControlChanged(AActor* Controlled, bool bIsControlling);
	void HandleWidgetDestruct(UUserWidget* RemovedWidget);
	UPROPERTY(Transient) TObjectPtr<UDYInteractionHUDWidget> View;
	TWeakObjectPtr<APlayerController> BoundController;
	TWeakObjectPtr<ADYStageGameMode> BoundMode;
	TWeakObjectPtr<ADYStagePresentation> BoundPresentation;
	TWeakObjectPtr<UDYInteractionComponent> BoundInteraction;
	FDelegateHandle RegistrationHandle;
	FDelegateHandle DisplayHandle;
	FDelegateHandle ActDisplayHandle;
	FDelegateHandle AlignmentDisplayHandle;
	FDYPlayerAlignmentDisplay AlignmentDisplay;
	FDYActSequenceSnapshot ActDisplay;
	bool bFocused = false;
	bool bControlling = false;
	EDYStageFeedbackDisplay Feedback = EDYStageFeedbackDisplay::Hidden;
#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYPlayerHUDTestSeam;
	friend struct FDYActSequenceTestSeam;
	friend struct FDYAlignmentFeedbackTestSeam;
#endif
};
