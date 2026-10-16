#pragma once

#include "CoreMinimal.h"
#include "Core/DYStagePlayerController.h"
#include "Engine/EngineBaseTypes.h"
#include "Engine/EngineTypes.h"
#include "Puzzles/DYActSequenceTypes.h"
#include "UI/DYDevEntryWidget.h"
#include "DYDevEntryPlayerController.generated.h"

class ADYStageGameMode;
class ADYStagePresentation;
class ADYPuzzleDirector;

/** Independent Dev opt-in: local menu intent/focus, never puzzle or camera authority. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYDevEntryPlayerController : public ADYStagePlayerController
{
	GENERATED_BODY()
public:
	ADYDevEntryPlayerController();
	UFUNCTION(BlueprintCallable, Category = "DY|Dev Entry") bool RequestStartExperience();
	UFUNCTION(BlueprintCallable, Category = "DY|Dev Entry") bool RequestReplayExperience();
	UFUNCTION(BlueprintCallable, Category = "DY|Dev Entry") void RequestQuitExperience();
	UFUNCTION(BlueprintPure, Category = "DY|Dev Entry") EDYDevEntryPanel GetEntryPanel() const;
protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	virtual FName GetCurrentDevEntryMap() const;
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry") TSubclassOf<UDYDevEntryWidget> MenuWidgetClass;
private:
	/** One exact identity resolver shared by menu opt-in and same-map replay. */
	static FName ResolveDevEntryMapName(const FString& PackageName, EWorldType::Type WorldType);
	bool IsEntryLoopWorld() const;
	ADYPuzzleDirector* GetBoundDirector() const;
	void AttachPresentation(ADYStagePresentation* Stage);
	void HandleActDisplay(const FDYActSequenceSnapshot& Snapshot);
	static bool ShouldReleaseControlForActEntry(const FDYActSequenceSnapshot& Current, int32 LastPlayingActIndex);
	void RefreshControlForActEntry();
	void RefreshMenu();
	void PerformReplay();
	void HandleTravelFailure(UWorld* World, ETravelFailure::Type Failure, const FString& Error);
	UPROPERTY(Transient) TObjectPtr<UDYDevEntryWidget> MenuView;
	TWeakObjectPtr<ADYStageGameMode> BoundMode;
	TWeakObjectPtr<ADYStagePresentation> BoundStage;
	FDelegateHandle RegistrationHandle;
	FDelegateHandle ActHandle;
	FDelegateHandle TravelFailureHandle;
	FTimerHandle ReadyRefreshHandle;
	FTimerHandle ReplayHandle;
	bool bRequestInFlight = false;
	bool bReplayPending = false;
	bool bEndingPlay = false;
	bool bMenuInputApplied = false;
	/** Current bound Stage only; same-act reset and cosmetic synchronization do not release control. */
	int32 LastObservedPlayingActIndex = INDEX_NONE;
#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYEntryLoopTestSeam;
#endif
};
