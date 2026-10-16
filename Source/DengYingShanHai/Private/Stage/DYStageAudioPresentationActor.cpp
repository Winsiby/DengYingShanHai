#include "Stage/DYStageAudioPresentationActor.h"

#include "Components/AudioComponent.h"
#include "AudioDevice.h"
#include "Components/SceneComponent.h"
#include "DengYingShanHai.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/ReverbEffect.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Stage/DYStagePresentation.h"

FDYStageAudioPlan FDYStageAudioGate::Observe(const FDYActSequenceSnapshot& Sequence,
	const EDYStageFeedbackDisplay Feedback, const bool bAllowOneShot)
{
	FDYStageAudioPlan Plan;
	const bool bActive = Sequence.bSequenceEnabled && Sequence.ActCount > 0
		&& Sequence.ActIndex >= 0 && Sequence.ActIndex < Sequence.ActCount
		&& Sequence.Phase != EDYActSequencePhase::Inactive;
	Plan.bAmbient = bActive;
	Plan.bHolding = bActive && Sequence.Phase == EDYActSequencePhase::Playing
		&& Feedback == EDYStageFeedbackDisplay::Holding;
	Plan.bLeaves = bActive && Sequence.Phase == EDYActSequencePhase::Complete;
	if (bActive && Sequence.Phase == EDYActSequencePhase::AwaitingTransition
		&& Sequence.ActIndex < Sequence.ActCount - 1 && !ResolvedActCues.Contains(Sequence.ActIndex))
	{
		ResolvedActCues.Add(Sequence.ActIndex);
		Plan.bResolveOneShot = bAllowOneShot; // Late bind consumes, but does not replay old impacts.
	}
	return Plan;
}

bool FDYStageAudioGate::AcceptContact(const FDYStaffContactPresentationSnapshot& Notification,
	const FDYStaffContactPresentationSnapshot& Current, const FDYActSequenceSnapshot& Sequence)
{
	if (!Sequence.bSequenceEnabled || Sequence.ActCount < 1 || Sequence.ActIndex != Sequence.ActCount - 1
		|| Sequence.Phase != EDYActSequencePhase::AwaitingFinale || !Notification.bHasContact
		|| !Current.bHasContact || !Current.Token.IsValid() || Notification.Token != Current.Token
		|| Current.Token == LastContactCue) { return false; }
	LastContactCue = Current.Token;
	return true;
}

void FDYStageAudioGate::Reset()
{
	ResolvedActCues.Reset();
	LastContactCue.Invalidate();
}

ADYStageAudioPresentationActor::ADYStageAudioPresentationActor()
{
	PrimaryActorTick.bCanEverTick = false;
	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);
	AmbientVoice = CreateDefaultSubobject<UAudioComponent>(TEXT("AmbientVoice"));
	HoldingVoice = CreateDefaultSubobject<UAudioComponent>(TEXT("HoldingVoice"));
	ResolveVoice = CreateDefaultSubobject<UAudioComponent>(TEXT("ResolveVoice"));
	ContactVoice = CreateDefaultSubobject<UAudioComponent>(TEXT("ContactVoice"));
	LeavesVoice = CreateDefaultSubobject<UAudioComponent>(TEXT("LeavesVoice"));
	for (UAudioComponent* Voice : {AmbientVoice.Get(), HoldingVoice.Get(), ResolveVoice.Get(), ContactVoice.Get(), LeavesVoice.Get()})
	{
		Voice->SetupAttachment(SceneRoot);
		Voice->bAutoActivate = false;
		Voice->bAutoDestroy = false;
		Voice->bStopWhenOwnerDestroyed = true;
		Voice->bAllowSpatialization = false; // Dev mix; no distance affects a cue's meaning.
	}
}

bool ADYStageAudioPresentationActor::HasLiveStage() const
{
	const ADYStagePresentation* Stage = BoundStage.Get();
	return Diagnostics.bRuntimeActive && IsValid(Stage) && Stage == StagePresentation
		&& Stage->GetWorld() == GetWorld();
}

