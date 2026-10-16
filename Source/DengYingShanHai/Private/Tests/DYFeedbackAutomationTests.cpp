#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Core/DYStageGameMode.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Stage/DYStagePresentation.h"
#include "UI/DYDevInteractionHUD.h"
#include "UI/DYInteractionHUD.h"
#include "UI/DYInteractionHUDWidget.h"
#include "Player/DYStageOperatorPawn.h"
#include "Interaction/DYInteractionComponent.h"
#include "TimerManager.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"

/** Private test access only; no public success-setting or cheat API. */
struct FDYStageFeedbackTestSeam
{
	static void Sample(ADYStagePresentation& P, EDYPuzzleFeedbackState Feedback, bool bCanceled = false)
	{
		FDYEvaluationResult Result;
		Result.Feedback = Feedback;
		Result.bHoldCanceled = bCanceled;
		P.HandleEvaluationUpdated(Result);
	}
	static void Activate(ADYStagePresentation& P) { P.HandlePuzzleActivated(TEXT("FeedbackTest")); }
	static void Cancel(ADYStagePresentation& P) { P.HandleHoldCanceled(TEXT("FeedbackTest")); }
	static void End(ADYStagePresentation& P) { P.EndPlay(EEndPlayReason::Destroyed); }
	static void Resolve(ADYStagePresentation& P)
	{
		FDYEvaluationResult Result;
		Result.Feedback = EDYPuzzleFeedbackState::Resolved;
		P.HandlePuzzleResolved(TEXT("FeedbackTest"), Result);
	}
	static void SetDuration(ADYStagePresentation& P, float Seconds) { P.DevInterruptedDisplaySeconds = Seconds; }
	static bool HasTimer(ADYStagePresentation& P) { return P.GetWorld()->GetTimerManager().IsTimerActive(P.DevInterruptedTimerHandle); }
	static float Remaining(ADYStagePresentation& P) { return P.GetWorld()->GetTimerManager().GetTimerRemaining(P.DevInterruptedTimerHandle); }
	static void Bind(ADYDevInteractionHUD& HUD, ADYStageGameMode* Mode) { HUD.BindToGameMode(Mode); }
	static void Unbind(ADYDevInteractionHUD& HUD) { HUD.UnbindGameMode(); }
	static EDYStageFeedbackDisplay Cached(const ADYDevInteractionHUD& HUD) { return HUD.CachedFeedbackDisplay; }
};

