#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/DYFootstepAudioComponent.h"
#include "Components/AudioComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/StrongObjectPtr.h"
#include "Sound/SoundAttenuation.h"
#include <limits>

struct FDYFootstepAudioTestSeam
{
	static bool Bound(UDYFootstepAudioComponent& Component, ADYStageOperatorPawn& Pawn)
	{
		return Pawn.OnCharacterMovementUpdated.IsAlreadyBound(&Component, &UDYFootstepAudioComponent::HandleMovementUpdated)
			&& Pawn.MovementModeChangedDelegate.IsAlreadyBound(&Component, &UDYFootstepAudioComponent::HandleMovementModeChanged)
			&& Pawn.OnOperatorReset.IsAlreadyBound(&Component, &UDYFootstepAudioComponent::HandleOperatorReset);
	}
	// Pure-clock setup only, not a fabricated movement callback or proof of physical walking.
	static void PrimeDistance(UDYFootstepAudioComponent& Component)
	{
		Component.Gate.Observe(FVector::ZeroVector, FVector(100.0, 0.0, 0.0), 0.3, true, false, 150.0, 360.0);
	}
};

namespace DYFootstepTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;
	FDYFootstepDistanceDecision Move(FDYFootstepDistanceGate& Gate, double From, double To, double DeltaSeconds,
		bool bGrounded = true, bool bTeleported = false, double StepDistance = 150.0, double MaximumSpeed = 360.0)
	{
		return Gate.Observe(FVector(From, 0.0, 0.0), FVector(To, 0.0, 0.0), DeltaSeconds,
			bGrounded, bTeleported, StepDistance, MaximumSpeed);
	}
	struct FWorld
	{
		FWorld()
		{
			World = UWorld::CreateWorld(EWorldType::Game, false);
			Strong.Reset(World);
			if (World && GEngine)
			{
				GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
				World->InitializeActorsForPlay(FURL());
			}
		}
		~FWorld()
		{
			if (World && GEngine)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
			Strong.Reset();
		}
		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> Strong;
	};
	UDYFootstepAudioComponent* AddComponent(AActor& Owner, bool bEnable = true)
	{
		auto* Component = NewObject<UDYFootstepAudioComponent>(&Owner);
		Owner.AddInstanceComponent(Component);
		Component->bEnableDevelopmentFootsteps = bEnable;
		Component->RegisterComponent();
		return Component;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepPartition, "DengYingShanHai.Audio.Footsteps.DistancePartitionAndAlternation", DYFootstepTests::Flags)
bool FDYFootstepPartition::RunTest(const FString&)
{
	FDYFootstepDistanceGate Fine, Coarse;
	int32 FineCount = 0, CoarseCount = 0;
	for (int32 I = 0; I < 100; ++I)
	{
		const auto Result = DYFootstepTests::Move(Fine, I * 9.0, (I + 1) * 9.0, 0.025);
		if (Result.bEmit)
		{
			TestEqual(TEXT("Presentation alternates two candidates"), Result.bLeft, FineCount % 2 == 0);
			++FineCount;
		}
	}
	for (int32 I = 0; I < 50; ++I)
	{
		if (DYFootstepTests::Move(Coarse, I * 18.0, (I + 1) * 18.0, 0.05).bEmit) { ++CoarseCount; }
	}
	TestEqual(TEXT("Nine metres yields an onset and five subsequent 150 cm impacts"), FineCount, 6);
	TestEqual(TEXT("Normal update partition does not change cadence"), CoarseCount, FineCount);
	TestTrue(TEXT("Both partitions end at same distance remainder"), FMath::IsNearlyEqual(Fine.GetAccumulatedDistance(), Coarse.GetAccumulatedDistance(), 1.e-6));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepStop, "DengYingShanHai.Audio.Footsteps.StationaryBlockedAndStop", DYFootstepTests::Flags)