void ADYStageAudioPresentationActor::BeginPlay()
{
	Super::BeginPlay();
	StopAllVoices();
	CueGate.Reset();
	Diagnostics = {};
	if (!bEnableDevelopmentAudio || !GetWorld() || !GetWorld()->IsGameWorld()
		|| !IsValid(StagePresentation) || StagePresentation->GetWorld() != GetWorld()) { return; }
	Diagnostics.bRuntimeActive = true;
	Diagnostics.bMuted = FParse::Param(FCommandLine::Get(), TEXT("DYAudioMuted"));
	AmbientVoice->SetSound(WindSound); HoldingVoice->SetSound(HoldingSound);
	ResolveVoice->SetSound(ResolveSound); ContactVoice->SetSound(ContactSound); LeavesVoice->SetSound(LeavesSound);
	BoundStage = StagePresentation;
	ActivateTheatreReverb();
	ActHandle = StagePresentation->OnPlayerActDisplayChanged().AddUObject(this, &ThisClass::HandleActChanged);
	FeedbackHandle = StagePresentation->OnPlayerFeedbackDisplayChanged().AddUObject(this, &ThisClass::HandleFeedbackChanged);
	ContactHandle = StagePresentation->OnStaffContactAccepted().AddUObject(this, &ThisClass::HandleContactAccepted);
	AlignmentHandle = StagePresentation->OnPlayerAlignmentDisplayChanged().AddUObject(this, &ThisClass::HandleAlignmentChanged);
	StagePresentation->OnEndPlay.AddDynamic(this, &ThisClass::HandleStageEndPlay);
	Refresh(false);
	const auto ExistingContact = BoundStage->GetStaffContactPresentationSnapshot();
	CueGate.AcceptContact(ExistingContact, ExistingContact, BoundStage->GetPlayerActDisplay()); // Consume late old impact silently.
}

void ADYStageAudioPresentationActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	DeactivateAudioSession();
	Super::EndPlay(EndPlayReason);
}

void ADYStageAudioPresentationActor::DeactivateAudioSession()
{
	Diagnostics.bRuntimeActive = false;
	DeactivateTheatreReverb();
	if (ADYStagePresentation* Stage = BoundStage.Get())
	{
		Stage->OnPlayerActDisplayChanged().Remove(ActHandle);
		Stage->OnPlayerFeedbackDisplayChanged().Remove(FeedbackHandle);
		Stage->OnStaffContactAccepted().Remove(ContactHandle);
		Stage->OnPlayerAlignmentDisplayChanged().Remove(AlignmentHandle);
		Stage->OnEndPlay.RemoveDynamic(this, &ThisClass::HandleStageEndPlay);
	}
	BoundStage.Reset(); ActHandle.Reset(); FeedbackHandle.Reset(); ContactHandle.Reset(); AlignmentHandle.Reset();
	StopAllVoices(); CueGate.Reset();
	Diagnostics.bAmbientDesired = Diagnostics.bHoldingDesired = Diagnostics.bLeavesDesired = false;
}

void ADYStageAudioPresentationActor::HandleStageEndPlay(AActor* Actor, const EEndPlayReason::Type Reason)
{
	if (Actor == BoundStage.Get()) { DeactivateAudioSession(); }
}

void ADYStageAudioPresentationActor::ApplyLoop(UAudioComponent* Voice, const bool bDesired,
	bool& bPrevious, const float Volume)
{
	if (bPrevious == bDesired) { return; }
	bPrevious = bDesired;
	if (bDesired && !Diagnostics.bMuted && IsValid(Voice) && IsValid(Voice->Sound))
	{
		++Diagnostics.PlaybackStarts;
		Voice->FadeIn(0.08f, FMath::Clamp(Volume, 0.f, 1.f));
	}
	else if (IsValid(Voice)) { Voice->Stop(); }
}

void ADYStageAudioPresentationActor::PlayOneShot(UAudioComponent* Voice, const float Volume, const TCHAR* Kind)
{
	if (!Diagnostics.bMuted && IsValid(Voice) && IsValid(Voice->Sound))
	{
		++Diagnostics.PlaybackStarts;
		Voice->SetVolumeMultiplier(FMath::Clamp(Volume, 0.f, 1.f));
		Voice->Play();
	}
	UE_LOG(LogDengYingShanHai, Log, TEXT("AudioDev Cue=%s Muted=%d PlaybackStarts=%d"), Kind, Diagnostics.bMuted, Diagnostics.PlaybackStarts);
}