namespace DYFeedbackTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;

	/** Unsaved, strongly held world: real Dev/non-Dev package paths, never a gate bypass. */
	struct FScopedWorld
	{
		explicit FScopedWorld(bool bDev = true)
		{
			if (!GEngine) { return; }
			const FName Name = MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYFeedbackTestWorld"), EUniqueObjectNameOptions::GloballyUnique);
			const FString Prefix = bDev ? TEXT("/Game/DengYingShanHai/Dev/Automation/") : TEXT("/Game/DengYingShanHai/Maps/");
			UPackage* Package = CreatePackage(*(Prefix + Name.ToString()));
			Package->SetFlags(RF_Transient);
			World = UWorld::CreateWorld(EWorldType::Game, false, Name, Package);
			StrongWorld.Reset(World);
			if (World)
			{
				GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
				World->InitializeActorsForPlay(FURL());
			}
		}
		~FScopedWorld()
		{
			if (World && GEngine) { GEngine->DestroyWorldContext(World); World->DestroyWorld(false); }
			StrongWorld.Reset();
		}
		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> StrongWorld;
	};

	enum class ETimerScenario { Restore, Hold, Resolve, Activate, DuplicateCancel };

	/** Latent updates cross actual engine frames; never modify GFrameCounter. */
	class FTimerScenarioCommand : public IAutomationLatentCommand
	{
	public:
		FTimerScenarioCommand(FAutomationTestBase* InTest, ETimerScenario InScenario, bool bDev = true)
			: Test(InTest), Scenario(InScenario), Fixture(MakeShared<FScopedWorld>(bDev)) {}
		virtual bool Update() override
		{
			if (!Fixture->World) { Test->AddError(TEXT("Feedback world missing")); return true; }
			if (!P)
			{
				P = Fixture->World->SpawnActor<ADYStagePresentation>();
				if (!P) { Test->AddError(TEXT("Presentation spawn failed")); return true; }
				FDYStageFeedbackTestSeam::SetDuration(*P, 0.2f);
				FDYStageFeedbackTestSeam::Activate(*P);
				FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Near, true);
				Test->TestEqual(TEXT("Cancel displays Interrupted"), P->GetPlayerFeedbackDisplay(), EDYStageFeedbackDisplay::Interrupted);
				Test->TestTrue(TEXT("Real one-shot exists"), FDYStageFeedbackTestSeam::HasTimer(*P));
				Fixture->World->GetTimerManager().Tick(0.01f); // Pending -> Active.
				LastFrame = GFrameCounter;
				return false;
			}
			if (GFrameCounter == LastFrame) { return false; }
			EDYStageFeedbackDisplay Expected = EDYStageFeedbackDisplay::Hidden;
			switch (Scenario)
			{
			case ETimerScenario::Restore:
				FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Far);
				Test->TestEqual(TEXT("New baseline does not swallow overlay"), P->GetPlayerFeedbackDisplay(), EDYStageFeedbackDisplay::Interrupted);
				Expected = EDYStageFeedbackDisplay::Adjust;
				break;
			case ETimerScenario::Hold:
				FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Holding);
				Expected = EDYStageFeedbackDisplay::Holding;
				break;
			case ETimerScenario::Resolve:
				FDYStageFeedbackTestSeam::Resolve(*P);
				Expected = EDYStageFeedbackDisplay::Complete;
				break;
			case ETimerScenario::Activate:
				FDYStageFeedbackTestSeam::Activate(*P);
				Expected = EDYStageFeedbackDisplay::Hidden;
				break;
			case ETimerScenario::DuplicateCancel:
				{
					const float Before = FDYStageFeedbackTestSeam::Remaining(*P);
					FDYStageFeedbackTestSeam::Cancel(*P);
					Test->TestEqual(TEXT("Duplicate cancel does not extend timer"), FDYStageFeedbackTestSeam::Remaining(*P), Before);
					Expected = EDYStageFeedbackDisplay::Near;
				}
				break;
			}
			if (Scenario == ETimerScenario::Hold || Scenario == ETimerScenario::Resolve || Scenario == ETimerScenario::Activate)
			{
				Test->TestFalse(TEXT("New state canceled the timer"), FDYStageFeedbackTestSeam::HasTimer(*P));
				Test->TestEqual(TEXT("New state shown immediately"), P->GetPlayerFeedbackDisplay(), Expected);
			}
			Fixture->World->GetTimerManager().Tick(0.4f); // Actual timer expiry, later ENGINE frame.
			Test->TestFalse(TEXT("No timer remains past original expiry"), FDYStageFeedbackTestSeam::HasTimer(*P));
			Test->TestEqual(TEXT("Expiry restores or preserves correct display"), P->GetPlayerFeedbackDisplay(), Expected);
			return true;
		}
	private:
		FAutomationTestBase* Test;
		ETimerScenario Scenario;
		TSharedPtr<FScopedWorld> Fixture;
		ADYStagePresentation* P = nullptr; // Fixture owns the world throughout the latent command.
		uint64 LastFrame = 0;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFeedbackMappingTest, "DengYingShanHai.M2.Feedback.DisplayMapping", DYFeedbackTests::Flags)
