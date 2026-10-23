#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Puzzles/DYPuzzleTypes.h"
#include "Puzzles/DYResolvedPuzzleSnapshot.h"
#include "Puzzles/DYActSequenceTypes.h"
#include "DYPuzzleDirector.generated.h"

class ADYLightRigActor;
class ADYPuppetActor;
class UDYPuzzleDefinition;
class UDYPuzzleEvaluatorComponent;
class ADYStagePresentation;
class ADYDevEntryPlayerController;
class UMaterialInstanceDynamic;
class AExponentialHeightFog;
class UDYPuppetPerformanceComponent;

/** Notification only: fact is already invalid before any listener runs. */
DECLARE_MULTICAST_DELEGATE_OneParam(FDYResolvedSnapshotInvalidatedSignature, const FGuid&);
DECLARE_MULTICAST_DELEGATE_OneParam(FDYActSequenceChangedSignature, const FDYActSequenceSnapshot&);

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FDYEvaluationUpdatedSignature, const FDYEvaluationResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FDYPuzzleIdSignature, FName, PuzzleId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
	FDYPuzzleResolvedSignature,
	FName, PuzzleId,
	const FDYEvaluationResult&, ResolvedSnapshot);

UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYPuzzleDirector : public AActor
{
	GENERATED_BODY()

public:
	ADYPuzzleDirector();

	UFUNCTION(BlueprintCallable, Category = "DY|Puzzle")
	void StartCurrentPuzzle();

	UFUNCTION(BlueprintCallable, Category = "DY|Puzzle")
	void ResetCurrentPuzzle();

	UFUNCTION(BlueprintCallable, Category = "DY|Puzzle")
	void EvaluatePuzzleNow();

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle")
	FDYEvaluationResult GetLastEvaluation() const;

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle")
	FName GetCurrentPuzzleId() const;

	/** Empty authored sequence preserves the accepted single-puzzle behavior. */
	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Act Sequence")
	bool IsActSequenceEnabled() const { return !ActSequence.IsEmpty(); }

	/** Legacy maps still auto-start. Only the independent entry-loop Dev map opts out. */
	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Act Sequence")
	bool IsAutoStartOnBeginPlay() const { return bAutoStartOnBeginPlay; }

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Act Sequence")
	bool IsFinalSequenceAct() const;

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Act Sequence")
	FDYActSequenceSnapshot GetActSequenceSnapshot() const;

	/** Four-act campaign. Chapter 0 replays the authored ActSequence; later chapters are built at runtime. */
	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Campaign")
	int32 GetChapterCount() const;

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Campaign")
	int32 GetCurrentChapterIndex() const { return CurrentChapterIndex; }

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Campaign")
	FText GetChapterTitle(int32 ChapterIndex) const;

	/** Menu browse list; static so the entry widget never needs a live Director. */
	static const TArray<FText>& GetCampaignChapterTitles();

	FDYActSequenceChangedSignature& OnActSequenceChanged() { return ActSequenceChanged; }

	/** Read-only value copy; empty until Resolve, or after reset/teardown. */
	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Resolved Snapshot")
	FDYResolvedPuzzleSnapshot GetResolvedPuzzleSnapshot() const;

	/** Identity check only. Does not finish a cue, grow a forest, or decide success. */
	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Resolved Snapshot")
	bool IsResolvedTokenCurrent(const FGuid& Token) const;

	FDYResolvedSnapshotInvalidatedSignature& OnResolvedSnapshotInvalidated() { return ResolvedSnapshotInvalidated; }

	/** Actual configured actors, not a world-discovered substitute. Read-only access. */
	UFUNCTION(BlueprintPure, Category = "DY|Puzzle")
	ADYLightRigActor* GetLightRigActor() const { return LightRig; }

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle")
	ADYPuppetActor* GetPuppetActor() const { return PuppetActor; }

	/** Swaps only the plaque material; no judgement, timing or control path reads it. */
	UFUNCTION(BlueprintCallable, Category = "DY|Puzzle|Campaign")
	void ApplyChapterTitlePlaque(int32 ChapterIndex);

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle")
	UDYPuzzleEvaluatorComponent* GetEvaluatorComponent() const { return Evaluator; }

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle")
	double GetEvaluationFrequencyHz() const { return EvaluationFrequencyHz; }

	/**
	 * Pure reach-guidance copy. Empty when the player can already act on every part this
	 * act requires; otherwise the line names what is still out of reach. No world access,
	 * so automation can pin the rule without spawning actors.
	 */
	static FText MakeReachHint(bool bLightInReach, bool bPuppetRequired, bool bPuppetInReach);

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Development")
	bool IsDevelopmentDebugEnabled() const { return bShowDevelopmentDebug; }

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle|Development")
	double GetDevelopmentDebugRefreshIntervalSeconds() const { return DevelopmentDebugRefreshIntervalSeconds; }

	UPROPERTY(BlueprintAssignable, Category = "DY|Puzzle")
	FDYEvaluationUpdatedSignature OnEvaluationUpdated;

	/** Emitted after the authored references are valid and mutable puzzle state is reset. */
	UPROPERTY(BlueprintAssignable, Category = "DY|Puzzle")
	FDYPuzzleIdSignature OnPuzzleActivated;

	UPROPERTY(BlueprintAssignable, Category = "DY|Puzzle")
	FDYPuzzleIdSignature OnHoldStarted;

	UPROPERTY(BlueprintAssignable, Category = "DY|Puzzle")
	FDYPuzzleIdSignature OnHoldCanceled;

	UPROPERTY(BlueprintAssignable, Category = "DY|Puzzle")
	FDYPuzzleResolvedSignature OnPuzzleResolved;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	friend class ADYStagePresentation;
	friend class ADYDevEntryPlayerController;
	bool CanStartManualSequence(const ADYStagePresentation* Requester) const;
	bool StartManualSequence(ADYStagePresentation* Requester);
	bool ValidateActSequence() const;
	/** Exposed so editor checks can drive the same chapter path the entry flow uses. */
	UFUNCTION(BlueprintCallable, Category = "DY|Puzzle|Campaign")
	bool StartCampaignChapter(int32 ChapterIndex, ADYStagePresentation* Requester);
	void EnsureCampaignChapters();
	void ApplyChapterPalette();
	void AdvanceCampaignChapter();
	void ScheduleCampaignChapterFallback();
	void HandleCampaignChapterTimeout();
	void HandleCampaignAutoPlayTick();
	void ProbeCampaignPhase(const TCHAR* Where) const;
	bool IsCampaignEnabled() const { return bFourActCampaign && Chapters.Num() > 1; }
	bool RegisterSequencePresentation(ADYStagePresentation* Presentation);
	void UnregisterSequencePresentation(ADYStagePresentation* Presentation);
	/** Native trusted presentation boundary; no public Blueprint bypass of visual completion. */
	bool AcceptActTransition(ADYStagePresentation* Presentation, const FGuid& Token);
	bool AcceptFinaleCompletion(ADYStagePresentation* Presentation, const FGuid& Token);
	bool IsSequenceSubmissionCurrent(const ADYStagePresentation* Presentation, const FGuid& Token,
		EDYActSequencePhase RequiredPhase) const;
	void SetSequencePhase(EDYActSequencePhase NewPhase);
	bool AreSequenceActorsReady() const;
	void ScheduleEvaluation();
	void StopEvaluation();
	/** Cosmetic guidance only: it never feeds evaluation or phase state. */
	void UpdateReachHint(double DeltaSeconds);
	void PublishReachHint(const FText& Hint);
	/** Verification-only file probe (DY_CARRY_PROBE); never feeds evaluation or phases. */
	void ProbeCarriedEntryValues(bool bCarried);
	void UpdateDevelopmentDebug(const FDYEvaluationResult& Result);

	/** Chapter show playback is presentation only: the judge result is already frozen
	 *  when a show starts, and this class publishes the same resolution after it ends. */
	void BindPuppetPerformance();
	void HandlePuppetPerformanceFinished(int32 ChapterIndex, bool bSkipped);
	void PublishResolvedSequence();
	/** Short reaction clip for crossing a progress band; never changes judgement. */
	void TriggerProgressFeedback(double Progress);
	bool CurrentPuzzleRequiresPuppet() const;
	uint64 InvalidateResolvedSnapshot();
	void CaptureResolvedSnapshot(const FDYEvaluationResult& Result);

	UFUNCTION()
	void HandleControlResetRequested();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puzzle", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UDYPuzzleEvaluatorComponent> Evaluator;

	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "DY|Puzzle", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<ADYLightRigActor> LightRig;

	/** Required only when the active definition uses puppet position or pose. */
	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "DY|Puzzle", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<ADYPuppetActor> PuppetActor;

	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "DY|Puzzle", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UDYPuzzleDefinition> PuzzleDefinition;

	/** Opt-in only. Exactly three valid, distinct, explicit definitions in this Dev version. */
	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "DY|Puzzle|Act Sequence", meta = (AllowPrivateAccess = "true"))
	TArray<FDYActSequenceEntry> ActSequence;

	UPROPERTY(EditInstanceOnly, Category = "DY|Puzzle|Act Sequence")
	bool bAutoStartOnBeginPlay = true;

	/** Four-act campaign opt-in. Authored per map instance; automation fixtures keep it off. */
	UPROPERTY(EditInstanceOnly, Category = "DY|Puzzle|Campaign")
	bool bFourActCampaign = false;

	/** Presentation only: the plaque above the screen names the current act. Empty falls back to the shipped instances. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle|Campaign", meta = (AllowPrivateAccess = "true"))
	TArray<TSoftObjectPtr<UMaterialInterface>> ChapterTitleMaterials;

	/** Within one chapter the next act starts from the previous act's authored Target when that
	 * parameter was authored there. Chapter boundaries and explicit resets still return to .15.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle|Campaign", meta = (AllowPrivateAccess = "true"))
	bool bCarryControlValuesAcrossActs = true;
	bool bCarryEntryValuesOnNextStart = false;
	bool bAcceptingManualStart = false;

	UPROPERTY(Transient)
	TWeakObjectPtr<AActor> TitleGlyphActor;
	UPROPERTY(Transient)
	int32 CurrentActIndex = INDEX_NONE;
	UPROPERTY(Transient)
	EDYActSequencePhase SequencePhase = EDYActSequencePhase::Inactive;
	TWeakObjectPtr<ADYStagePresentation> SequencePresentation;
	FDYActSequenceChangedSignature ActSequenceChanged;
	bool bBroadcastingResolve = false;

	/** Resolution already frozen but its notification waits for the chapter show. */
	bool bResolveNotificationDeferred = false;
	FDYEvaluationResult DeferredResolveResult;
	FName DeferredResolvePuzzleId;
	FGuid DeferredResolveToken;
	int32 LastFeedbackBand = 0;
	UPROPERTY(Transient)
	TWeakObjectPtr<UDYPuppetPerformanceComponent> BoundPerformanceComponent;
	/** Stack-local notification provenance, copied from the SAME activation identity.
	 * Not a second authority/token or a serialized gameplay fact. Nested events restore it.
	 */
	FGuid PuzzleNotificationToken;

	/** Accepted competition baseline; holding still accumulates real world time. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle|Development", meta = (AllowPrivateAccess = "true", ClampMin = "1.0", ClampMax = "60.0", Units = "Hz"))
	double EvaluationFrequencyHz = 15.0;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle|Development", meta = (AllowPrivateAccess = "true"))
	bool bShowDevelopmentDebug = false;

	/** Debug presentation refresh is deliberately independent from puzzle sampling. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle|Development", meta = (AllowPrivateAccess = "true", ClampMin = "0.1", Units = "s"))
	double DevelopmentDebugRefreshIntervalSeconds = 0.25;

	FTimerHandle EvaluationTimerHandle;
	FTimerHandle SequenceActivationTimerHandle;
	FTimerHandle CampaignChapterTimerHandle;
	FTimerHandle CampaignAutoPlayHandle;
	bool bCampaignAutoPlay = false;
	bool bSequenceActivationDeferred = false;

	/** Campaign state. Chapter 0 mirrors the authored ActSequence captured at BeginPlay. */
	UPROPERTY(Transient)
	TArray<FDYChapterEntry> Chapters;
	UPROPERTY(Transient)
	TArray<TObjectPtr<UDYPuzzleDefinition>> RuntimeDefinitions;
	UPROPERTY(Transient)
	TArray<FDYActSequenceEntry> BaseActSequence;
	UPROPERTY(Transient)
	int32 CurrentChapterIndex = 0;
	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> SkyInstance;
	UPROPERTY(Transient)
	TObjectPtr<AExponentialHeightFog> ExteriorFog;

	/** Runtime evidence only, never serialized into authored definitions or maps. */
	UPROPERTY(Transient)
	FDYResolvedPuzzleSnapshot ResolvedSnapshot;

	UPROPERTY(Transient)
	FGuid ActivationToken;

	FDYResolvedSnapshotInvalidatedSignature ResolvedSnapshotInvalidated;
	uint64 InvalidationSerial = 0;
	bool bEndingPlay = false;

	double LastEvaluationTimeSeconds = 0.0;
	double LastDevelopmentDebugTimeSeconds = -DBL_MAX;

	/** Reach guidance delay/duration; 0 delay disables the line. Reset by every act start. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle|Reach Hint", meta = (AllowPrivateAccess = "true", ClampMin = "0.0", Units = "s"))
	double ReachHintDelaySeconds = 6.0;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puzzle|Reach Hint", meta = (AllowPrivateAccess = "true", ClampMin = "0.5", Units = "s"))
	double ReachHintDurationSeconds = 6.0;
	double OutOfReachSeconds = 0.0;
	bool bReachHintShownThisAct = false;

#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYResolvedSnapshotTestSeam;
	friend struct FDYActSequenceTestSeam;
	friend struct FDYEntryLoopTestSeam;
#endif
};