void ADYStageAudioPresentationActor::Refresh(const bool bAllowOneShot)
{
	if (!HasLiveStage()) { DeactivateAudioSession(); return; }
	const auto Alignment = BoundStage->GetPlayerAlignmentDisplay();
	const auto Feedback = Alignment.bEnabled
		? (Alignment.bHolding ? EDYStageFeedbackDisplay::Holding : EDYStageFeedbackDisplay::Adjust)
		: BoundStage->GetPlayerFeedbackDisplay();
	const FDYStageAudioPlan Plan = CueGate.Observe(BoundStage->GetPlayerActDisplay(), Feedback, bAllowOneShot);
	if (Plan.bHolding != Diagnostics.bHoldingDesired)
	{
		if (Plan.bHolding) { ++Diagnostics.HoldStarts; } else { ++Diagnostics.HoldStops; }
	}
	if (Plan.bLeaves && !Diagnostics.bLeavesDesired) { ++Diagnostics.ForestStarts; }
	ApplyLoop(AmbientVoice, Plan.bAmbient, Diagnostics.bAmbientDesired, WindVolume);
	ApplyLoop(HoldingVoice, Plan.bHolding, Diagnostics.bHoldingDesired, HoldingVolume);
	ApplyLoop(LeavesVoice, Plan.bLeaves, Diagnostics.bLeavesDesired, LeavesVolume);
	if (Plan.bResolveOneShot) { ++Diagnostics.ResolveCues; PlayOneShot(ResolveVoice, ResolveVolume, TEXT("Resolve")); }
}

void ADYStageAudioPresentationActor::HandleActChanged(const FDYActSequenceSnapshot& Snapshot)
{
	// Read current passive view rather than accepting potentially stale reentrant notifications.
	Refresh(true);
}

void ADYStageAudioPresentationActor::HandleFeedbackChanged(const EDYStageFeedbackDisplay Feedback)
{
	Refresh(true);
}

void ADYStageAudioPresentationActor::HandleAlignmentChanged(const FDYPlayerAlignmentDisplay& Snapshot)
{
	// Ignore the 15 Hz hold-fraction updates. Only the existing finite Holding flag matters.
	if (Snapshot.bHolding != Diagnostics.bHoldingDesired) { Refresh(true); }
}

void ADYStageAudioPresentationActor::HandleContactAccepted(const FDYStaffContactPresentationSnapshot& Contact)
{
	if (!HasLiveStage()) { DeactivateAudioSession(); return; }
	if (CueGate.AcceptContact(Contact, BoundStage->GetStaffContactPresentationSnapshot(), BoundStage->GetPlayerActDisplay()))
	{
		++Diagnostics.ContactCues;
		PlayOneShot(ContactVoice, ContactVolume, TEXT("ActualStaffContact"));
	}
}

void ADYStageAudioPresentationActor::StopAllVoices()
{
	for (UAudioComponent* Voice : {AmbientVoice.Get(), HoldingVoice.Get(), ResolveVoice.Get(), ContactVoice.Get(), LeavesVoice.Get()})
	{
		if (IsValid(Voice)) { Voice->Stop(); }
	}
}

void ADYStageAudioPresentationActor::SetMuted(const bool bNewMuted)
{
	if (Diagnostics.bMuted == bNewMuted) { return; }
	Diagnostics.bMuted = bNewMuted;
	StopAllVoices();
	if (bNewMuted) { DeactivateTheatreReverb(); }
	else { ActivateTheatreReverb(); }
	if (!bNewMuted && HasLiveStage())
	{
		// Rebuild desired continuous voices only. Muted/old one-shots never replay.
		const auto Resume = [this](UAudioComponent* Voice, const bool bDesired, const float Volume)
		{
			if (bDesired && IsValid(Voice) && IsValid(Voice->Sound))
			{
				++Diagnostics.PlaybackStarts;
				Voice->FadeIn(0.08f, FMath::Clamp(Volume, 0.f, 1.f));
			}
		};
		Resume(AmbientVoice, Diagnostics.bAmbientDesired, WindVolume);
		Resume(HoldingVoice, Diagnostics.bHoldingDesired, HoldingVolume);
		Resume(LeavesVoice, Diagnostics.bLeavesDesired, LeavesVolume);
	}
}