bool FDYFeedbackMappingTest::RunTest(const FString& Parameters)
{
	DYFeedbackTests::FScopedWorld Fixture;
	ADYStagePresentation* P = Fixture.World ? Fixture.World->SpawnActor<ADYStagePresentation>() : nullptr;
	if (!TestNotNull(TEXT("Presentation"), P)) { return false; }
	const TPair<EDYPuzzleFeedbackState, EDYStageFeedbackDisplay> Cases[] = {
		{EDYPuzzleFeedbackState::Far, EDYStageFeedbackDisplay::Adjust},
		{EDYPuzzleFeedbackState::Near, EDYStageFeedbackDisplay::Near},
		{EDYPuzzleFeedbackState::InsideTarget, EDYStageFeedbackDisplay::Holding},
		{EDYPuzzleFeedbackState::Holding, EDYStageFeedbackDisplay::Holding},
		{EDYPuzzleFeedbackState::Resolved, EDYStageFeedbackDisplay::Complete},
		{EDYPuzzleFeedbackState::InvalidSample, EDYStageFeedbackDisplay::Hidden}};
	for (const auto& Pair : Cases)
	{
		FDYStageFeedbackTestSeam::Sample(*P, Pair.Key);
		TestEqual(TEXT("Product feedback mapping"), P->GetFeedbackDisplay(), Pair.Value);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFeedbackNotificationsTest, "DengYingShanHai.M2.Feedback.NoDuplicateNotifications", DYFeedbackTests::Flags)
bool FDYFeedbackNotificationsTest::RunTest(const FString& Parameters)
{
	DYFeedbackTests::FScopedWorld Fixture;
	ADYStagePresentation* P = Fixture.World ? Fixture.World->SpawnActor<ADYStagePresentation>() : nullptr;
	if (!TestNotNull(TEXT("Presentation"), P)) { return false; }
	int32 Count = 0;
	const FDelegateHandle Handle = P->OnFeedbackDisplayChanged().AddLambda([&Count](EDYStageFeedbackDisplay) { ++Count; });
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Holding);
	TestEqual(TEXT("Holding notified once"), Count, 1);
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Near, true);
	FDYStageFeedbackTestSeam::Cancel(*P);
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Near);
	TestEqual(TEXT("Two cancel sources produce one notification"), Count, 2);
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Resolved);
	FDYStageFeedbackTestSeam::Resolve(*P);
	TestEqual(TEXT("Complete notified once"), Count, 3);
	P->OnFeedbackDisplayChanged().Remove(Handle);
	return true;
}

#define DY_FEEDBACK_TIMER_TEST(ClassName, Path, ScenarioName) \
IMPLEMENT_SIMPLE_AUTOMATION_TEST(ClassName, Path, DYFeedbackTests::Flags) \
bool ClassName::RunTest(const FString& Parameters) \
{ \
	FAutomationTestFramework::Get().EnqueueLatentCommand(MakeShared<DYFeedbackTests::FTimerScenarioCommand>(this, DYFeedbackTests::ETimerScenario::ScenarioName)); \
	return true; \
}

