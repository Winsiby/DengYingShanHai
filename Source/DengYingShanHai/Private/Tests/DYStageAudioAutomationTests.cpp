#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Stage/DYStageAudioPresentationActor.h"
#include "Stage/DYStagePresentation.h"
#include "Components/AudioComponent.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include "Puzzles/DYPuzzleDirector.h"

struct FDYStageAudioTestSeam
{
	static void Begin(ADYStageAudioPresentationActor& Actor) { Actor.DispatchBeginPlay(); }
	static void End(ADYStageAudioPresentationActor& Actor) { Actor.EndPlay(EEndPlayReason::Destroyed); }
	static bool Bound(const ADYStageAudioPresentationActor& Actor) { return Actor.ActHandle.IsValid() && Actor.FeedbackHandle.IsValid() && Actor.ContactHandle.IsValid() && Actor.AlignmentHandle.IsValid(); }
};
namespace DYAudioTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;
	FDYActSequenceSnapshot View(EDYActSequencePhase Phase, int32 Act = 0, int32 Chapter = INDEX_NONE)
	{
		FDYActSequenceSnapshot S; S.bSequenceEnabled = true; S.ActCount = 3; S.ActIndex = Act; S.Phase = Phase;
		S.ChapterIndex = Chapter; S.ChapterCount = Chapter == INDEX_NONE ? 0 : 4; return S;
	}
	struct FWorld
	{
		FWorld()
		{
			World = UWorld::CreateWorld(EWorldType::Game, false);
			Strong.Reset(World);
			if (World && GEngine) { GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World); World->InitializeActorsForPlay(FURL()); }
		}
		~FWorld()
		{
			if (World && GEngine) { GEngine->DestroyWorldContext(World); World->DestroyWorld(false); }
			Strong.Reset();
		}
		UWorld* World = nullptr; TStrongObjectPtr<UWorld> Strong;
	};
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioFinite, "DengYingShanHai.Audio.FiniteHolding", DYAudioTests::Flags)
bool FDYAudioFinite::RunTest(const FString&)
{
	FDYStageAudioGate Gate;
	const auto Inactive = Gate.Observe(DYAudioTests::View(EDYActSequencePhase::Inactive), EDYStageFeedbackDisplay::Holding, true);
	TestFalse(TEXT("No ambient before start"), Inactive.bAmbient); TestFalse(TEXT("No hold before start"), Inactive.bHolding);
	const auto Holding = Gate.Observe(DYAudioTests::View(EDYActSequencePhase::Playing), EDYStageFeedbackDisplay::Holding, true);
	TestTrue(TEXT("Playing has ambient"), Holding.bAmbient); TestTrue(TEXT("Existing Holding enables rhythm"), Holding.bHolding);
	TestFalse(TEXT("Interrupted cancels rhythm"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::Playing), EDYStageFeedbackDisplay::Interrupted, true).bHolding);
	TestFalse(TEXT("AwaitingFinale never keeps Holding"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingFinale, 2), EDYStageFeedbackDisplay::Holding, true).bHolding);
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioResolve, "DengYingShanHai.Audio.ResolveDeduplicated", DYAudioTests::Flags)
bool FDYAudioResolve::RunTest(const FString&)
{
	FDYStageAudioGate Gate;
	TestTrue(TEXT("P01 once"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingTransition, 0), EDYStageFeedbackDisplay::Complete, true).bResolveOneShot);
	for (int32 I = 0; I < 100; ++I) { TestFalse(TEXT("Repeated notification cannot retrigger"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingTransition, 0), EDYStageFeedbackDisplay::Complete, true).bResolveOneShot); }
	TestTrue(TEXT("P02 once"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingTransition, 1), EDYStageFeedbackDisplay::Complete, true).bResolveOneShot);
	TestFalse(TEXT("P03 resolve not contact impact"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingFinale, 2), EDYStageFeedbackDisplay::Complete, true).bResolveOneShot);
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioCampaignResolve, "DengYingShanHai.Audio.FourChapterResolveCues", DYAudioTests::Flags)
bool FDYAudioCampaignResolve::RunTest(const FString&)
{
	FDYStageAudioGate Gate;
	int32 Cues = 0;
	for (int32 Chapter = 0; Chapter < 4; ++Chapter)
	{
		for (int32 Act = 0; Act < 2; ++Act)
		{
			Gate.Observe(DYAudioTests::View(EDYActSequencePhase::Playing, Act, Chapter), EDYStageFeedbackDisplay::Adjust, true);
			const auto Resolved = DYAudioTests::View(EDYActSequencePhase::AwaitingTransition, Act, Chapter);
			const auto Plan = Gate.Observe(Resolved, EDYStageFeedbackDisplay::Complete, true);
			TestTrue(TEXT("Each chapter's first two steps emit their own cue"), Plan.bResolveOneShot);
			Cues += Plan.bResolveOneShot ? 1 : 0;
			for (int32 Repeat = 0; Repeat < 3; ++Repeat)
			{
				TestFalse(TEXT("Duplicate resolve stays silent within the step"),
					Gate.Observe(Resolved, EDYStageFeedbackDisplay::Complete, true).bResolveOneShot);
			}
		}
		TestFalse(TEXT("A chapter finale is not a step resolve cue"),
			Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingFinale, 2, Chapter), EDYStageFeedbackDisplay::Complete, true).bResolveOneShot);
	}
	TestEqual(TEXT("Four chapters produce all eight step cues"), Cues, 8);
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioChapterRetry, "DengYingShanHai.Audio.ChapterReturnAndStepRetry", DYAudioTests::Flags)
bool FDYAudioChapterRetry::RunTest(const FString&)
{
	FDYStageAudioGate Gate;
	auto Start = [&Gate](int32 Chapter, int32 Act)
	{
		Gate.Observe(DYAudioTests::View(EDYActSequencePhase::Playing, Act, Chapter), EDYStageFeedbackDisplay::Adjust, true);
	};
	auto Resolve = [&Gate](int32 Chapter, int32 Act)
	{
		return Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingTransition, Act, Chapter),
			EDYStageFeedbackDisplay::Complete, true).bResolveOneShot;
	};
	Start(0, 0); TestTrue(TEXT("Original chapter step zero"), Resolve(0, 0));
	Start(0, 1); TestTrue(TEXT("Original chapter step one"), Resolve(0, 1));
	Start(1, 0); TestTrue(TEXT("Next chapter may reuse step zero"), Resolve(1, 0));
	Start(0, 0); TestTrue(TEXT("Selecting a previously played chapter starts a fresh attempt"), Resolve(0, 0));
	TestFalse(TEXT("Returned chapter duplicate stays silent"), Resolve(0, 0));
	Start(0, 0);
	for (int32 Repeat = 0; Repeat < 5; ++Repeat) { Start(0, 0); }
	TestTrue(TEXT("Retrying the settled same step emits once after completion"), Resolve(0, 0));
	TestFalse(TEXT("Retried step duplicate stays silent"), Resolve(0, 0));
	Start(0, 1); TestTrue(TEXT("Step one still emits after chapter replay"), Resolve(0, 1));
	Start(0, 1); TestTrue(TEXT("Retrying step one emits for the new completion"), Resolve(0, 1));
	TestFalse(TEXT("Second retry duplicate stays silent"), Resolve(0, 1));
	Start(0, 0); TestTrue(TEXT("Reselecting the same chapter from a later step rearms step zero"), Resolve(0, 0));
	Gate.Observe(DYAudioTests::View(EDYActSequencePhase::Inactive), EDYStageFeedbackDisplay::Hidden, true);
	TestTrue(TEXT("An inactive session clears consumed cues"), Resolve(0, 0));
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioChapterLate, "DengYingShanHai.Audio.ChapterLateJoinNoReplay", DYAudioTests::Flags)
bool FDYAudioChapterLate::RunTest(const FString&)
{
	FDYStageAudioGate Gate;
	for (int32 Chapter : {0, 1, 0})
	{
		const auto Resolved = DYAudioTests::View(EDYActSequencePhase::AwaitingTransition, 0, Chapter);
		TestFalse(TEXT("Late chapter sync consumes without playback"),
			Gate.Observe(Resolved, EDYStageFeedbackDisplay::Complete, false).bResolveOneShot);
		TestFalse(TEXT("A later notification does not replay the consumed cue"),
			Gate.Observe(Resolved, EDYStageFeedbackDisplay::Complete, true).bResolveOneShot);
	}
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioLate, "DengYingShanHai.Audio.LateJoinNoReplay", DYAudioTests::Flags)
bool FDYAudioLate::RunTest(const FString&)
{
	FDYStageAudioGate Gate;
	TestFalse(TEXT("Late sync consumes resolved cue silently"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingTransition), EDYStageFeedbackDisplay::Complete, false).bResolveOneShot);
	TestFalse(TEXT("Later duplicate remains silent"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingTransition), EDYStageFeedbackDisplay::Complete, true).bResolveOneShot);
	FDYStaffContactPresentationSnapshot Contact; Contact.bHasContact = true; Contact.Token = FGuid::NewGuid();
	Gate.AcceptContact(Contact, Contact, DYAudioTests::View(EDYActSequencePhase::AwaitingFinale, 2)); // Actor seeds this without playback.
	TestFalse(TEXT("Late contact notification not replayed"), Gate.AcceptContact(Contact, Contact, DYAudioTests::View(EDYActSequencePhase::AwaitingFinale, 2)));
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioContact, "DengYingShanHai.Audio.AcceptedContactIdentity", DYAudioTests::Flags)
bool FDYAudioContact::RunTest(const FString&)
{
	FDYStageAudioGate Gate; FDYStaffContactPresentationSnapshot C; C.bHasContact = true; C.Token = FGuid::NewGuid();
	const auto Finale = DYAudioTests::View(EDYActSequencePhase::AwaitingFinale, 2);
	TestFalse(TEXT("No current Stage contact means silence"), Gate.AcceptContact(C, {}, Finale));
	TestFalse(TEXT("Resolve without AwaitingFinale not contact"), Gate.AcceptContact(C, C, DYAudioTests::View(EDYActSequencePhase::Playing, 2)));
	auto Old = C; Old.Token = FGuid::NewGuid(); TestFalse(TEXT("Old token cannot play current impact"), Gate.AcceptContact(Old, C, Finale));
	TestTrue(TEXT("Actual accepted current identity once"), Gate.AcceptContact(C, C, Finale));
	TestFalse(TEXT("Duplicate accepted identity suppressed"), Gate.AcceptContact(C, C, Finale));
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioForest, "DengYingShanHai.Audio.ForestWaitsForComplete", DYAudioTests::Flags)
bool FDYAudioForest::RunTest(const FString&)
{
	FDYStageAudioGate Gate;
	TestFalse(TEXT("P03 resolve is not complete forest"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::AwaitingFinale, 2), EDYStageFeedbackDisplay::Complete, true).bLeaves);
	TestTrue(TEXT("Stage complete permits leaf ambience"), Gate.Observe(DYAudioTests::View(EDYActSequencePhase::Complete, 2), EDYStageFeedbackDisplay::Complete, true).bLeaves);
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioReset, "DengYingShanHai.Audio.WorldSessionGateReset", DYAudioTests::Flags)
bool FDYAudioReset::RunTest(const FString&)
{
	FDYStageAudioGate Gate;
	const auto S = DYAudioTests::View(EDYActSequencePhase::AwaitingTransition);
	TestTrue(TEXT("First world cue"), Gate.Observe(S, EDYStageFeedbackDisplay::Complete, true).bResolveOneShot);
	Gate.Reset(); TestTrue(TEXT("Explicit new cosmetic session can emit again"), Gate.Observe(S, EDYStageFeedbackDisplay::Complete, true).bResolveOneShot);
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioDefaults, "DengYingShanHai.Audio.PassiveDefaultContract", DYAudioTests::Flags)
bool FDYAudioDefaults::RunTest(const FString&)
{
	const auto* Default = GetDefault<ADYStageAudioPresentationActor>();
	TestFalse(TEXT("No Tick"), Default->PrimaryActorTick.bCanEverTick);
	TestFalse(TEXT("Default off"), Default->bEnableDevelopmentAudio);
	TestNull(TEXT("No implicit Stage discovery"), Default->StagePresentation.Get());
	for (const UAudioComponent* Voice : {Default->AmbientVoice.Get(), Default->HoldingVoice.Get(), Default->ResolveVoice.Get(), Default->ContactVoice.Get(), Default->LeavesVoice.Get()})
	{
		TestNotNull(TEXT("Owned voice exists"), Voice); if (!Voice) { continue; }
		TestFalse(TEXT("Not auto-playing"), Voice->bAutoActivate); TestTrue(TEXT("Owner destruction stops voice"), Voice->bStopWhenOwnerDestroyed);
	}
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioLifecycle, "DengYingShanHai.Audio.MissingReferenceLifecycle", DYAudioTests::Flags)
bool FDYAudioLifecycle::RunTest(const FString&)
{
	DYAudioTests::FWorld Scope; if (!TestNotNull(TEXT("Transient world"), Scope.World)) { return false; }
	auto* Actor = Scope.World->SpawnActor<ADYStageAudioPresentationActor>();
	if (!TestNotNull(TEXT("Audio actor"), Actor)) { return false; }
	Actor->bEnableDevelopmentAudio = true; FDYStageAudioTestSeam::Begin(*Actor);
	TestFalse(TEXT("Missing Stage is a silent fallback"), Actor->GetAudioDiagnostics().bRuntimeActive);
	Actor->SetMuted(true); Actor->SetMuted(false); FDYStageAudioTestSeam::End(*Actor);
	TestFalse(TEXT("End disables runtime"), Actor->GetAudioDiagnostics().bRuntimeActive);
	TestEqual(TEXT("No voice request for missing owner"), Actor->GetAudioDiagnostics().PlaybackStarts, 0);
	TestFalse(TEXT("No Hold after teardown"), Actor->GetAudioDiagnostics().bHoldingDesired);
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAudioBinding, "DengYingShanHai.Audio.RealStageBindingTeardown", DYAudioTests::Flags)
bool FDYAudioBinding::RunTest(const FString&)
{
	DYAudioTests::FWorld Scope; if (!TestNotNull(TEXT("Transient world"), Scope.World)) { return false; }
	auto* Stage = Scope.World->SpawnActor<ADYStagePresentation>();
	auto* Director = Scope.World->SpawnActor<ADYPuzzleDirector>();
	auto* Environment = Scope.World->SpawnActor<ADYStageEnvironment>();
	auto* Audio = Scope.World->SpawnActor<ADYStageAudioPresentationActor>();
	if (!Stage || !Director || !Environment || !Audio) { AddError(TEXT("Required native test actors")); return false; }
	// The same reflected instance configuration used by the editor; no puzzle event is fabricated.
	auto* DirectorProperty = FindFProperty<FObjectPropertyBase>(Stage->GetClass(), TEXT("PuzzleDirector"));
	auto* EnvironmentProperty = FindFProperty<FObjectPropertyBase>(Stage->GetClass(), TEXT("StageEnvironment"));
	if (!DirectorProperty || !EnvironmentProperty) { AddError(TEXT("Stable Stage configuration properties")); return false; }
	DirectorProperty->SetObjectPropertyValue_InContainer(Stage, Director);
	EnvironmentProperty->SetObjectPropertyValue_InContainer(Stage, Environment);
	Stage->DispatchBeginPlay();
	Audio->StagePresentation = Stage; Audio->bEnableDevelopmentAudio = true; Audio->DispatchBeginPlay();
	TestTrue(TEXT("Explicit actual same-world Stage bound"), Audio->GetAudioDiagnostics().bRuntimeActive);
	TestTrue(TEXT("All four native handles retained"), FDYStageAudioTestSeam::Bound(*Audio));
	Stage->Destroy();
	TestFalse(TEXT("Stage ending disables still-existing audio actor"), Audio->GetAudioDiagnostics().bRuntimeActive);
	TestFalse(TEXT("All handles cleared after Stage destruction"), FDYStageAudioTestSeam::Bound(*Audio));
	TestFalse(TEXT("Ambient demand cleared"), Audio->GetAudioDiagnostics().bAmbientDesired);
	TestFalse(TEXT("Leaves demand cleared"), Audio->GetAudioDiagnostics().bLeavesDesired);
	for (UAudioComponent* Voice : {Audio->AmbientVoice.Get(),Audio->HoldingVoice.Get(),Audio->ResolveVoice.Get(),Audio->ContactVoice.Get(),Audio->LeavesVoice.Get()}) { TestFalse(TEXT("Every voice stopped"), Voice->IsPlaying()); }
	Audio->SetMuted(true); Audio->SetMuted(false);
	TestEqual(TEXT("Unmute cannot recreate ended session"), Audio->GetAudioDiagnostics().PlaybackStarts, 0);
	Audio->Destroy();
	return true;
}
#endif