void ADYStageAudioPresentationActor::ActivateTheatreReverb()
{
	if (Diagnostics.bTheatreReverbActive || !bEnableTheatreReverb || Diagnostics.bMuted || !HasLiveStage()
		|| !GetWorld()->GetAudioDeviceRaw()) { return; }
	TheatreReverb = NewObject<UReverbEffect>(this);
	TheatreReverb->bBypassEarlyReflections = false;
	TheatreReverb->bBypassLateReflections = false;
	TheatreReverb->ReflectionsDelay = 0.035f;
	TheatreReverb->ReflectionsGain = 0.12f;
	TheatreReverb->GainHF = 0.7f;
	TheatreReverb->LateDelay = 0.028f;
	TheatreReverb->DecayTime = FMath::IsFinite(TheatreDecaySeconds) ? FMath::Clamp(TheatreDecaySeconds, 0.1f, 20.f) : 2.4f;
	TheatreReverb->DecayHFRatio = 0.68f;
	TheatreReverb->Density = 0.75f;
	TheatreReverb->Diffusion = 0.8f;
	TheatreReverb->AirAbsorptionGainHF = 0.94f;
	TheatreReverb->LateGain = 1.1f;
	TheatreReverb->Gain = 0.32f;
	TheatreReverbTag = FName(*FString::Printf(TEXT("DYTheatre_%s"), *FGuid::NewGuid().ToString(EGuidFormats::Digits)));
	TheatreAudioDevice = GetWorld()->GetAudioDevice();
	UGameplayStatics::ActivateReverbEffect(this, TheatreReverb, TheatreReverbTag, 1.f, 1.f, 0.1f);
	const FActivatedReverb* Registered = TheatreAudioDevice->GetActiveReverb().Find(TheatreReverbTag);
	Diagnostics.bTheatreReverbActive = Registered && Registered->ReverbSettings.ReverbEffect.Get() == TheatreReverb.Get();
	if (!Diagnostics.bTheatreReverbActive)
	{
		TheatreAudioDevice.Reset(); TheatreReverbTag = NAME_None; TheatreReverb = nullptr;
		UE_LOG(LogDengYingShanHai, Warning, TEXT("TheatreAudio Room registration refused; dry sound fallback"));
		return;
	}
	// These remain 2D and unattenuated. bAllowSpatialization enables reading the override,
	// not actual spatialization. Manual send is required for native 2D master reverb.
	int32 Index = 0;
	const float Sends[] = {0.04f, 0.06f, 0.16f, 0.22f, 0.08f};
	for (UAudioComponent* Voice : {AmbientVoice.Get(), HoldingVoice.Get(), ResolveVoice.Get(), ContactVoice.Get(), LeavesVoice.Get()})
	{
		FSoundAttenuationSettings Settings;
		Settings.bSpatialize = false;
		Settings.bAttenuate = false;
		Settings.bEnableReverbSend = true;
		Settings.ReverbSendMethod = EReverbSendMethod::Manual;
		Settings.ManualReverbSendLevel = Sends[Index++];
		Voice->bAllowSpatialization = true;
		Voice->bReverb = true;
		Voice->AdjustAttenuation(Settings);
	}
	UE_LOG(LogDengYingShanHai, Log, TEXT("TheatreAudio RoomActive Tag=%s Decay=%.2f NativeTagRegistered=1 Device=%u"), *TheatreReverbTag.ToString(), TheatreReverb->DecayTime, static_cast<uint32>(TheatreAudioDevice.GetDeviceID()));
}

void ADYStageAudioPresentationActor::DeactivateTheatreReverb()
{
	if (TheatreAudioDevice.IsValid() && !TheatreReverbTag.IsNone())
	{
		// Cleanup must work even after World disables audio playback; GameplayStatics may
		// reject that World during teardown. Release exactly our tag on its original device.
		TheatreAudioDevice->DeactivateReverbEffect(TheatreReverbTag);
		UE_LOG(LogDengYingShanHai, Log, TEXT("TheatreAudio RoomCleanup Tag=%s NativeTagRemaining=%d"), *TheatreReverbTag.ToString(), TheatreAudioDevice->GetActiveReverb().Contains(TheatreReverbTag));
	}
	Diagnostics.bTheatreReverbActive = false;
	TheatreReverbTag = NAME_None;
	TheatreReverb = nullptr;
	TheatreAudioDevice.Reset();
	// Existing mixed tails decay naturally; this removes only our tagged effect.
}

FDYStageAudioDiagnostics ADYStageAudioPresentationActor::GetAudioDiagnostics() const
{
	FDYStageAudioDiagnostics Result = Diagnostics;
	const FActivatedReverb* Registered = TheatreAudioDevice.IsValid() && !TheatreReverbTag.IsNone()
		? TheatreAudioDevice->GetActiveReverb().Find(TheatreReverbTag) : nullptr;
	Result.bTheatreReverbActive = Registered && Registered->ReverbSettings.ReverbEffect.Get() == TheatreReverb.Get();
	return Result;
}