DY_FEEDBACK_TIMER_TEST(FDYFeedbackRestoreTest, "DengYingShanHai.M2.Feedback.Timer.RestoresLatestBaseline", Restore)
DY_FEEDBACK_TIMER_TEST(FDYFeedbackHoldTest, "DengYingShanHai.M2.Feedback.Timer.HoldCancels", Hold)
DY_FEEDBACK_TIMER_TEST(FDYFeedbackResolveTest, "DengYingShanHai.M2.Feedback.Timer.ResolveCancels", Resolve)
DY_FEEDBACK_TIMER_TEST(FDYFeedbackActivateTest, "DengYingShanHai.M2.Feedback.Timer.ActivateCancels", Activate)
DY_FEEDBACK_TIMER_TEST(FDYFeedbackDuplicateCancelTest, "DengYingShanHai.M2.Feedback.Timer.DuplicateCancelDoesNotExtend", DuplicateCancel)
#undef DY_FEEDBACK_TIMER_TEST

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFeedbackRegistrationTest, "DengYingShanHai.M2.Feedback.HUD.RegistrationOrderAndTeardown", DYFeedbackTests::Flags)
bool FDYFeedbackRegistrationTest::RunTest(const FString& Parameters)
{
	DYFeedbackTests::FScopedWorld Fixture;
	if (!TestNotNull(TEXT("World"), Fixture.World)) { return false; }
	ADYStageGameMode* Mode = Fixture.World->SpawnActor<ADYStageGameMode>();
	ADYStagePresentation* P = Fixture.World->SpawnActor<ADYStagePresentation>();
	ADYStagePresentation* Replacement = Fixture.World->SpawnActor<ADYStagePresentation>();
	ADYDevInteractionHUD* HUD = Fixture.World->SpawnActor<ADYDevInteractionHUD>();
	if (!Mode || !P || !Replacement || !HUD) { AddError(TEXT("Registration fixture incomplete")); return false; }
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Holding);
	Mode->RegisterStagePresentation(P);
	FDYStageFeedbackTestSeam::Bind(*HUD, Mode); // Presentation first.
	TestEqual(TEXT("Late HUD reads snapshot without replay"), FDYStageFeedbackTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Holding);
	Mode->UnregisterStagePresentation(P);
	TestEqual(TEXT("Unregister hides HUD"), FDYStageFeedbackTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Hidden);
	FDYStageFeedbackTestSeam::Bind(*HUD, Mode); // HUD first.
	Mode->RegisterStagePresentation(P);
	Mode->RegisterStagePresentation(P);
	TestEqual(TEXT("Later and duplicate registration reach HUD"), FDYStageFeedbackTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Holding);
	FDYStageFeedbackTestSeam::Sample(*Replacement, EDYPuzzleFeedbackState::Near);
	Mode->RegisterStagePresentation(Replacement);
	Mode->UnregisterStagePresentation(P);
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Far);
	TestEqual(TEXT("Old actor cannot clear or update replacement"), FDYStageFeedbackTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Near);
	FDYStageFeedbackTestSeam::Unbind(*HUD);
	FDYStageFeedbackTestSeam::Sample(*Replacement, EDYPuzzleFeedbackState::Holding);
	TestEqual(TEXT("Teardown stops updates"), FDYStageFeedbackTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Hidden);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFeedbackGateTest, "DengYingShanHai.M2.Feedback.DevIsolation", DYFeedbackTests::Flags)
bool FDYFeedbackGateTest::RunTest(const FString& Parameters)
{
	TestTrue(TEXT("Dev map"), IsDevContentPackage(TEXT("/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab")));
	TestTrue(TEXT("Real PIE short-name prefix"), IsDevContentPackage(TEXT("/Game/DengYingShanHai/Dev/M2/Maps/UEDPIE_0_LV_M2PuzzleLab")));
	TestFalse(TEXT("Not a nested lookalike"), IsDevContentPackage(TEXT("/Game/Other/DengYingShanHai/Dev/Map")));
	TestFalse(TEXT("Not a similarly named folder"), IsDevContentPackage(TEXT("/Game/DengYingShanHai/Devotional/Map")));
	DYFeedbackTests::FScopedWorld Fixture(false);
	if (!TestNotNull(TEXT("Non-Dev world"), Fixture.World)) { return false; }
	ADYStagePresentation* P = Fixture.World->SpawnActor<ADYStagePresentation>();
	ADYStageGameMode* Mode = Fixture.World->SpawnActor<ADYStageGameMode>();
	if (!P || !Mode) { AddError(TEXT("Isolation fixture incomplete")); return false; }
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Near, true);
	Mode->RegisterStagePresentation(P);
	TestEqual(TEXT("Non-Dev has no display"), P->GetFeedbackDisplay(), EDYStageFeedbackDisplay::Hidden);
	// ADR-013 promotes cosmetic player feedback, not the legacy Dev readout.
	TestEqual(TEXT("Public player sees interruption in non-Dev world"), P->GetPlayerFeedbackDisplay(), EDYStageFeedbackDisplay::Interrupted);
	TestTrue(TEXT("Public player feedback owns the single timer"), FDYStageFeedbackTestSeam::HasTimer(*P));
	TestNull(TEXT("Legacy Dev getter remains isolated"), Mode->GetStagePresentation());
	TestEqual(TEXT("Public registration works outside Dev"), Mode->GetPlayerStagePresentation(), P);
	return true;
}

