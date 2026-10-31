#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Puppets/DYPuppetPerformanceTypes.h"
#include "DYPuppetPerformanceComponent.generated.h"

class USkeletalMeshComponent;
class ADYPuppetActor;

DECLARE_MULTICAST_DELEGATE_TwoParams(FDYPuppetPerformanceFinishedSignature, int32 /*ChapterIndex*/, bool /*bSkipped*/);

/**
 * Drives the authored shadow-puppet show on whichever skeletal mesh the puppet actor is
 * currently displaying. Pure presentation: it never reads puzzle state, never resolves an
 * act and never gates control. The Director decides when a show starts and resumes its own
 * notification once the show reports finished.
 */
UCLASS(ClassGroup = (DY), meta = (BlueprintSpawnableComponent))
class DENGYINGSHANHAI_API UDYPuppetPerformanceComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UDYPuppetPerformanceComponent();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Returns false when this chapter has no authored show (the Director then behaves exactly as before). */
	UFUNCTION(BlueprintCallable, Category = "DY|Performance")
	bool StartChapterPerformance(int32 ChapterIndex);

	/** One short reaction clip. Ignored while the full show owns the mesh or when the chapter has none. */
	void TriggerFeedback(int32 ChapterIndex);

	/** Ends the running show at its final beat; identical end state to watching it through. */
	UFUNCTION(BlueprintCallable, Category = "DY|Performance")
	void SkipPerformance();

	/** Releases cosmetic playback for a reset/chapter change without publishing completion. */
	void CancelPlayback();

	/** Pose updates must wait until both reaction clips and full shows release the mesh. */
	bool OwnsAnimation() const { return bPerforming || bFeedbackActive; }

	UFUNCTION(BlueprintPure, Category = "DY|Performance")
	bool IsPerforming() const { return bPerforming; }
	int32 GetPerformingChapter() const { return PerformingChapter; }
	bool HasChapter(int32 ChapterIndex) const;
	float GetPerformanceProgress() const;

	/** Used by the skip input, which must work without a Director reference. */
	static bool SkipAnyPerformanceInWorld(UWorld* World);

	FDYPuppetPerformanceFinishedSignature OnPerformanceFinished;

private:
	void ResolveData();
	void PlaySegment(int32 InSegmentIndex);
	void ShowCaption(const FText& Caption);
	void SetHudPerformanceActive(bool bActive);
	void Finish(bool bSkipped);
	void PlayOnMesh(const FDYPerformanceSegment& Segment, bool bForceLoop);
	void RestorePose();
	ADYPuppetActor* GetPuppetOwner() const;
	USkeletalMeshComponent* GetTargetMesh() const;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance", meta = (AllowPrivateAccess = "true"))
	TSoftObjectPtr<UDYPuppetPerformanceData> PerformanceData;

	UPROPERTY(Transient)
	TObjectPtr<UDYPuppetPerformanceData> ResolvedData;

	UPROPERTY(Transient)
	TArray<FDYPerformanceSegment> ActiveSegments;

	UPROPERTY(Transient)
	TArray<FDYPerformanceSegment> ActiveFeedback;

	FTimerHandle FeedbackHandle;
	int32 FeedbackCursor = 0;
	int32 PerformingChapter = INDEX_NONE;
	int32 SegmentIndex = INDEX_NONE;
	float SegmentElapsed = 0.f;
	float ElapsedSeconds = 0.f;
	float TotalSeconds = 0.f;
	bool bPerforming = false;
	bool bFeedbackActive = false;
	bool bRestoreAnimationBlueprint = false;
	TWeakObjectPtr<USkeletalMeshComponent> PlaybackMesh;
};