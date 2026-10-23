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
class UAudioComponent;
class USoundWave;

/** Independent Dev opt-in: local menu intent/focus, never puzzle or camera authority. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYDevEntryPlayerController : public ADYStagePlayerController
{
	GENERATED_BODY()
public:
	ADYDevEntryPlayerController();
	UFUNCTION(BlueprintCallable, Category = "DY|Dev Entry") bool RequestStartExperience();
	/** Four-act campaign: open the selected chapter (0-based) straight from the chapter list. */
	UFUNCTION(BlueprintCallable, Category = "DY|Dev Entry") bool RequestChapterExperience(int32 ChapterIndex);
	UFUNCTION(BlueprintCallable, Category = "DY|Dev Entry") bool RequestReplayExperience();
	UFUNCTION(BlueprintCallable, Category = "DY|Dev Entry") void RequestQuitExperience();
	/** Pause menu is an in-memory session only; it never persists across a cold start. */
	UFUNCTION(BlueprintCallable, Category = "DY|Dev Entry") bool RequestPauseExperience();
	UFUNCTION(BlueprintCallable, Category = "DY|Dev Entry") bool RequestContinueExperience();
	UFUNCTION(BlueprintPure, Category = "DY|Dev Entry") bool IsPauseSessionActive() const { return bPausedSession; }
	/** Title-panel "继续游戏" is only offered while a chapter was started and not yet finished. */
	UFUNCTION(BlueprintPure, Category = "DY|Dev Entry") bool HasContinueProgress() const { return ContinueChapterIndex > 0; }
	/** 1-based chapter the saved run stopped at; 0 means nothing to continue. */
	UFUNCTION(BlueprintPure, Category = "DY|Dev Entry") int32 GetContinueChapterIndex() const { return ContinueChapterIndex; }
	/** True once that act has been played to its end at least once: the chapter list marks it so a judge can see the four-act structure is real state. */
	UFUNCTION(BlueprintPure, Category = "DY|Dev Entry") bool WasChapterPlayed(int32 ChapterIndex) const;
	UFUNCTION(BlueprintPure, Category = "DY|Dev Entry") bool HasAnyPlayedChapter() const { return PlayedChapterMask != 0; }
	UFUNCTION(BlueprintPure, Category = "DY|Dev Entry") EDYDevEntryPanel GetEntryPanel() const;
protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	virtual void SetupInputComponent() override;
	virtual void PlayerTick(float DeltaSeconds) override;
	virtual FName GetCurrentDevEntryMap() const;
	UPROPERTY(EditDefaultsOnly, Category = "DY|Dev Entry") TSubclassOf<UDYDevEntryWidget> MenuWidgetClass;
