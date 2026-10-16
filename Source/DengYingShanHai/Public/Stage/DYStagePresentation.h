#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Puzzles/DYPuzzleTypes.h"
#include "Puzzles/DYActSequenceTypes.h"
#include "Stage/DYStageEnvironment.h"
#include "Stage/DYStageFeedbackTypes.h"
#include "Stage/DYStaffPresentationTypes.h"
#include "DYStagePresentation.generated.h"

class ADYPuzzleDirector;
class ADYStageGameMode;
class AStaticMeshActor;
class ADYForestPresentationActor;

/** Native cosmetic notification. Carries no answer data. */
DECLARE_MULTICAST_DELEGATE_OneParam(FDYStageFeedbackDisplayChangedSignature, EDYStageFeedbackDisplay);
DECLARE_MULTICAST_DELEGATE_OneParam(FDYStaffContactAcceptedSignature, const FDYStaffContactPresentationSnapshot&);
DECLARE_MULTICAST_DELEGATE_OneParam(FDYPlayerActDisplayChangedSignature, const FDYActSequenceSnapshot&);
DECLARE_MULTICAST_DELEGATE_OneParam(FDYPlayerAlignmentDisplayChangedSignature, const FDYPlayerAlignmentDisplay&);

/**
 * Event-driven boundary between authoritative puzzle facts and authored stage presentation.
 * The native base owns safe binding, late-listener synchronization and environment mapping;
 * its Blueprint child owns only audiovisual responses to the finite state events below.
 */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYStagePresentation : public AActor
{
	GENERATED_BODY()

public:
	ADYStagePresentation();

	/** Re-query current Director state after binding or explicit runtime reconfiguration. */
	UFUNCTION(BlueprintCallable, Category = "DY|Stage Presentation")
	void SynchronizeFromDirector();

	/** Empty before a live Resolve, after invalidation, or when this opt-in is disabled. */
	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation|Staff")
	FDYStageResolvedPresentationSnapshot GetResolvedStaffPresentationSnapshot() const;

	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation|Staff")
	FDYStaffContactPresentationSnapshot GetStaffContactPresentationSnapshot() const;

	/**
	 * Authored animation contact callback. Reads actual A-end geometry; a caller cannot
	 * self-report a successful location. Cosmetic only; does not resolve/finish a puzzle.
	 */
	UFUNCTION(BlueprintCallable, Category = "DY|Stage Presentation|Staff")
	bool TryAcceptStaffContact(const FGuid& Token);

	/** Cosmetic resource creation only, after actual A contact with a current token. */
	UFUNCTION(BlueprintCallable, Category = "DY|Stage Presentation|Forest")
	bool BeginForestPresentation(const FGuid& Token);

	/** Authored normalized progress; no seconds, puzzle judgment or finale completion. */
	UFUNCTION(BlueprintCallable, Category = "DY|Stage Presentation|Forest")
	bool SetForestNormalizedGrowth(const FGuid& Token, double Progress);

	/** Clear this resource session only. NOT Skip, R, RestartExperience or FinishFinale. */
	UFUNCTION(BlueprintCallable, Category = "DY|Stage Presentation|Forest")
	bool ClearForestPresentation(const FGuid& Token);

	/** Final authored cue callback: native checks actual contact and full live branch geometry.
	 * A resolved Token alone never authorizes experience completion. Legacy single puzzles
	 * have no experience sequence to finish, so this opt-in call returns false there.
	 */
	UFUNCTION(BlueprintCallable, Category = "DY|Stage Presentation|Act Sequence")
	bool SubmitForestFinaleCompletion(const FGuid& Token);

	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation|Player Feedback")
	FDYActSequenceSnapshot GetPlayerActDisplay() const { return PlayerActDisplay; }

	FDYPlayerActDisplayChangedSignature& OnPlayerActDisplayChanged() { return PlayerActDisplayChanged; }

	/** Default-off, passive readiness and hold-clock projection. No answer data. */
	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation|Player Feedback")
	FDYPlayerAlignmentDisplay GetPlayerAlignmentDisplay() const;
	FDYPlayerAlignmentDisplayChangedSignature& OnPlayerAlignmentDisplayChanged() { return PlayerAlignmentDisplayChanged; }
	static FDYPlayerAlignmentDisplay BuildPlayerAlignmentDisplay(const FDYEvaluationResult& Result, bool bEnabled);

	/** Actual configured cosmetic resource, read-only; does not discover or authorize it. */
	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation|Forest")
	ADYForestPresentationActor* GetForestPresentationActor() const;

	/** Real Director identity invalidation only. Repeated/late old tokens must not clear a new cue. */
	UFUNCTION(BlueprintImplementableEvent, Category = "DY|Stage Presentation|Staff")
	void ReceiveStaffPresentationInvalidated(const FGuid& Token);

	FDYStaffContactAcceptedSignature& OnStaffContactAccepted() { return StaffContactAccepted; }

	UFUNCTION(BlueprintImplementableEvent, Category = "DY|Stage Presentation|Staff")
	void ReceiveStaffContactAccepted(const FDYStaffContactPresentationSnapshot& Contact);

	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation")
	ADYPuzzleDirector* GetPuzzleDirector() const { return PuzzleDirector; }

	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation")
	ADYStageEnvironment* GetStageEnvironment() const { return StageEnvironment; }

	/** Default-off: only the separate EnvironmentStates Dev map opts into five-state projection. */
	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation|Environment")
	bool IsFiveStateEnvironmentEnabled() const { return bEnableFiveStateDevEnvironment; }

	/** Cosmetic pure projection; never mutates or authorizes the authoritative sequence. */
	static EDYStageEnvironmentState MapSequenceToEnvironment(const FDYActSequenceSnapshot& Snapshot);

	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation")
	EDYStageEnvironmentState GetResolvedEnvironmentState() const { return ResolvedEnvironmentState; }

	/**
	 * The state a Dev readout should currently show. This is a presentation snapshot,
	 * not puzzle truth: it never contains a target, a tolerance or a progress value.
	 */
	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation")
	EDYStageFeedbackDisplay GetFeedbackDisplay() const
	{
		return IsDevFeedbackEnabledForWorld(GetWorld()) ? FeedbackDisplay : EDYStageFeedbackDisplay::Hidden;
	}

	/** Public cosmetic snapshot. Never contains targets, tolerance or numeric progress. */
	UFUNCTION(BlueprintPure, Category = "DY|Stage Presentation|Player Feedback")
	EDYStageFeedbackDisplay GetPlayerFeedbackDisplay() const { return FeedbackDisplay; }

	FDYStageFeedbackDisplayChangedSignature& OnPlayerFeedbackDisplayChanged() { return PlayerFeedbackDisplayChanged; }

	/** Native listener hook for the Dev HUD. Not a Blueprint entry point. */
	FDYStageFeedbackDisplayChangedSignature& OnFeedbackDisplayChanged() { return FeedbackDisplayChanged; }

	/** Blueprint cue hook; never used to decide puzzle truth. */
	UFUNCTION(BlueprintImplementableEvent, Category = "DY|Stage Presentation")
	void ReceivePuzzleActivated(FName PuzzleId);

	/** Emitted only when the finite feedback state changes, not at the 15 Hz sample cadence. */
	UFUNCTION(BlueprintImplementableEvent, Category = "DY|Stage Presentation")
	void ReceiveFeedbackStateChanged(
		FName PuzzleId,
		EDYPuzzleFeedbackState PreviousState,
		EDYPuzzleFeedbackState NewState,
		double Progress);

	UFUNCTION(BlueprintImplementableEvent, Category = "DY|Stage Presentation")
	void ReceiveHoldStarted(FName PuzzleId);

	UFUNCTION(BlueprintImplementableEvent, Category = "DY|Stage Presentation")
	void ReceiveHoldCanceled(FName PuzzleId);

	UFUNCTION(BlueprintImplementableEvent, Category = "DY|Stage Presentation")
	void ReceivePuzzleResolved(FName PuzzleId, const FDYEvaluationResult& ResolvedSnapshot);

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	void BindDirector();
	void UnbindDirector();

	/** Registers explicitly with this world's GameMode for public player UI. */
	void RegisterWithGameMode();

	/** True only in a non-Shipping build inside the Dev content tree. */
	static bool IsDevFeedbackEnabledForWorld(const UWorld* World);

	/** Recomputes the baseline (Adjust/Near/Holding) from a finite puzzle state. */
	void UpdateBaselineDisplay(EDYPuzzleFeedbackState FeedbackState);
	void SetFeedbackDisplay(EDYStageFeedbackDisplay NewDisplay);
	void SetPlayerAlignmentDisplay(const FDYPlayerAlignmentDisplay& Snapshot);

	/** Overlays Interrupted for the shared prototype presentation duration. */
	void ShowInterruptedTemporarily();

	/** Ends the interrupted overlay and restores the baseline immediately. */
	void ClearInterruptedOverlay();

	/** Stops any pending one-shot and clears both transient and baseline display. */
	void ResetFeedbackDisplay();
	void ApplyActivatedPresentation(FName PuzzleId);
	void ApplyResolvedPresentation(FName PuzzleId, const FDYEvaluationResult& ResolvedSnapshot);
	void ResetStaffPresentation();
	void CaptureResolvedStaffPresentation(FName PuzzleId);
	bool IsStaffPresentationTokenCurrent(const FGuid& Token) const;
	void ResetForestPresentation();
	void HandleResolvedSnapshotInvalidated(const FGuid& Token);
	bool IsContactSceneUnchanged() const;
	bool HasCompletedForestForToken(const FGuid& Token) const;
	void HandleActSequenceChanged(const FDYActSequenceSnapshot& Snapshot);
	void ScheduleActTransition();
	void CancelActTransition();
	bool IsSequenceOperationCurrent(const FGuid& Token) const;
	bool IsIncomingPuzzleNotificationCurrent() const;
	void ApplyEvaluationPresentation(const FDYEvaluationResult& Result);
	void ApplyFiveStateEnvironment(const FDYActSequenceSnapshot& Snapshot);

	UFUNCTION()
	void HandlePuzzleActivated(FName PuzzleId);

	UFUNCTION()
	void HandleEvaluationUpdated(const FDYEvaluationResult& Result);

	UFUNCTION()
	void HandleHoldStarted(FName PuzzleId);

	UFUNCTION()
	void HandleHoldCanceled(FName PuzzleId);

	UFUNCTION()
	void HandlePuzzleResolved(FName PuzzleId, const FDYEvaluationResult& ResolvedSnapshot);

	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "DY|Stage Presentation", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<ADYPuzzleDirector> PuzzleDirector;

	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "DY|Stage Presentation", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<ADYStageEnvironment> StageEnvironment;

	UPROPERTY(EditInstanceOnly, Category = "DY|Stage Presentation|Environment")
	bool bEnableFiveStateDevEnvironment = false;

	/** Default-off: existing M1/M2 assets keep their accepted presentation behavior. */
	UPROPERTY(EditInstanceOnly, Category = "DY|Stage Presentation|Staff")
	bool bEnableStaffContactPresentation = false;

	UPROPERTY(EditInstanceOnly, Category = "DY|Stage Presentation|Staff", meta = (EditCondition = "bEnableStaffContactPresentation"))
	TObjectPtr<AStaticMeshActor> StaffProjectionScreen;

	/** Position must be on the emitter-facing receiver face; no implicit ground Z. */
	UPROPERTY(EditInstanceOnly, Category = "DY|Stage Presentation|Staff", meta = (EditCondition = "bEnableStaffContactPresentation"))
	TObjectPtr<AActor> NarrativeGroundLine;

	/** Optional explicit reference. Existing M2 assets remain null and unchanged. */
	UPROPERTY(EditInstanceOnly, Category = "DY|Stage Presentation|Staff", meta = (EditCondition = "bEnableStaffContactPresentation"))
	TObjectPtr<ADYForestPresentationActor> ForestPresentationActor;

	TWeakObjectPtr<ADYForestPresentationActor> OwnedForestActor;
	FGuid OwnedForestToken;
	TWeakObjectPtr<ADYPuzzleDirector> InvalidationDirector;
	FDelegateHandle ResolvedInvalidationHandle;
	FDelegateHandle ActSequenceHandle;
	FTimerHandle ActTransitionTimerHandle;
	FGuid PendingTransitionToken;
	UPROPERTY(Transient)
	FDYActSequenceSnapshot PlayerActDisplay;
	FDYPlayerActDisplayChangedSignature PlayerActDisplayChanged;
	/** New Dev instance opt-in; accepted old maps retain their original HUD. */
	UPROPERTY(EditInstanceOnly, Category = "DY|Stage Presentation|Player Feedback")
	bool bEnablePlayerAlignmentFeedback = false;
	UPROPERTY(Transient) FDYPlayerAlignmentDisplay PlayerAlignmentDisplay;
	FDYPlayerAlignmentDisplayChangedSignature PlayerAlignmentDisplayChanged;

	/** Approved Dev candidate only, independent from holding/15 Hz evaluation. */
	UPROPERTY(EditAnywhere, Category = "DY|Stage Presentation|Act Sequence", meta = (ClampMin = "0.1", Units = "s"))
	float DevActTransitionSeconds = 2.0f;

	UPROPERTY(Transient)
	FDYStageResolvedPresentationSnapshot ResolvedStaffPresentation;

	UPROPERTY(Transient)
	FDYStaffContactPresentationSnapshot StaffContactPresentation;

	bool bStaffPresentationRuntimeActive = false;
	FDYStaffContactAcceptedSignature StaffContactAccepted;

	/** Authored mapping from this puzzle's resolved fact to one environment presentation state. */
	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category = "DY|Stage Presentation", meta = (AllowPrivateAccess = "true"))
	EDYStageEnvironmentState ResolvedEnvironmentState = EDYStageEnvironmentState::SunAwakened;

	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Transient, Category = "DY|Stage Presentation", meta = (AllowPrivateAccess = "true"))
	EDYPuzzleFeedbackState LastForwardedFeedback = EDYPuzzleFeedbackState::InvalidSample;

	bool bHasForwardedFeedback = false;

	/**
	 * Shared prototype UI timing, not puzzle truth or a final art decision.
	 * Legacy serialized property name is retained to preserve existing map overrides.
	 */
	UPROPERTY(EditAnywhere, Category = "DY|Stage Presentation|Dev Feedback", meta = (AllowPrivateAccess = "true", ClampMin = "0.1", Units = "s"))
	float DevInterruptedDisplaySeconds = 1.2f;

	/** The steady state the readout returns to once no transient override is active. */
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Transient, Category = "DY|Stage Presentation|Dev Feedback", meta = (AllowPrivateAccess = "true"))
	EDYStageFeedbackDisplay FeedbackBaseline = EDYStageFeedbackDisplay::Hidden;

	/** What the readout should show right now, baseline or transient override. */
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Transient, Category = "DY|Stage Presentation|Dev Feedback", meta = (AllowPrivateAccess = "true"))
	EDYStageFeedbackDisplay FeedbackDisplay = EDYStageFeedbackDisplay::Hidden;

	FDYStageFeedbackDisplayChangedSignature FeedbackDisplayChanged;
	FDYStageFeedbackDisplayChangedSignature PlayerFeedbackDisplayChanged;

	FTimerHandle DevInterruptedTimerHandle;

#if WITH_DEV_AUTOMATION_TESTS
	/** Test-only access to the private handlers. No public API is added for testing. */
	friend struct FDYStageFeedbackTestSeam;
	friend struct FDYStaffContactTestSeam;
	friend struct FDYActSequenceTestSeam;
	friend struct FDYAlignmentFeedbackTestSeam;
#endif
};