bool FDYFootstepStop::RunTest(const FString&)
{
	FDYFootstepDistanceGate Gate;
	TestTrue(TEXT("Starting physical walking does not wait a full stride"), DYFootstepTests::Move(Gate, 0.0, 140.0, 0.4).bEmit);
	const auto Stopped = DYFootstepTests::Move(Gate, 140.0, 140.0, 0.1);
	TestFalse(TEXT("Stationary update never emits"), Stopped.bEmit);
	TestTrue(TEXT("Actual stop tells the component to stop its dry voice"), Stopped.bStopped);
	TestEqual(TEXT("Stopping removes the old distance debt"), Gate.GetAccumulatedDistance(), 0.0);
	const auto Restart = DYFootstepTests::Move(Gate, 140.0, 160.0, 0.1);
	TestTrue(TEXT("New short walk gets its own onset"), Restart.bEmit && Restart.bStarted);
	TestEqual(TEXT("New walk has only its own distance past onset, no pre-stop debt"), Gate.GetAccumulatedDistance(), 18.0);
	for (int32 I = 0; I < 100; ++I)
	{
		TestFalse(TEXT("Wall-blocked zero displacement stays silent even if input was held"), DYFootstepTests::Move(Gate, 160.0, 160.0, 0.025).bEmit);
	}
	TestEqual(TEXT("Blocked input cannot accumulate distance"), Gate.GetAccumulatedDistance(), 0.0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepAir, "DengYingShanHai.Audio.Footsteps.AirborneAndLanding", DYFootstepTests::Flags)
bool FDYFootstepAir::RunTest(const FString&)
{
	FDYFootstepDistanceGate Gate;
	DYFootstepTests::Move(Gate, 0.0, 140.0, 0.4);
	TestFalse(TEXT("Airborne horizontal travel is not a footstep"), DYFootstepTests::Move(Gate, 140.0, 170.0, 0.1, false).bEmit);
	TestEqual(TEXT("Airborne transition clears old debt"), Gate.GetAccumulatedDistance(), 0.0);
	TestFalse(TEXT("Stationary landing is not a walking impact"), DYFootstepTests::Move(Gate, 170.0, 170.0, 0.1).bEmit);
	TestTrue(TEXT("Walking after stationary landing gets a fresh onset"), DYFootstepTests::Move(Gate, 170.0, 190.0, 0.1).bStarted);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepWarp, "DengYingShanHai.Audio.Footsteps.TeleportAndContinuity", DYFootstepTests::Flags)
bool FDYFootstepWarp::RunTest(const FString&)
{
	FDYFootstepDistanceGate Gate;
	DYFootstepTests::Move(Gate, 0.0, 140.0, 0.4);
	const auto Teleport = DYFootstepTests::Move(Gate, 140.0, 5000.0, 0.1, true, true);
	TestFalse(TEXT("Explicit teleport cannot emit"), Teleport.bEmit);
	TestTrue(TEXT("Explicit teleport records discontinuity"), Teleport.bDiscontinuity);
	TestEqual(TEXT("Teleport clears debt"), Gate.GetAccumulatedDistance(), 0.0);
	TestTrue(TEXT("Small real move after teleport starts fresh"), DYFootstepTests::Move(Gate, 5000.0, 5020.0, 0.1).bStarted);
	const auto BetweenUpdates = DYFootstepTests::Move(Gate, 9000.0, 9020.0, 0.1);
	TestTrue(TEXT("Displacement between movement updates is detected even if movement clears its teleport flag"), BetweenUpdates.bDiscontinuity);
	TestFalse(TEXT("Between-update relocation remains silent"), BetweenUpdates.bEmit);
	const auto TooFast = DYFootstepTests::Move(Gate, 9020.0, 10020.0, 0.1);
	TestTrue(TEXT("Implausible movement without a teleport flag is rejected"), TooFast.bDiscontinuity);
	TestFalse(TEXT("Implausible movement cannot emit"), TooFast.bEmit);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepLowFrame, "DengYingShanHai.Audio.Footsteps.LowFrameRateAndSessionReset", DYFootstepTests::Flags)
bool FDYFootstepLowFrame::RunTest(const FString&)
{
	FDYFootstepDistanceGate Gate;
	const auto LowFrame = DYFootstepTests::Move(Gate, 0.0, 180.0, 0.5, true, false, 50.0);
	TestTrue(TEXT("A valid slow update emits at most the one returned request"), LowFrame.bEmit);
	TestEqual(TEXT("Missed full steps are discarded after the 2 cm onset rather than queued"), Gate.GetAccumulatedDistance(), 28.0);
	const auto Stalled = DYFootstepTests::Move(Gate, 180.0, 540.0, 1.0);
	TestFalse(TEXT("Long stalled update does not trigger a catch-up request"), Stalled.bEmit);
	TestTrue(TEXT("Long update is treated as a timing discontinuity"), Stalled.bDiscontinuity);
	Gate.Reset();
	const auto NewSession = DYFootstepTests::Move(Gate, 0.0, 150.0, 0.5);
	TestTrue(TEXT("New world/session can emit a fresh first step"), NewSession.bEmit);
	TestTrue(TEXT("New session starts with first candidate again"), NewSession.bLeft);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepDefaults, "DengYingShanHai.Audio.Footsteps.PassiveDefaultContract", DYFootstepTests::Flags)
bool FDYFootstepDefaults::RunTest(const FString&)
{
	const auto* Component = GetDefault<UDYFootstepAudioComponent>();
	TestFalse(TEXT("No component Tick"), Component->PrimaryComponentTick.bCanEverTick);
	TestFalse(TEXT("Default off"), Component->bEnableDevelopmentFootsteps);
	TestFalse(TEXT("No auto activation"), Component->bAutoActivate);
	TestEqual(TEXT("Dev default distance, no speed edit"), Component->StepDistanceCentimeters, 150.0);
	TestEqual(TEXT("Candidate native room send"), Component->TheatreReverbSendLevel, 0.22f);
	TestNull(TEXT("No implicit left source"), Component->LeftSound.Get());
	TestNull(TEXT("No implicit right source"), Component->RightSound.Get());
	TestNull(TEXT("No audio voice created in the CDO/editor"), Component->GetFootstepVoice());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepInvalidParameters, "DengYingShanHai.Audio.Footsteps.InvalidParametersFailSilent", DYFootstepTests::Flags)
bool FDYFootstepInvalidParameters::RunTest(const FString&)
{
	FDYFootstepDistanceGate Gate;
	TestFalse(TEXT("Zero step distance never becomes an infinite cadence"), DYFootstepTests::Move(Gate, 0.0, 30.0, 0.1, true, false, 0.0).bEmit);
	TestFalse(TEXT("Negative step distance is silent"), DYFootstepTests::Move(Gate, 0.0, 30.0, 0.1, true, false, -10.0).bEmit);
	TestFalse(TEXT("Zero delta time cannot emit"), DYFootstepTests::Move(Gate, 0.0, 30.0, 0.0).bEmit);
	TestFalse(TEXT("Non-finite delta time cannot emit"), DYFootstepTests::Move(Gate, 0.0, 30.0, std::numeric_limits<double>::quiet_NaN()).bEmit);
	TestFalse(TEXT("Non-finite geometry cannot emit"), Gate.Observe(FVector::ZeroVector,
		FVector(std::numeric_limits<double>::infinity(), 0.0, 0.0), 0.1, true, false, 150.0, 360.0).bEmit);
	TestEqual(TEXT("Invalid parameters leave no partial debt"), Gate.GetAccumulatedDistance(), 0.0);
	TestEqual(TEXT("Negative room send clamps to zero"), UDYFootstepAudioComponent::SanitizeReverbSendLevel(-0.5f), 0.0f);
	TestEqual(TEXT("Excessive room send clamps to one"), UDYFootstepAudioComponent::SanitizeReverbSendLevel(5.0f), 1.0f);
	TestEqual(TEXT("Non-finite room send fails dry rather than sending NaN"), UDYFootstepAudioComponent::SanitizeReverbSendLevel(std::numeric_limits<float>::quiet_NaN()), 0.0f);
	TestEqual(TEXT("Valid candidate room send unchanged"), UDYFootstepAudioComponent::SanitizeReverbSendLevel(0.22f), 0.22f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepInvalidOwner, "DengYingShanHai.Audio.Footsteps.MissingCharacterFallback", DYFootstepTests::Flags)
bool FDYFootstepInvalidOwner::RunTest(const FString&)
{
	DYFootstepTests::FWorld Scope;
	if (!TestNotNull(TEXT("Transient game world"), Scope.World)) { return false; }
	auto* Owner = Scope.World->SpawnActor<AActor>();
	if (!TestNotNull(TEXT("Non-Character owner"), Owner)) { return false; }
	auto* Component = DYFootstepTests::AddComponent(*Owner);
	Owner->DispatchBeginPlay();
	TestFalse(TEXT("Invalid owner leaves runtime inactive"), Component->GetFootstepDiagnostics().bRuntimeActive);
	TestNull(TEXT("Invalid owner creates no voice"), Component->GetFootstepVoice());
	Component->SetMuted(true);
	Component->SetMuted(false);
	TestEqual(TEXT("Silence fallback cannot replay anything"), Component->GetFootstepDiagnostics().PlaybackStarts, 0);
	Owner->Destroy();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepLifecycle, "DengYingShanHai.Audio.Footsteps.RealBindingResetAndTeardown", DYFootstepTests::Flags)
bool FDYFootstepLifecycle::RunTest(const FString&)
{
	DYFootstepTests::FWorld Scope;
	if (!TestNotNull(TEXT("Transient game world"), Scope.World)) { return false; }
	auto* Pawn = Scope.World->SpawnActor<ADYStageOperatorPawn>();
	if (!TestNotNull(TEXT("Existing native operator"), Pawn)) { return false; }
	auto* Component = DYFootstepTests::AddComponent(*Pawn);
	// The real Actor lifecycle enters all registered components. Never call BeginPlay directly.
	Pawn->DispatchBeginPlay();
	TestTrue(TEXT("Same-world Character starts opted-in capability"), Component->GetFootstepDiagnostics().bRuntimeActive);
	TestTrue(TEXT("Real movement, mode-change and existing reset delegates are bound"), FDYFootstepAudioTestSeam::Bound(*Component, *Pawn));
	UAudioComponent* Voice = Component->GetFootstepVoice();
	if (!TestNotNull(TEXT("One runtime voice"), Voice)) { return false; }
	TestTrue(TEXT("Voice owned by existing operator"), Voice->GetOwner() == Pawn);
	TestTrue(TEXT("Voice registered in owner's world"), Voice->IsRegistered() && Voice->GetWorld() == Scope.World);
	TestFalse(TEXT("No automatic playback"), Voice->bAutoActivate);
	TestFalse(TEXT("No auto destruction"), Voice->bAutoDestroy);
	TestTrue(TEXT("Owner destruction stops voice"), Voice->bStopWhenOwnerDestroyed);
	TestFalse(TEXT("No voice Tick"), Voice->PrimaryComponentTick.bCanEverTick);
	TestTrue(TEXT("Native attenuation override available for send routing"), Voice->bAllowSpatialization && Voice->bOverrideAttenuation);
	TestFalse(TEXT("No spatialization imposed on the near-player dry sound"), Voice->AttenuationOverrides.bSpatialize);
	TestFalse(TEXT("No distance-based volume attenuation"), Voice->AttenuationOverrides.bAttenuate);
	TestTrue(TEXT("Native reverb send enabled"), Voice->AttenuationOverrides.bEnableReverbSend && Voice->bReverb);
	TestEqual(TEXT("Constant native reverb send"), Voice->AttenuationOverrides.ReverbSendMethod, EReverbSendMethod::Manual);
	TestEqual(TEXT("Configured room send reaches actual registered voice"), Voice->AttenuationOverrides.ManualReverbSendLevel, 0.22f);
	FDYFootstepAudioTestSeam::PrimeDistance(*Component);
	TestEqual(TEXT("Pure clock primed past the 2 cm onset for reset boundary"), Component->GetFootstepDiagnostics().AccumulatedDistanceCentimeters, 98.0);
	Pawn->ResetOperatorToStart(EDYOperatorResetReason::Manual);
	TestEqual(TEXT("Existing real operator reset event consumed once"), Component->GetFootstepDiagnostics().ResetEvents, 1);
	TestEqual(TEXT("Existing reset clears partial cadence immediately"), Component->GetFootstepDiagnostics().AccumulatedDistanceCentimeters, 0.0);
	FDYFootstepAudioTestSeam::PrimeDistance(*Component);
	Component->SetMuted(true);
	TestTrue(TEXT("Mute diagnostic true"), Component->GetFootstepDiagnostics().bMuted);
	TestEqual(TEXT("Mute clears partial debt"), Component->GetFootstepDiagnostics().AccumulatedDistanceCentimeters, 0.0);
	Component->SetMuted(false);
	TestEqual(TEXT("Unmute has no old impact to replay"), Component->GetFootstepDiagnostics().PlaybackStarts, 0);
	Component->DestroyComponent();
	TestFalse(TEXT("Capability EndPlay disables runtime"), Component->GetFootstepDiagnostics().bRuntimeActive);
	TestFalse(TEXT("Actual owner delegates unbound"), FDYFootstepAudioTestSeam::Bound(*Component, *Pawn));
	TestNull(TEXT("Owned voice reference released"), Component->GetFootstepVoice());
	TestFalse(TEXT("Old voice unregistered"), Voice->IsRegistered());
	Pawn->Destroy();

	auto* SecondPawn = Scope.World->SpawnActor<ADYStageOperatorPawn>();
	if (!TestNotNull(TEXT("Second independent Character session"), SecondPawn)) { return false; }
	auto* SecondComponent = DYFootstepTests::AddComponent(*SecondPawn);
	SecondPawn->DispatchBeginPlay();
	TestTrue(TEXT("Second session binds independently"), FDYFootstepAudioTestSeam::Bound(*SecondComponent, *SecondPawn));
	SecondPawn->Destroy();
	TestFalse(TEXT("Actual owner destruction disables its capability"), SecondComponent->GetFootstepDiagnostics().bRuntimeActive);
	TestFalse(TEXT("Actual owner destruction clears source bindings"), FDYFootstepAudioTestSeam::Bound(*SecondComponent, *SecondPawn));
	TestNull(TEXT("Actual owner destruction releases its voice"), SecondComponent->GetFootstepVoice());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepOnset, "DengYingShanHai.Audio.Footsteps.ShortWalkOnsetAndRestart", DYFootstepTests::Flags)
bool FDYFootstepOnset::RunTest(const FString&)
{
	FDYFootstepDistanceGate Gate;
	TestFalse(TEXT("One centimetre correction does not emit"), DYFootstepTests::Move(Gate, 0.0, 1.0, 0.025).bEmit);
	const auto First = DYFootstepTests::Move(Gate, 1.0, 2.0, 0.025);
	TestTrue(TEXT("Short walk emits at 2 cm, not 150 cm"), First.bEmit && First.bStarted && First.bLeft);
	TestTrue(TEXT("Gate moving after real onset"), Gate.IsMoving());
	TestFalse(TEXT("Sub-stride travel does not retrigger onset"), DYFootstepTests::Move(Gate, 2.0, 140.0, 0.4).bEmit);
	TestFalse(TEXT("Stride is measured from the exact onset"), DYFootstepTests::Move(Gate, 140.0, 151.0, 0.05).bEmit);
	const auto Next = DYFootstepTests::Move(Gate, 151.0, 152.0, 0.025);
	TestTrue(TEXT("Subsequent impact is 150 cm past onset and alternates"), Next.bEmit && !Next.bStarted && !Next.bLeft);
	TestTrue(TEXT("Stop transition occurs once"), DYFootstepTests::Move(Gate, 152.0, 152.0, 0.025).bStopped);
	TestFalse(TEXT("Repeated stationary updates are not repeated stop events"), DYFootstepTests::Move(Gate, 152.0, 152.0, 0.025).bStopped);
	const auto Restart = DYFootstepTests::Move(Gate, 152.0, 154.0, 0.025);
	TestTrue(TEXT("Short restart immediately confirms new onset"), Restart.bEmit && Restart.bStarted && Restart.bLeft);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFootstepJitter, "DengYingShanHai.Audio.Footsteps.CollisionJitterCannotAccumulateOnset", DYFootstepTests::Flags)
bool FDYFootstepJitter::RunTest(const FString&)
{
	FDYFootstepDistanceGate Gate;
	for (int32 I = 0; I < 200; ++I)
	{
		const double From = I % 2 == 0 ? 0.0 : 0.5;
		const double To = I % 2 == 0 ? 0.5 : 0.0;
		TestFalse(TEXT("Oscillation within 2 cm does not accumulate a fake onset"), DYFootstepTests::Move(Gate, From, To, 0.025).bEmit);
	}
	TestFalse(TEXT("Jitter leaves gate stationary"), Gate.IsMoving());
	TestTrue(TEXT("Genuine net travel after jitter is still accepted"), DYFootstepTests::Move(Gate, 0.0, 2.0, 0.025).bStarted);
	return true;
}

#endif