private:
	/** One exact identity resolver shared by menu opt-in and same-map replay. */
	static FName ResolveDevEntryMapName(const FString& PackageName, EWorldType::Type WorldType);
	bool IsEntryLoopWorld() const;
	/** L_DY_Main is the theater world; the dev entry labs are not. */
	bool IsTheaterEntryMap() const;
	ADYPuzzleDirector* GetBoundDirector() const;
	void AttachPresentation(ADYStagePresentation* Stage);
	void HandleActDisplay(const FDYActSequenceSnapshot& Snapshot);
	/** Persisted in GameUserSettings.ini so a cold start can resume the chapter, never the act. */
	void LoadContinueProgress();
	void StoreContinueProgress(int32 InChapterIndex);
	void MarkChapterPlayed(int32 ChapterIndex);
	void WriteContinueProgress();
	void UpdateContinueProgress(const FDYActSequenceSnapshot& Snapshot);
	static bool ShouldReleaseControlForActEntry(const FDYActSequenceSnapshot& Current, int32 LastPlayingActIndex);
	void RefreshControlForActEntry();
	void RefreshMenu();
	void HandleEscape();
	void HandleSkipPerformance();
	/** L_DY_Main only: point the player down the lantern path and confirm the theater entry. Cosmetic. */
	void BeginEntryWalkGuidance();
	void HandleEntryWalkCheck();
	/** Safety net: the play instrumentation must never stay hidden after a missed walk. */
	void RestoreStageHud();
	/** Blueprint-side stage cue text (no C++ handle exists) hidden from the first frame until the player enters. */
	int32 SetEntryIntroCueVisible(bool bVisible);
	/** Re-issues the exterior entry hint until the HUD exists, so spawn order cannot swallow it. */
	void EnsureEntryWalkHint();
	/** Review viewpoint selected by the DY_DEBUG_VIEW environment variable (also honoured in Shipping for on-site checks). */
	void ApplyDebugReviewView();
	int32 DebugViewIndex = 0;
	int32 DebugViewPanel = 0;
	/** Dev-only: DY_MENU_PANEL=end paints the ending panel for visual review without finishing the acts. */
	bool bPreviewEnding = false;
	bool bLoggedHud = false;
	/** Self-made ambience (procedural wav, see Docs/LICENSES.md SELF-005). Loops until the level ends. */
	void StartTheatreAmbience();
	UFUNCTION() void HandleAmbienceFinished();
	/** Self-made gong/drum cues on act and chapter boundaries (SELF-006). Never fired per frame. */
	void PlaySequenceCue(const FDYActSequenceSnapshot& Snapshot);
	void PlayStageCue(int32 CueIndex);
	int32 LastCuedChapterIndex = INDEX_NONE;
	uint8 LastCuedPhase = 0;
	/** Dev/test instrumentation: DY_PERF_PROBE=1 appends one FPS line per second to Saved/PerfProbe.log. */
	void StartPerformanceProbe();
	void SamplePerformance();
	/** Dev/test instrumentation: DY_ART_PROBE=1 appends one stage-art line per second to Saved/ArtProbe.log. */
	void StartArtProbe();
	void SampleArtProbe();
	/** Explicit process-local acceptance harness. Absent DY_FLOW_VERIFY leaves normal play unchanged. */
	void StartFlowVerification();
	void TickFlowVerification();
	void WriteFlowVerificationProbe(const FString& Event) const;
	void FinishFlowVerification(bool bSuccess, const TCHAR* Reason);
	static bool FlowVerificationHasCompleteEvidence(uint32 StepMask, uint32 PerformanceMask, bool bWalkedInside);
	FTimerHandle FlowVerificationHandle;
	bool bFlowVerificationEnabled = false;
	bool bFlowVerificationStarted = false;
	bool bFlowVerificationWalkedInside = false;
	FString LastFlowVerificationState;
	double FlowVerificationShowStarted = 0.0;
	FTimerHandle ArtProbeHandle;
	int32 ArtProbeSamples = 0;
	void PerformReplay();
	/** Replay reloads the map, so the fresh world re-enters the performance by itself. */
	void TryAutoStartAfterReplay();
	void HandleTravelFailure(UWorld* World, ETravelFailure::Type Failure, const FString& Error);
	UPROPERTY(Transient) TObjectPtr<UDYDevEntryWidget> MenuView;
	TWeakObjectPtr<ADYStageGameMode> BoundMode;
	TWeakObjectPtr<ADYStagePresentation> BoundStage;
	FDelegateHandle RegistrationHandle;
	FDelegateHandle ActHandle;
	FDelegateHandle TravelFailureHandle;
	FTimerHandle ReadyRefreshHandle;
	FTimerHandle ReplayHandle;
	FTimerHandle EntryWalkHandle;
	FTimerHandle EntryWalkTimeoutHandle;
	FTimerHandle PerfProbeHandle;
	FTimerHandle AutoReplayHandle;
	int32 AutoReplayAttempts = 0;
	int32 PerfProbeSamples = 0;
	double PerfProbeSeconds = 0.0;
	float PerfProbeMin = 10000.f;
	float PerfProbeMax = 0.f;
	float PerfProbeFps = 0.f;
	bool bRequestInFlight = false;
	bool bReplayPending = false;
	bool bEndingPlay = false;
	bool bEntryHintIssued = false;
	bool bEntryWalkSettled = false;
	/** 60s timeout retires the center hint, but the blueprint cue stays hidden until the door. */
	bool bEntryHintRetired = false;
	UPROPERTY(Transient) TObjectPtr<UAudioComponent> AmbienceComponent;
	UPROPERTY(Transient) TObjectPtr<USoundWave> AmbienceWave;
	UPROPERTY(Transient) TArray<TObjectPtr<USoundWave>> CueWaves;
	double LastEntryHintSeconds = 0.0;
	bool bMenuInputApplied = false;
	bool bPausedSession = false;
	/** 1-based chapter index of the run in progress (0 = none). Chapter granularity only. */
	int32 ContinueChapterIndex = 0;
	/** Bit per act (0..3) recorded in Saved/DYProgress.txt; survives restarts so the chapter list can show 已演. */
	int32 PlayedChapterMask = 0;
	/** Last act the controller saw running; used to decide when the previous act is finished. */
	int32 LastProgressChapterIndex = -1;
	double LastEscapeSeconds = 0.0;
	/** Current bound Stage only; same-act reset and cosmetic synchronization do not release control. */
	int32 LastObservedPlayingActIndex = INDEX_NONE;
#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYEntryLoopTestSeam;
	friend struct FDYFlowVerifyTestSeam;
#endif
};