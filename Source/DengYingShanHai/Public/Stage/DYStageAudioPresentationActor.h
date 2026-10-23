#pragma once

#include "CoreMinimal.h"
#include "AudioDeviceHandle.h"
#include "GameFramework/Actor.h"
#include "Puzzles/DYActSequenceTypes.h"
#include "Stage/DYStageFeedbackTypes.h"
#include "Stage/DYStaffPresentationTypes.h"
#include "DYStageAudioPresentationActor.generated.h"

class ADYStagePresentation;
class UAudioComponent;
class USceneComponent;
class USoundBase;
class UReverbEffect;

/** Desired cosmetic voices, never puzzle truth. */
struct FDYStageAudioPlan
{
	bool bAmbient = false;
	bool bHolding = false;
	bool bLeaves = false;
	bool bResolveOneShot = false;
};

/** Per-world cosmetic de-duplication only; contains no target, hold clock or geometry. */
struct DENGYINGSHANHAI_API FDYStageAudioGate
{
	FDYStageAudioPlan Observe(const FDYActSequenceSnapshot& Sequence, EDYStageFeedbackDisplay Feedback, bool bAllowOneShot);
	bool AcceptContact(const FDYStaffContactPresentationSnapshot& Notification,
		const FDYStaffContactPresentationSnapshot& Current, const FDYActSequenceSnapshot& Sequence);
	void Reset();
private:
	TSet<int32> ResolvedActCues;
	FGuid LastContactCue;
	int32 LastObservedChapterIndex = INDEX_NONE;
	int32 LastObservedActIndex = INDEX_NONE;
	EDYActSequencePhase LastObservedPhase = EDYActSequencePhase::Inactive;
};

USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYStageAudioDiagnostics
{
	GENERATED_BODY()
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") bool bRuntimeActive = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") bool bMuted = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") bool bTheatreReverbActive = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") bool bAmbientDesired = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") bool bHoldingDesired = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") bool bLeavesDesired = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") int32 HoldStarts = 0;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") int32 HoldStops = 0;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") int32 ResolveCues = 0;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") int32 ContactCues = 0;
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") int32 ForestStarts = 0;
	/** Voice requests are not proof of audible OS output. */
	UPROPERTY(BlueprintReadOnly, Category="DY|Audio") int32 PlaybackStarts = 0;
};

/**
 * Explicitly placed local sound-emission entity. Consumes the existing Stage's passive
 * snapshots/contact notification; never reads Director, drives input, or advances gameplay.
 */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYStageAudioPresentationActor : public AActor
{
	GENERATED_BODY()
public:
	ADYStageAudioPresentationActor();
	UFUNCTION(BlueprintPure, Category="DY|Audio") FDYStageAudioDiagnostics GetAudioDiagnostics() const;
	/** Dev validation seam, not a settings system or a new player key. */
	UFUNCTION(BlueprintCallable, Category="DY|Audio") void SetMuted(bool bNewMuted);
	UPROPERTY(EditInstanceOnly, Category="DY|Audio") bool bEnableDevelopmentAudio = false;
	/** Native shared-device room colour. Dev candidate, not measured theatre acoustics. */
	UPROPERTY(EditInstanceOnly, Category="DY|Audio") bool bEnableTheatreReverb = false;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio", meta=(ClampMin="0.1",ClampMax="20")) float TheatreDecaySeconds = 2.4f;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio") TObjectPtr<ADYStagePresentation> StagePresentation;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio") TObjectPtr<USoundBase> WindSound;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio") TObjectPtr<USoundBase> HoldingSound;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio") TObjectPtr<USoundBase> ResolveSound;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio") TObjectPtr<USoundBase> ContactSound;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio") TObjectPtr<USoundBase> LeavesSound;
	/** PCM assets carry a bounded mix gain; these are optional instance trims. */
	UPROPERTY(EditInstanceOnly, Category="DY|Audio", meta=(ClampMin="0",ClampMax="1")) float WindVolume = 1.0f;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio", meta=(ClampMin="0",ClampMax="1")) float HoldingVolume = 1.0f;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio", meta=(ClampMin="0",ClampMax="1")) float ResolveVolume = 1.0f;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio", meta=(ClampMin="0",ClampMax="1")) float ContactVolume = 1.0f;
	UPROPERTY(EditInstanceOnly, Category="DY|Audio", meta=(ClampMin="0",ClampMax="1")) float LeavesVolume = 1.0f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="DY|Audio") TObjectPtr<UAudioComponent> AmbientVoice;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="DY|Audio") TObjectPtr<UAudioComponent> HoldingVoice;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="DY|Audio") TObjectPtr<UAudioComponent> ResolveVoice;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="DY|Audio") TObjectPtr<UAudioComponent> ContactVoice;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="DY|Audio") TObjectPtr<UAudioComponent> LeavesVoice;
protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
private:
	void Refresh(bool bAllowOneShot);
	void HandleActChanged(const FDYActSequenceSnapshot& Snapshot);
	void HandleFeedbackChanged(EDYStageFeedbackDisplay Feedback);
	void HandleAlignmentChanged(const FDYPlayerAlignmentDisplay& Snapshot);
	UFUNCTION() void HandleStageEndPlay(AActor* Actor, EEndPlayReason::Type Reason);
	void DeactivateAudioSession();
	void HandleContactAccepted(const FDYStaffContactPresentationSnapshot& Contact);
	bool HasLiveStage() const;
	void ApplyLoop(UAudioComponent* Voice, bool bDesired, bool& bPrevious, float Volume);
	void PlayOneShot(UAudioComponent* Voice, float Volume, const TCHAR* Kind);
	void StopAllVoices();
	void ActivateTheatreReverb();
	void DeactivateTheatreReverb();
	UPROPERTY(Transient) TObjectPtr<UReverbEffect> TheatreReverb;
	FName TheatreReverbTag;
	FAudioDeviceHandle TheatreAudioDevice;
	UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> SceneRoot;
	UPROPERTY(Transient) FDYStageAudioDiagnostics Diagnostics;
	TWeakObjectPtr<ADYStagePresentation> BoundStage;
	FDelegateHandle ActHandle;
	FDelegateHandle FeedbackHandle;
	FDelegateHandle ContactHandle;
	FDelegateHandle AlignmentHandle;
	FDYStageAudioGate CueGate;
#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYStageAudioTestSeam;
#endif
};
