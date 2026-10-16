#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Puzzles/DYPuzzleDefinition.h"
#include "Puzzles/DYPuzzleEvaluatorComponent.h"
#include "Stage/DYStageEnvironment.h"
#include "Stage/DYStagePresentation.h"

namespace DYM2Tests
{
	constexpr EAutomationTestFlags TestFlags =
		EAutomationTestFlags::EditorContext |
		EAutomationTestFlags::EngineFilter;

	UDYPuzzleDefinition* MakeCombinedDefinition()
	{
		UDYPuzzleDefinition* Definition = NewObject<UDYPuzzleDefinition>();
		Definition->PuzzleId = TEXT("P02_ChaseForm_Dev");
		Definition->LightPosition.bEnabled = true;
		Definition->LightPosition.Target = 0.72;
		Definition->LightPosition.EnterTolerance = 0.05;
		Definition->LightPosition.ExitTolerance = 0.08;
		Definition->PuppetPosition.bEnabled = true;
		Definition->PuppetPosition.Target = 0.80;
		Definition->PuppetPosition.EnterTolerance = 0.05;
		Definition->PuppetPosition.ExitTolerance = 0.09;
		Definition->RequiredPuppetPoseId = TEXT("P02_StrideReach");
		Definition->RequiredHoldSeconds = 1.0;
		return Definition;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYM2CombinedConditionsTest,
	"DengYingShanHai.M2.Evaluator.CombinedConditions",
	DYM2Tests::TestFlags)

bool FDYM2CombinedConditionsTest::RunTest(const FString& Parameters)
{
	UDYPuzzleDefinition* Definition = DYM2Tests::MakeCombinedDefinition();
	UDYPuzzleEvaluatorComponent* Evaluator = NewObject<UDYPuzzleEvaluatorComponent>();
	FDYPuzzleSample Sample;
	Sample.bIsValid = true;
	Sample.LightPosition = Definition->LightPosition.Target;
	Sample.PuppetPosition = Definition->PuppetPosition.Target;
	Sample.PuppetPoseId = TEXT("P02_StrideMid");

	FDYEvaluationResult Result = Evaluator->Evaluate(Sample, Definition, 0.25);
	TestTrue(TEXT("Light condition is independently valid"), Result.LightPosition.bIsValid);
	TestTrue(TEXT("Puppet-position condition is independently valid"), Result.PuppetPosition.bIsValid);
	TestFalse(TEXT("Wrong authored pose blocks the combined result"), Result.bPuppetPoseValid);
	TestFalse(TEXT("Holding does not start until every condition is valid"), Result.bAllRequiredConditionsValid);
	TestEqual(TEXT("Blocked conditions keep the evaluator searching"), Result.State, EDYPuzzleRuntimeState::Searching);

	Sample.PuppetPoseId = Definition->RequiredPuppetPoseId;
	Result = Evaluator->Evaluate(Sample, Definition, 0.4);
	TestTrue(TEXT("Correct light, puppet position and pose start holding"), Result.bHoldStarted);
	TestEqual(TEXT("Combined puzzle enters Holding"), Result.State, EDYPuzzleRuntimeState::Holding);
	TestEqual(TEXT("Holding uses supplied real-world delta"), Result.HoldElapsedSeconds, 0.4);

	Sample.LightPosition = 0.20;
	Result = Evaluator->Evaluate(Sample, Definition, 0.3);
	TestTrue(TEXT("Losing either controlled object cancels holding"), Result.bHoldCanceled);
	TestEqual(TEXT("Canceled holding clears accumulated time"), Result.HoldElapsedSeconds, 0.0);

	Sample.LightPosition = Definition->LightPosition.Target;
	Result = Evaluator->Evaluate(Sample, Definition, 0.5);
	TestEqual(TEXT("Re-entry starts a fresh hold"), Result.HoldElapsedSeconds, 0.5);
	Result = Evaluator->Evaluate(Sample, Definition, 0.5);
	TestTrue(TEXT("The shared evaluator resolves the coordinated setup"), Result.bJustResolved);
	TestEqual(TEXT("The combined puzzle resolves exactly once"), Result.ResolveCount, 1);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYM2PuppetHysteresisTest,
	"DengYingShanHai.M2.Evaluator.PuppetHysteresis",
	DYM2Tests::TestFlags)

bool FDYM2PuppetHysteresisTest::RunTest(const FString& Parameters)
{
	UDYPuzzleDefinition* Definition = NewObject<UDYPuzzleDefinition>();
	Definition->PuppetPosition.bEnabled = true;
	Definition->PuppetPosition.Target = 0.60;
	Definition->PuppetPosition.EnterTolerance = 0.04;
	Definition->PuppetPosition.ExitTolerance = 0.08;
	Definition->RequiredHoldSeconds = 5.0;

	UDYPuzzleEvaluatorComponent* Evaluator = NewObject<UDYPuzzleEvaluatorComponent>();
	FDYPuzzleSample Sample;
	Sample.bIsValid = true;

	Sample.PuppetPosition = 0.65;
	FDYEvaluationResult Result = Evaluator->Evaluate(Sample, Definition, 0.1);
	TestFalse(TEXT("Puppet remains outside before entering its tight tolerance"), Result.PuppetPosition.bIsValid);

	Sample.PuppetPosition = 0.63;
	Result = Evaluator->Evaluate(Sample, Definition, 0.1);
	TestTrue(TEXT("Puppet enters inside its enter tolerance"), Result.PuppetPosition.bIsValid);

	Sample.PuppetPosition = 0.67;
	Result = Evaluator->Evaluate(Sample, Definition, 0.1);
	TestTrue(TEXT("Puppet validity survives inside its wider exit tolerance"), Result.PuppetPosition.bIsValid);

	Sample.PuppetPosition = 0.69;
	Result = Evaluator->Evaluate(Sample, Definition, 0.1);
	TestFalse(TEXT("Puppet validity exits beyond its hysteresis band"), Result.PuppetPosition.bIsValid);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYM2PuppetClassDefaultsTest,
	"DengYingShanHai.M2.Puppet.ClassDefaults",
	DYM2Tests::TestFlags)

bool FDYM2PuppetClassDefaultsTest::RunTest(const FString& Parameters)
{
	const ADYPuppetActor* Puppet = GetDefault<ADYPuppetActor>();
	TestNotNull(TEXT("Puppet CDO exists"), Puppet);
	TestNotNull(TEXT("Puppet owns the shared control capability"), Puppet ? Puppet->GetPuppetControlComponent() : nullptr);
	if (const UDYPuppetControlComponent* Control = Puppet ? Puppet->GetPuppetControlComponent() : nullptr)
	{
		TestFalse(TEXT("Puppet control is opt-in so P01 remains fixed"), Control->IsControlEnabled());
		TestEqual(TEXT("The first M2 pose stop is deterministic"), Control->GetPoseId(), FName(TEXT("P02_StrideBack")));
		TestFalse(TEXT("Puppet capability does not tick"), Control->PrimaryComponentTick.bCanEverTick);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYM2PresentationClassDefaultsTest,
	"DengYingShanHai.M2.Presentation.ClassDefaults",
	DYM2Tests::TestFlags)

bool FDYM2PresentationClassDefaultsTest::RunTest(const FString& Parameters)
{
	const ADYStagePresentation* Presentation = GetDefault<ADYStagePresentation>();
	const ADYStageEnvironment* Environment = GetDefault<ADYStageEnvironment>();
	TestNotNull(TEXT("Stage Presentation CDO exists"), Presentation);
	TestNotNull(TEXT("Stage Environment CDO exists"), Environment);
	if (Presentation)
	{
		TestFalse(TEXT("Stage Presentation is event-driven and does not tick"), Presentation->PrimaryActorTick.bCanEverTick);
		TestEqual(
			TEXT("Presentation defaults to the P01-compatible resolved environment state"),
			Presentation->GetResolvedEnvironmentState(),
			EDYStageEnvironmentState::SunAwakened);
	}
	if (Environment)
	{
		TestNotNull(TEXT("ChaseAwakened has a dedicated Dev wing accent"), Environment->GetChaseAwakenedAccent());
	}
	return true;
}

#endif