struct FDYPlayerHUDTestSeam
{
	static void Bind(ADYInteractionHUD& HUD, ADYStageGameMode* Mode) { HUD.BindGameMode(Mode); }
	static void Unbind(ADYInteractionHUD& HUD) { HUD.UnbindGameMode(); }
	static void Pawn(ADYInteractionHUD& HUD, APawn* Pawn) { HUD.BindPawn(Pawn); }
	static EDYStageFeedbackDisplay Cached(const ADYInteractionHUD& HUD) { return HUD.Feedback; }
	static UDYInteractionComponent* Interaction(const ADYInteractionHUD& HUD) { return HUD.BoundInteraction.Get(); }
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYPlayerFeedbackTimerTest, "DengYingShanHai.M2.PlayerUI.NonDevTimerExpiry", DYFeedbackTests::Flags)
bool FDYPlayerFeedbackTimerTest::RunTest(const FString& Parameters)
{
	FAutomationTestFramework::Get().EnqueueLatentCommand(MakeShared<DYFeedbackTests::FTimerScenarioCommand>(this, DYFeedbackTests::ETimerScenario::Restore, false));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYPlayerFeedbackEndTest, "DengYingShanHai.M2.PlayerUI.EndPlayClearsTimer", DYFeedbackTests::Flags)
bool FDYPlayerFeedbackEndTest::RunTest(const FString& Parameters)
{
	DYFeedbackTests::FScopedWorld Fixture(false);
	ADYStagePresentation* P = Fixture.World ? Fixture.World->SpawnActor<ADYStagePresentation>() : nullptr;
	if (!TestNotNull(TEXT("Presentation"), P)) { return false; }
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Near, true);
	TestTrue(TEXT("Public timer armed"), FDYStageFeedbackTestSeam::HasTimer(*P));
	// Invoke the real EndPlay implementation; no duplicate cleanup algorithm.
	FDYStageFeedbackTestSeam::End(*P);
	TestFalse(TEXT("EndPlay clears shared timer"), FDYStageFeedbackTestSeam::HasTimer(*P));
	TestEqual(TEXT("EndPlay clears public display"), P->GetPlayerFeedbackDisplay(), EDYStageFeedbackDisplay::Hidden);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYPlayerHUDRegistrationTest, "DengYingShanHai.M2.PlayerUI.RegistrationAndTeardown", DYFeedbackTests::Flags)
bool FDYPlayerHUDRegistrationTest::RunTest(const FString& Parameters)
{
	DYFeedbackTests::FScopedWorld Fixture(false);
	if (!TestNotNull(TEXT("Non-Dev world"), Fixture.World)) { return false; }
	ADYStageGameMode* Mode = Fixture.World->SpawnActor<ADYStageGameMode>();
	ADYStagePresentation* P = Fixture.World->SpawnActor<ADYStagePresentation>();
	ADYStagePresentation* Replacement = Fixture.World->SpawnActor<ADYStagePresentation>();
	ADYInteractionHUD* HUD = Fixture.World->SpawnActor<ADYInteractionHUD>();
	if (!Mode || !P || !Replacement || !HUD) { AddError(TEXT("Player HUD fixture incomplete")); return false; }
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Holding);
	Mode->RegisterStagePresentation(P);
	FDYPlayerHUDTestSeam::Bind(*HUD, Mode);
	TestEqual(TEXT("Late public HUD reads settled snapshot"), FDYPlayerHUDTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Holding);
	Mode->UnregisterStagePresentation(P);
	TestEqual(TEXT("Unregister clears public HUD"), FDYPlayerHUDTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Hidden);
	FDYPlayerHUDTestSeam::Bind(*HUD, Mode);
	Mode->RegisterStagePresentation(P);
	Mode->RegisterStagePresentation(P);
	TestEqual(TEXT("HUD-first registration works"), FDYPlayerHUDTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Holding);
	FDYStageFeedbackTestSeam::Sample(*Replacement, EDYPuzzleFeedbackState::Near);
	Mode->RegisterStagePresentation(Replacement);
	Mode->UnregisterStagePresentation(P);
	FDYStageFeedbackTestSeam::Sample(*P, EDYPuzzleFeedbackState::Far);
	TestEqual(TEXT("Old publisher cannot clear replacement"), FDYPlayerHUDTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Near);
	FDYPlayerHUDTestSeam::Unbind(*HUD);
	FDYStageFeedbackTestSeam::Sample(*Replacement, EDYPuzzleFeedbackState::Holding);
	TestEqual(TEXT("Unbound public HUD receives no updates"), FDYPlayerHUDTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Hidden);
	FDYPlayerHUDTestSeam::Bind(*HUD, Mode);
	TestEqual(TEXT("Recreated binding reads latest state"), FDYPlayerHUDTestSeam::Cached(*HUD), EDYStageFeedbackDisplay::Holding);
	FDYPlayerHUDTestSeam::Unbind(*HUD);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYPlayerHUDPawnTest, "DengYingShanHai.M2.PlayerUI.PawnRebind", DYFeedbackTests::Flags)
