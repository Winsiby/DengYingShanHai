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

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle")
	UDYPuzzleEvaluatorComponent* GetEvaluatorComponent() const { return Evaluator; }

	UFUNCTION(BlueprintPure, Category = "DY|Puzzle")
	double GetEvaluationFrequencyHz() const { return EvaluationFrequencyHz; }

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
	void UpdateDevelopmentDebug(const FDYEvaluationResult& Result);
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
	bool bAcceptingManualStart = false;

	UPROPERTY(Transient)
	int32 CurrentActIndex = INDEX_NONE;
	UPROPERTY(Transient)
	EDYActSequencePhase SequencePhase = EDYActSequencePhase::Inactive;
	TWeakObjectPtr<ADYStagePresentation> SequencePresentation;
	FDYActSequenceChangedSignature ActSequenceChanged;
	bool bBroadcastingResolve = false;
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
	bool bSequenceActivationDeferred = false;

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

#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYResolvedSnapshotTestSeam;
	friend struct FDYActSequenceTestSeam;
	friend struct FDYEntryLoopTestSeam;
#endif
};
