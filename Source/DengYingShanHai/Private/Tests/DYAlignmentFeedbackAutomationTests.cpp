#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Core/DYStageGameMode.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Stage/DYStagePresentation.h"
#include "UI/DYInteractionHUD.h"
#include "UI/DYInteractionHUDWidget.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"

#include <limits>

/** Native test access only; never exposed as a player action or a success setter. */
struct FDYAlignmentFeedbackTestSeam
{
	static void Enable(ADYStagePresentation& Stage)
	{
		Stage.bEnablePlayerAlignmentFeedback = true;
		Stage.bStaffPresentationRuntimeActive = true;
	}
	static void Sample(ADYStagePresentation& Stage, const FDYEvaluationResult& Result)
	{
		Stage.HandleEvaluationUpdated(Result);
	}
	static void Activate(ADYStagePresentation& Stage)
	{
		Stage.HandlePuzzleActivated(TEXT("AlignmentTest"));
	}
	static void End(ADYStagePresentation& Stage)
	{
		Stage.EndPlay(EEndPlayReason::Destroyed);
	}
	static void BindHUD(ADYInteractionHUD& HUD, ADYStageGameMode* Mode)
	{
		HUD.BindGameMode(Mode);
	}
	static void UnbindHUD(ADYInteractionHUD& HUD)
	{
		HUD.UnbindGameMode();
	}
	static FDYPlayerAlignmentDisplay HUDSnapshot(const ADYInteractionHUD& HUD)
	{
		return HUD.AlignmentDisplay;
	}
};

namespace DYAlignmentFeedbackTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;

	/** An unsaved, strongly held world. No asset, map, input or Director state is changed. */
	struct FScopedWorld
	{
		FScopedWorld()
		{
			if (!GEngine) { return; }
			const FName Name = MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYAlignmentTestWorld"), EUniqueObjectNameOptions::GloballyUnique);
			UPackage* Package = CreatePackage(*(TEXT("/Game/DengYingShanHai/Dev/Automation/") + Name.ToString()));
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
			if (World && GEngine)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
			StrongWorld.Reset();
		}
		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> StrongWorld;
	};

	FDYEvaluationResult MakeSample(bool bLightReady = false, bool bPuppetReady = false)
	{
		FDYEvaluationResult Result;
		Result.State = EDYPuzzleRuntimeState::Searching;
		Result.Feedback = EDYPuzzleFeedbackState::Near;
		Result.LightPosition.bEnabled = true;
		Result.LightPosition.bIsValid = bLightReady;
		Result.PuppetPosition.bEnabled = true;
		Result.PuppetPosition.bIsValid = bPuppetReady;
		Result.bPuppetPoseEnabled = true;
		Result.bPuppetPoseValid = bPuppetReady;
		Result.bAllRequiredConditionsValid = bLightReady && bPuppetReady;
		Result.HoldRequiredSeconds = 1.25;
		return Result;
	}

	FDYEvaluationResult MakeHolding(double Elapsed)
	{
		FDYEvaluationResult Result = MakeSample(true, true);
		Result.State = EDYPuzzleRuntimeState::Holding;
		Result.Feedback = EDYPuzzleFeedbackState::Holding;
		Result.HoldElapsedSeconds = Elapsed;
		return Result;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentDisabledAndP01Test,
	"DengYingShanHai.Readability.Alignment.Projection.DisabledAndLightOnly", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentDisabledAndP01Test::RunTest(const FString& Parameters)
{
	FDYEvaluationResult Result = DYAlignmentFeedbackTests::MakeSample(true, true);
	const auto Disabled = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, false);
	TestFalse(TEXT("Default-off projection is disabled"), Disabled.bEnabled);
	TestFalse(TEXT("Disabled projection carries no sample"), Disabled.bHasValidSample);
	TestFalse(TEXT("Disabled projection does not announce a lamp"), Disabled.bLightRequired);
	TestFalse(TEXT("Disabled projection does not announce a puppet"), Disabled.bPuppetRequired);
	TestEqual(TEXT("Disabled projection has no hold fill"), Disabled.HoldFraction, 0.0);

	Result.PuppetPosition.bEnabled = false;
	Result.PuppetPosition.bIsValid = true; // The evaluator's disabled-condition convention.
	Result.bPuppetPoseEnabled = false;
	Result.bPuppetPoseValid = true;
	const auto P01 = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestTrue(TEXT("P01 lamp is required"), P01.bLightRequired);
	TestTrue(TEXT("P01 lamp readiness is preserved"), P01.bLightReady);
	TestFalse(TEXT("P01 has no phantom puppet condition"), P01.bPuppetRequired);
	TestFalse(TEXT("P01 does not label a disabled puppet as ready"), P01.bPuppetReady);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentPositionPoseTest,
	"DengYingShanHai.Readability.Alignment.Projection.PositionAndPose", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentPositionPoseTest::RunTest(const FString& Parameters)
{
	FDYEvaluationResult Result = DYAlignmentFeedbackTests::MakeSample(false, true);
	Result.bPuppetPoseValid = false;
	Result.bAllRequiredConditionsValid = false;
	auto Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestTrue(TEXT("Position/pose puppet condition is required"), Display.bPuppetRequired);
	TestFalse(TEXT("Position alone never labels the puppet ready"), Display.bPuppetReady);
	Result.PuppetPosition.bIsValid = false;
	Result.bPuppetPoseValid = true;
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestFalse(TEXT("Pose alone never labels a position-required puppet ready"), Display.bPuppetReady);
	Result.PuppetPosition.bIsValid = true;
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestTrue(TEXT("Both existing evaluator flags label the puppet ready"), Display.bPuppetReady);
	TestFalse(TEXT("Ready puppet does not imply ready lamp"), Display.bLightReady);
	TestFalse(TEXT("One ready object never implies joint readiness"), Display.bJointReady);

	Result.PuppetPosition.bEnabled = false;
	Result.PuppetPosition.bIsValid = true;
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestTrue(TEXT("Pose-only authored condition remains required"), Display.bPuppetRequired);
	TestTrue(TEXT("Pose-only authored condition uses its evaluator validity"), Display.bPuppetReady);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentHoldProjectionTest,
	"DengYingShanHai.Readability.Alignment.Projection.HoldNotOverlapScore", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentHoldProjectionTest::RunTest(const FString& Parameters)
{
	FDYEvaluationResult Result = DYAlignmentFeedbackTests::MakeHolding(0.25);
	Result.Progress = 0.99;
	auto Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestTrue(TEXT("Joint readiness is the evaluator fact"), Display.bJointReady);
	TestTrue(TEXT("Existing Holding state is presented"), Display.bHolding);
	TestTrue(TEXT("Fill uses elapsed / required, never parameter score"), FMath::IsNearlyEqual(Display.HoldFraction, 0.2));
	Result.Progress = 0.03;
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestTrue(TEXT("Changing score alone cannot change the hold bar"), FMath::IsNearlyEqual(Display.HoldFraction, 0.2));
	Result.HoldElapsedSeconds = 4.0;
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestEqual(TEXT("Finite overrun is clamped"), Display.HoldFraction, 1.0);
	Result.HoldElapsedSeconds = -0.5;
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestEqual(TEXT("Negative elapsed cannot underflow the bar"), Display.HoldFraction, 0.0);
	Result.State = EDYPuzzleRuntimeState::Searching;
	Result.Feedback = EDYPuzzleFeedbackState::Near;
	Result.bAllRequiredConditionsValid = false;
	Result.bHoldCanceled = true;
	Result.HoldElapsedSeconds = 0.9; // Stale time must never survive a cancellation.
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestFalse(TEXT("Canceled sample is not Holding"), Display.bHolding);
	TestEqual(TEXT("Cancellation clears the fill"), Display.HoldFraction, 0.0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentInvalidFiniteTest,
	"DengYingShanHai.Readability.Alignment.Projection.InvalidAndNonFinite", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentInvalidFiniteTest::RunTest(const FString& Parameters)
{
	FDYEvaluationResult Result = DYAlignmentFeedbackTests::MakeHolding(0.5);
	for (const double Required : {0.0, -1.0, std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::infinity()})
	{
		Result.HoldRequiredSeconds = Required;
		const auto Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
		TestTrue(TEXT("Invalid duration never exports a nonfinite fill"), FMath::IsFinite(Display.HoldFraction));
		TestEqual(TEXT("Invalid duration has no fabricated completion"), Display.HoldFraction, 0.0);
	}
	Result.HoldRequiredSeconds = 1.25;
	for (const double Elapsed : {std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::infinity()})
	{
		Result.HoldElapsedSeconds = Elapsed;
		const auto Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
		TestTrue(TEXT("Invalid elapsed never exports a nonfinite fill"), FMath::IsFinite(Display.HoldFraction));
		TestEqual(TEXT("Invalid elapsed is not a fabricated overlap rate"), Display.HoldFraction, 0.0);
	}
	Result.Feedback = EDYPuzzleFeedbackState::InvalidSample;
	Result.State = EDYPuzzleRuntimeState::Searching;
	auto Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestFalse(TEXT("Invalid sample is not advertised"), Display.bHasValidSample);
	TestFalse(TEXT("Invalid sample never holds"), Display.bHolding);
	TestEqual(TEXT("Invalid sample has empty hold fill"), Display.HoldFraction, 0.0);
	Result.State = EDYPuzzleRuntimeState::Resolved;
	Result.Feedback = EDYPuzzleFeedbackState::Resolved;
	Result.HoldElapsedSeconds = 1.25;
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(Result, true);
	TestFalse(TEXT("Resolve is not an ongoing player hold"), Display.bHolding);
	TestEqual(TEXT("Resolve hands over to existing terminal presentation"), Display.HoldFraction, 0.0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentSameNearTest,
	"DengYingShanHai.Readability.Alignment.Stage.SameNearAndActivationClear", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentSameNearTest::RunTest(const FString& Parameters)
{
	DYAlignmentFeedbackTests::FScopedWorld Fixture;
	ADYStagePresentation* Stage = Fixture.World ? Fixture.World->SpawnActor<ADYStagePresentation>() : nullptr;
	if (!TestNotNull(TEXT("Presentation"), Stage)) { return false; }
	FDYAlignmentFeedbackTestSeam::Enable(*Stage);
	int32 Changes = 0;
	const FDelegateHandle Handle = Stage->OnPlayerAlignmentDisplayChanged().AddLambda([&](const FDYPlayerAlignmentDisplay&) { ++Changes; });
	FDYEvaluationResult Result = DYAlignmentFeedbackTests::MakeSample(false, false);
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, Result);
	TestEqual(TEXT("Initial valid sample is published"), Changes, 1);
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, Result);
	TestEqual(TEXT("Identical display snapshot is not spammed"), Changes, 1);
	Result.LightPosition.bIsValid = true;
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, Result);
	TestEqual(TEXT("Same Near with newly ready lamp is published"), Changes, 2);
	TestTrue(TEXT("Lamp readiness reaches the current getter"), Stage->GetPlayerAlignmentDisplay().bLightReady);
	Result.LightPosition.bIsValid = false;
	Result.PuppetPosition.bIsValid = true;
	Result.bPuppetPoseValid = true;
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, Result);
	TestEqual(TEXT("Same Near with newly ready puppet is published"), Changes, 3);
	TestTrue(TEXT("Puppet readiness reaches the current getter"), Stage->GetPlayerAlignmentDisplay().bPuppetReady);
	TestFalse(TEXT("Prior lamp readiness did not remain stale"), Stage->GetPlayerAlignmentDisplay().bLightReady);
	FDYAlignmentFeedbackTestSeam::Activate(*Stage);
	const auto Cleared = Stage->GetPlayerAlignmentDisplay();
	TestFalse(TEXT("New activation clears old readiness sample"), Cleared.bHasValidSample);
	TestFalse(TEXT("New activation clears old hold"), Cleared.bHolding);
	TestEqual(TEXT("New activation clears old fill"), Cleared.HoldFraction, 0.0);
	Stage->OnPlayerAlignmentDisplayChanged().Remove(Handle);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentHoldingCadenceTest,
	"DengYingShanHai.Readability.Alignment.Stage.HoldingElapsedAndCancel", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentHoldingCadenceTest::RunTest(const FString& Parameters)
{
	DYAlignmentFeedbackTests::FScopedWorld Fixture;
	ADYStagePresentation* Stage = Fixture.World ? Fixture.World->SpawnActor<ADYStagePresentation>() : nullptr;
	if (!TestNotNull(TEXT("Presentation"), Stage)) { return false; }
	FDYAlignmentFeedbackTestSeam::Enable(*Stage);
	int32 Changes = 0;
	const FDelegateHandle Handle = Stage->OnPlayerAlignmentDisplayChanged().AddLambda([&](const FDYPlayerAlignmentDisplay&) { ++Changes; });
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, DYAlignmentFeedbackTests::MakeHolding(0.1));
	TestEqual(TEXT("First Holding snapshot is published"), Changes, 1);
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, DYAlignmentFeedbackTests::MakeHolding(0.4));
	TestEqual(TEXT("Elapsed change is published despite same feedback enum"), Changes, 2);
	TestTrue(TEXT("Hold fill follows latest existing elapsed time"), FMath::IsNearlyEqual(Stage->GetPlayerAlignmentDisplay().HoldFraction, 0.32));
	FDYEvaluationResult Canceled = DYAlignmentFeedbackTests::MakeSample(true, false);
	Canceled.bHoldCanceled = true;
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, Canceled);
	TestEqual(TEXT("Existing interruption text remains authoritative"), Stage->GetPlayerFeedbackDisplay(), EDYStageFeedbackDisplay::Interrupted);
	TestFalse(TEXT("Interrupted alignment is not holding"), Stage->GetPlayerAlignmentDisplay().bHolding);
	TestEqual(TEXT("Interrupted alignment immediately empties the bar"), Stage->GetPlayerAlignmentDisplay().HoldFraction, 0.0);
	Stage->OnPlayerAlignmentDisplayChanged().Remove(Handle);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentIsolationEndPlayTest,
	"DengYingShanHai.Readability.Alignment.Stage.DefaultOffAndEndPlay", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentIsolationEndPlayTest::RunTest(const FString& Parameters)
{
	DYAlignmentFeedbackTests::FScopedWorld Fixture;
	ADYStagePresentation* Stage = Fixture.World ? Fixture.World->SpawnActor<ADYStagePresentation>() : nullptr;
	if (!TestNotNull(TEXT("Presentation"), Stage)) { return false; }
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, DYAlignmentFeedbackTests::MakeHolding(0.4));
	TestFalse(TEXT("Existing stages remain default-off"), Stage->GetPlayerAlignmentDisplay().bEnabled);
	FDYAlignmentFeedbackTestSeam::Enable(*Stage);
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, DYAlignmentFeedbackTests::MakeHolding(0.4));
	TestTrue(TEXT("Opt-in stage can publish a holding display"), Stage->GetPlayerAlignmentDisplay().bHolding);
	FDYAlignmentFeedbackTestSeam::End(*Stage);
	const auto Ended = Stage->GetPlayerAlignmentDisplay();
	TestFalse(TEXT("EndPlay disables the new display"), Ended.bEnabled);
	TestFalse(TEXT("EndPlay has no valid alignment sample"), Ended.bHasValidSample);
	TestFalse(TEXT("EndPlay cannot retain an old Holding display"), Ended.bHolding);
	TestEqual(TEXT("EndPlay clears the hold fraction"), Ended.HoldFraction, 0.0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentEndReentryTest,
	"DengYingShanHai.Readability.Alignment.Stage.MulticastEndPlayReentry", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentEndReentryTest::RunTest(const FString& Parameters)
{
	DYAlignmentFeedbackTests::FScopedWorld Fixture;
	ADYStagePresentation* Stage = Fixture.World ? Fixture.World->SpawnActor<ADYStagePresentation>() : nullptr;
	if (!TestNotNull(TEXT("Presentation"), Stage)) { return false; }
	FDYAlignmentFeedbackTestSeam::Enable(*Stage);
	bool bEnded = false;
	bool bLaterListenerSawSettledEmpty = false;
	const FDelegateHandle EndHandle = Stage->OnPlayerAlignmentDisplayChanged().AddLambda([&](const FDYPlayerAlignmentDisplay& Snapshot)
	{
		if (!bEnded && Snapshot.bHolding)
		{
			bEnded = true; // Consume before the nested clearing notification.
			FDYAlignmentFeedbackTestSeam::End(*Stage);
		}
	});
	const FDelegateHandle ReadHandle = Stage->OnPlayerAlignmentDisplayChanged().AddLambda([&](const FDYPlayerAlignmentDisplay&)
	{
		if (bEnded)
		{
			const auto Settled = Stage->GetPlayerAlignmentDisplay();
			bLaterListenerSawSettledEmpty = !Settled.bEnabled && !Settled.bHolding && Settled.HoldFraction == 0.0;
		}
	});
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, DYAlignmentFeedbackTests::MakeHolding(0.4));
	TestTrue(TEXT("Actual multicast listener invoked EndPlay"), bEnded);
	TestTrue(TEXT("Later listener can read settled empty state, not stale payload"), bLaterListenerSawSettledEmpty);
	TestFalse(TEXT("Outer notification cannot resurrect an ended display"), Stage->GetPlayerAlignmentDisplay().bHolding);
	Stage->OnPlayerAlignmentDisplayChanged().Remove(EndHandle);
	Stage->OnPlayerAlignmentDisplayChanged().Remove(ReadHandle);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentTextTest,
	"DengYingShanHai.Readability.Alignment.UI.ReadinessTextAndLegacyIsolation", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentTextTest::RunTest(const FString& Parameters)
{
	auto Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(DYAlignmentFeedbackTests::MakeSample(false, false), true);
	TestEqual(TEXT("Neither condition ready explains both controls"),
		UDYInteractionHUDWidget::GetAlignmentStatusText(Display, EDYStageFeedbackDisplay::Near).ToString(), FString(TEXT("继续调整灯与偶")));
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(DYAlignmentFeedbackTests::MakeSample(false, true), true);
	TestEqual(TEXT("Puppet-ready status directs the remaining lamp control"),
		UDYInteractionHUDWidget::GetAlignmentStatusText(Display, EDYStageFeedbackDisplay::Near).ToString(), FString(TEXT("偶已就位，继续调灯")));
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(DYAlignmentFeedbackTests::MakeSample(true, false), true);
	TestEqual(TEXT("Lamp-ready status directs the remaining puppet control"),
		UDYInteractionHUDWidget::GetAlignmentStatusText(Display, EDYStageFeedbackDisplay::Near).ToString(), FString(TEXT("灯已就位，继续调偶")));
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(DYAlignmentFeedbackTests::MakeHolding(0.4), true);
	const FString Holding = UDYInteractionHUDWidget::GetAlignmentStatusText(Display, EDYStageFeedbackDisplay::Holding).ToString();
	TestTrue(TEXT("Joint Holding teaches release of existing adjustment keys"), Holding.Contains(TEXT("灯偶已到位")) && Holding.Contains(TEXT("A / D")) && Holding.Contains(TEXT("保持此刻")));
	TestEqual(TEXT("Interruption overrides a stale ready snapshot"),
		UDYInteractionHUDWidget::GetAlignmentStatusText(Display, EDYStageFeedbackDisplay::Interrupted).ToString(), FString(TEXT("贴合被打断，轻调后再保持")));
	TestEqual(TEXT("Existing complete text has priority"),
		UDYInteractionHUDWidget::GetAlignmentStatusText(Display, EDYStageFeedbackDisplay::Complete).ToString(),
		UDYInteractionHUDWidget::GetStatusText(EDYStageFeedbackDisplay::Complete).ToString());
	const FString Readiness = UDYInteractionHUDWidget::GetAlignmentReadinessText(Display).ToString();
	TestTrue(TEXT("Both readiness labels are present"), Readiness.Contains(TEXT("灯：已就位")) && Readiness.Contains(TEXT("偶：已就位")));
	TestFalse(TEXT("Readiness is not a percentage or numeric target"), Readiness.Contains(TEXT("%")) || Readiness.Contains(TEXT("Target")) || Readiness.Contains(TEXT("Progress")));
	FDYEvaluationResult P01Result = DYAlignmentFeedbackTests::MakeHolding(0.4);
	P01Result.PuppetPosition.bEnabled = false;
	P01Result.bPuppetPoseEnabled = false;
	Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(P01Result, true);
	TestFalse(TEXT("Light-only readiness never mentions a phantom puppet"), UDYInteractionHUDWidget::GetAlignmentReadinessText(Display).ToString().Contains(TEXT("偶")));
	const FDYPlayerAlignmentDisplay Disabled;
	TestTrue(TEXT("Disabled readiness is absent"), UDYInteractionHUDWidget::GetAlignmentReadinessText(Disabled).IsEmpty());
	for (const auto Feedback : {EDYStageFeedbackDisplay::Hidden, EDYStageFeedbackDisplay::Adjust, EDYStageFeedbackDisplay::Near, EDYStageFeedbackDisplay::Holding, EDYStageFeedbackDisplay::Interrupted, EDYStageFeedbackDisplay::Complete})
	{
		TestEqual(TEXT("Default-off preserves each old status string"),
			UDYInteractionHUDWidget::GetAlignmentStatusText(Disabled, Feedback).ToString(), UDYInteractionHUDWidget::GetStatusText(Feedback).ToString());
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentBarVisibilityTest,
	"DengYingShanHai.Readability.Alignment.UI.HoldBarStateGate", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentBarVisibilityTest::RunTest(const FString& Parameters)
{
	auto Display = ADYStagePresentation::BuildPlayerAlignmentDisplay(DYAlignmentFeedbackTests::MakeHolding(0.4), true);
	TestTrue(TEXT("Bar is visible only for a live joint hold"), UDYInteractionHUDWidget::ShouldShowHoldProgress(Display, EDYStageFeedbackDisplay::Holding));
	for (const auto Feedback : {EDYStageFeedbackDisplay::Hidden, EDYStageFeedbackDisplay::Adjust, EDYStageFeedbackDisplay::Near, EDYStageFeedbackDisplay::Interrupted, EDYStageFeedbackDisplay::Complete})
	{
		TestFalse(TEXT("Non-Holding cosmetic state hides the bar even with stale snapshot"), UDYInteractionHUDWidget::ShouldShowHoldProgress(Display, Feedback));
	}
	Display.bEnabled = false;
	TestFalse(TEXT("Default-off stage never mounts a hold bar"), UDYInteractionHUDWidget::ShouldShowHoldProgress(Display, EDYStageFeedbackDisplay::Holding));
	Display.bEnabled = true;
	Display.bHasValidSample = false;
	TestFalse(TEXT("No sample hides the hold bar"), UDYInteractionHUDWidget::ShouldShowHoldProgress(Display, EDYStageFeedbackDisplay::Holding));
	Display.bHasValidSample = true;
	Display.bJointReady = false;
	TestFalse(TEXT("One ready object never displays joint Holding"), UDYInteractionHUDWidget::ShouldShowHoldProgress(Display, EDYStageFeedbackDisplay::Holding));
	Display.bJointReady = true;
	Display.bHolding = false;
	TestFalse(TEXT("Ready flags alone do not start a UI clock"), UDYInteractionHUDWidget::ShouldShowHoldProgress(Display, EDYStageFeedbackDisplay::Holding));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentHUDLifecycleTest,
	"DengYingShanHai.Readability.Alignment.HUD.LateAttachReplaceAndDetach", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentHUDLifecycleTest::RunTest(const FString& Parameters)
{
	DYAlignmentFeedbackTests::FScopedWorld Fixture;
	if (!TestNotNull(TEXT("World"), Fixture.World)) { return false; }
	ADYStageGameMode* Mode = Fixture.World->SpawnActor<ADYStageGameMode>();
	ADYStagePresentation* Original = Fixture.World->SpawnActor<ADYStagePresentation>();
	ADYStagePresentation* Replacement = Fixture.World->SpawnActor<ADYStagePresentation>();
	ADYInteractionHUD* HUD = Fixture.World->SpawnActor<ADYInteractionHUD>();
	if (!Mode || !Original || !Replacement || !HUD) { AddError(TEXT("Alignment HUD fixture incomplete")); return false; }
	FDYAlignmentFeedbackTestSeam::Enable(*Original);
	FDYAlignmentFeedbackTestSeam::Enable(*Replacement);
	FDYAlignmentFeedbackTestSeam::Sample(*Original, DYAlignmentFeedbackTests::MakeSample(true, false));
	Mode->RegisterStagePresentation(Original);
	FDYAlignmentFeedbackTestSeam::BindHUD(*HUD, Mode);
	auto Cached = FDYAlignmentFeedbackTestSeam::HUDSnapshot(*HUD);
	TestTrue(TEXT("Late native HUD reads settled lamp-ready display"), Cached.bLightReady);
	TestFalse(TEXT("Late native HUD does not invent puppet readiness"), Cached.bPuppetReady);
	Mode->RegisterStagePresentation(Original); // A duplicate registration is a no-op.
	FDYAlignmentFeedbackTestSeam::Sample(*Replacement, DYAlignmentFeedbackTests::MakeSample(false, true));
	Mode->RegisterStagePresentation(Replacement);
	Cached = FDYAlignmentFeedbackTestSeam::HUDSnapshot(*HUD);
	TestTrue(TEXT("Replacement publisher supplies its settled puppet-ready display"), Cached.bPuppetReady);
	TestFalse(TEXT("Replacement clears original lamp-ready display"), Cached.bLightReady);
	Mode->UnregisterStagePresentation(Original);
	FDYAlignmentFeedbackTestSeam::Sample(*Original, DYAlignmentFeedbackTests::MakeHolding(0.8));
	Cached = FDYAlignmentFeedbackTestSeam::HUDSnapshot(*HUD);
	TestTrue(TEXT("Old unregister/update cannot replace current puppet readiness"), Cached.bPuppetReady);
	TestFalse(TEXT("Old publisher cannot start Holding in replacement HUD"), Cached.bHolding);
	FDYAlignmentFeedbackTestSeam::UnbindHUD(*HUD);
	Cached = FDYAlignmentFeedbackTestSeam::HUDSnapshot(*HUD);
	TestFalse(TEXT("Native HUD detach clears feature display"), Cached.bEnabled);
	TestFalse(TEXT("Native HUD detach clears valid sample"), Cached.bHasValidSample);
	FDYAlignmentFeedbackTestSeam::Sample(*Replacement, DYAlignmentFeedbackTests::MakeHolding(0.8));
	TestFalse(TEXT("Unbound publisher cannot refill detached native HUD"), FDYAlignmentFeedbackTestSeam::HUDSnapshot(*HUD).bHolding);
	FDYAlignmentFeedbackTestSeam::BindHUD(*HUD, Mode);
	TestTrue(TEXT("Recreated binding reads current publisher without replaying evaluation"), FDYAlignmentFeedbackTestSeam::HUDSnapshot(*HUD).bHolding);
	FDYAlignmentFeedbackTestSeam::UnbindHUD(*HUD);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYAlignmentHUDReentryTest,
	"DengYingShanHai.Readability.Alignment.HUD.EarlierObserverEndPlayReentry", DYAlignmentFeedbackTests::Flags)
bool FDYAlignmentHUDReentryTest::RunTest(const FString& Parameters)
{
	DYAlignmentFeedbackTests::FScopedWorld Fixture;
	if (!TestNotNull(TEXT("World"), Fixture.World)) { return false; }
	ADYStageGameMode* Mode = Fixture.World->SpawnActor<ADYStageGameMode>();
	ADYStagePresentation* Stage = Fixture.World->SpawnActor<ADYStagePresentation>();
	ADYInteractionHUD* HUD = Fixture.World->SpawnActor<ADYInteractionHUD>();
	if (!Mode || !Stage || !HUD) { AddError(TEXT("Alignment HUD reentry fixture incomplete")); return false; }
	FDYAlignmentFeedbackTestSeam::Enable(*Stage);
	bool bEnded = false;
	const FDelegateHandle EndHandle = Stage->OnPlayerAlignmentDisplayChanged().AddLambda([&](const FDYPlayerAlignmentDisplay& Snapshot)
	{
		if (!bEnded && Snapshot.bHolding)
		{
			bEnded = true;
			FDYAlignmentFeedbackTestSeam::End(*Stage);
		}
	});
	Mode->RegisterStagePresentation(Stage);
	FDYAlignmentFeedbackTestSeam::BindHUD(*HUD, Mode); // The destructive observer precedes HUD in the multicast.
	FDYAlignmentFeedbackTestSeam::Sample(*Stage, DYAlignmentFeedbackTests::MakeHolding(0.4));
	TestTrue(TEXT("Earlier actual listener ended Stage during a Holding notification"), bEnded);
	const auto Cached = FDYAlignmentFeedbackTestSeam::HUDSnapshot(*HUD);
	TestFalse(TEXT("HUD rereads settled Stage getter instead of stale Holding payload"), Cached.bHolding);
	TestFalse(TEXT("Ended publisher cannot leave feature enabled in HUD"), Cached.bEnabled);
	TestEqual(TEXT("Ended publisher cannot leave stale bar fill in HUD"), Cached.HoldFraction, 0.0);
	Stage->OnPlayerAlignmentDisplayChanged().Remove(EndHandle);
	FDYAlignmentFeedbackTestSeam::UnbindHUD(*HUD);
	return true;
}

#endif