bool FDYPlayerHUDPawnTest::RunTest(const FString& Parameters)
{
	DYFeedbackTests::FScopedWorld Fixture;
	if (!TestNotNull(TEXT("World"), Fixture.World)) { return false; }
	ADYInteractionHUD* HUD = Fixture.World->SpawnActor<ADYInteractionHUD>();
	ADYStageOperatorPawn* A = Fixture.World->SpawnActor<ADYStageOperatorPawn>();
	ADYStageOperatorPawn* B = Fixture.World->SpawnActor<ADYStageOperatorPawn>();
	if (!HUD || !A || !B) { AddError(TEXT("Pawn fixture incomplete")); return false; }
	FDYPlayerHUDTestSeam::Pawn(*HUD, A);
	TestTrue(TEXT("First pawn subscribed"), A->GetInteractionComponent()->OnFocusChanged.IsBound());
	FDYPlayerHUDTestSeam::Pawn(*HUD, B);
	TestFalse(TEXT("Old pawn unsubscribed"), A->GetInteractionComponent()->OnFocusChanged.IsBound());
	TestEqual(TEXT("Replacement component owned by current pawn"), FDYPlayerHUDTestSeam::Interaction(*HUD), B->GetInteractionComponent());
	FDYPlayerHUDTestSeam::Pawn(*HUD, B);
	FDYPlayerHUDTestSeam::Pawn(*HUD, nullptr);
	TestFalse(TEXT("Focus delegate removed"), B->GetInteractionComponent()->OnFocusChanged.IsBound());
	TestFalse(TEXT("Control delegate removed"), B->GetInteractionComponent()->OnControlStateChanged.IsBound());
	TestNull(TEXT("Null pawn clears cached component"), FDYPlayerHUDTestSeam::Interaction(*HUD));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYPlayerHUDTextTest, "DengYingShanHai.M2.PlayerUI.ChineseTextContract", DYFeedbackTests::Flags)
bool FDYPlayerHUDTextTest::RunTest(const FString& Parameters)
{
	TestEqual(TEXT("Explore"), UDYInteractionHUDWidget::GetPromptText(false, false).ToString(), FString(TEXT("对准灯具或皮影")));
	TestEqual(TEXT("Focus"), UDYInteractionHUDWidget::GetPromptText(true, false).ToString(), FString(TEXT("E　操纵")));
	const FString Control = UDYInteractionHUDWidget::GetPromptText(true, true).ToString();
	TestTrue(TEXT("Existing controls only"), Control.Contains(TEXT("A / D")) && Control.Contains(TEXT("放开")) && Control.Contains(TEXT("复位")));
	TestTrue(TEXT("Hidden has no status"), UDYInteractionHUDWidget::GetStatusText(EDYStageFeedbackDisplay::Hidden).IsEmpty());
	for (const EDYStageFeedbackDisplay Display : {EDYStageFeedbackDisplay::Adjust, EDYStageFeedbackDisplay::Near, EDYStageFeedbackDisplay::Holding, EDYStageFeedbackDisplay::Interrupted, EDYStageFeedbackDisplay::Complete})
	{
		const FString Line = UDYInteractionHUDWidget::GetStatusText(Display).ToString();
		TestFalse(TEXT("All five statuses nonempty"), Line.IsEmpty());
		TestFalse(TEXT("No numeric answer data"), Line.Contains(TEXT("Target")) || Line.Contains(TEXT("Progress")) || Line.Contains(TEXT("%")));
	}
	return true;
}

#endif
