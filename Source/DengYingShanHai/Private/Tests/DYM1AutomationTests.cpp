#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Components/SpotLightComponent.h"
#include "Interaction/DYInteractionComponent.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Player/DYStageOperatorPawn.h"
#include "Puzzles/DYPuzzleDefinition.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Puzzles/DYPuzzleEvaluatorComponent.h"
#include "Stage/DYStageEnvironment.h"

namespace DYM1Tests
{
	constexpr EAutomationTestFlags TestFlags =
		EAutomationTestFlags::EditorContext |
		EAutomationTestFlags::EngineFilter;

	UDYPuzzleDefinition* MakeDefinition()
	{
		UDYPuzzleDefinition* Definition = NewObject<UDYPuzzleDefinition>();
		Definition->PuzzleId = TEXT("P01_Dev");
		Definition->LightPosition.bEnabled = true;
		Definition->LightPosition.Target = 0.70;
		Definition->LightPosition.EnterTolerance = 0.05;
		Definition->LightPosition.ExitTolerance = 0.10;
		Definition->RequiredHoldSeconds = 1.0;
		return Definition;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYM1EvaluatorHysteresisTest,
	"DengYingShanHai.M1.Evaluator.Hysteresis",
	DYM1Tests::TestFlags)

bool FDYM1EvaluatorHysteresisTest::RunTest(const FString& Parameters)
{
	UDYPuzzleDefinition* Definition = DYM1Tests::MakeDefinition();
	UDYPuzzleEvaluatorComponent* Evaluator = NewObject<UDYPuzzleEvaluatorComponent>();
	FDYPuzzleSample Sample;
	Sample.bIsValid = true;

	Sample.LightPosition = 0.76;
	FDYEvaluationResult Result = Evaluator->Evaluate(Sample, Definition, 0.1);
	TestFalse(TEXT("Outside enter tolerance does not enter the target"), Result.LightPosition.bIsValid);

	Sample.LightPosition = 0.74;
	Result = Evaluator->Evaluate(Sample, Definition, 0.1);
	TestTrue(TEXT("Inside enter tolerance enters the target"), Result.LightPosition.bIsValid);

	Sample.LightPosition = 0.78;
	Result = Evaluator->Evaluate(Sample, Definition, 0.1);
	TestTrue(TEXT("Exit tolerance preserves validity near the boundary"), Result.LightPosition.bIsValid);

	Sample.LightPosition = 0.81;
	Result = Evaluator->Evaluate(Sample, Definition, 0.1);
	TestFalse(TEXT("Outside exit tolerance cancels validity"), Result.LightPosition.bIsValid);
	TestEqual(TEXT("Leaving the target clears hold time"), Result.HoldElapsedSeconds, 0.0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYM1EvaluatorFrequencyTest,
	"DengYingShanHai.M1.Evaluator.FrequencyIndependence",
	DYM1Tests::TestFlags)

bool FDYM1EvaluatorFrequencyTest::RunTest(const FString& Parameters)
{
	UDYPuzzleDefinition* Definition = DYM1Tests::MakeDefinition();

	for (const int32 FrequencyHz : {10, 15, 20})
	{
		UDYPuzzleEvaluatorComponent* Evaluator = NewObject<UDYPuzzleEvaluatorComponent>();
		FDYPuzzleSample Sample;
		Sample.bIsValid = true;
		Sample.LightPosition = Definition->LightPosition.Target;

		const double StepSeconds = 1.0 / static_cast<double>(FrequencyHz);
		FDYEvaluationResult Result;
		double SimulatedSeconds = 0.0;
		while (!Result.bJustResolved && SimulatedSeconds < 2.0)
		{
			Result = Evaluator->Evaluate(Sample, Definition, StepSeconds);
			SimulatedSeconds += StepSeconds;
		}

		TestTrue(
			FString::Printf(TEXT("%d Hz reaches Resolved"), FrequencyHz),
			Result.State == EDYPuzzleRuntimeState::Resolved);
		TestTrue(
			FString::Printf(TEXT("%d Hz does not resolve before the required hold"), FrequencyHz),
			SimulatedSeconds + UE_DOUBLE_SMALL_NUMBER >= Definition->RequiredHoldSeconds);
		TestTrue(
			FString::Printf(TEXT("%d Hz resolves within one sample after the hold"), FrequencyHz),
			SimulatedSeconds <= Definition->RequiredHoldSeconds + StepSeconds + UE_DOUBLE_SMALL_NUMBER);

		const FDYEvaluationResult RepeatedResult = Evaluator->Evaluate(Sample, Definition, StepSeconds);
		TestFalse(
			FString::Printf(TEXT("%d Hz resolve edge fires only once"), FrequencyHz),
			RepeatedResult.bJustResolved);
		TestEqual(
			FString::Printf(TEXT("%d Hz resolve count remains one"), FrequencyHz),
			RepeatedResult.ResolveCount,
			1);
	}

	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYM1ClassDefaultsTest,
	"DengYingShanHai.M1.ClassDefaults",
	DYM1Tests::TestFlags)

bool FDYM1ClassDefaultsTest::RunTest(const FString& Parameters)
{
	const ADYLightRigActor* LightRig = GetDefault<ADYLightRigActor>();
	const ADYPuzzleDirector* Director = GetDefault<ADYPuzzleDirector>();
	const ADYStageOperatorPawn* Operator = GetDefault<ADYStageOperatorPawn>();
	const ADYStageEnvironment* Environment = GetDefault<ADYStageEnvironment>();

	TestNotNull(TEXT("Light rig CDO exists"), LightRig);
	TestNotNull(TEXT("Puzzle Director CDO exists"), Director);
	if (LightRig)
	{
		TestNotNull(TEXT("Light rig owns a control component"), LightRig->GetLightControlComponent());
		TestNotNull(TEXT("Light rig owns a movable Spot Light"), LightRig->GetKeyLightComponent());
		if (const USpotLightComponent* SpotLight = LightRig->GetKeyLightComponent())
		{
			TestEqual(TEXT("Key Spot Light is Movable"), SpotLight->Mobility, EComponentMobility::Movable);
			TestTrue(TEXT("Key Spot Light casts real UE shadows"), SpotLight->CastShadows);
		}
	}
	if (Director)
	{
		TestNotNull(TEXT("Director owns one evaluator"), Director->GetEvaluatorComponent());
		TestEqual(TEXT("Dev sampling baseline is 15 Hz"), Director->GetEvaluationFrequencyHz(), 15.0);
		TestFalse(TEXT("Development debug is opt-in by default"), Director->IsDevelopmentDebugEnabled());
		TestEqual(TEXT("Debug presentation refreshes at most four times per second"), Director->GetDevelopmentDebugRefreshIntervalSeconds(), 0.25);
	}
	TestNotNull(TEXT("Operator owns reusable interaction capability"), Operator ? Operator->GetInteractionComponent() : nullptr);
	TestNotNull(TEXT("Stage environment CDO exists"), Environment);
	if (Environment)
	{
		TestEqual(TEXT("Stage environment starts Dormant"), Environment->GetCurrentState(), EDYStageEnvironmentState::Dormant);
		TestNotNull(TEXT("Stage environment owns the SunAwakened accent"), Environment->GetSunAwakenedAccent());
		TestNotNull(TEXT("Stage environment owns the ChaseAwakened wing accent"), Environment->GetChaseAwakenedAccent());
		TestFalse(TEXT("Stage environment does not tick"), Environment->PrimaryActorTick.bCanEverTick);
	}

	UDYLightControlComponent* Control = NewObject<UDYLightControlComponent>();
	Control->BeginControl();
	TestTrue(TEXT("Control session begins while enabled"), Control->IsUnderControl());
	Control->SetControlEnabled(false);
	TestFalse(TEXT("Gameplay response can be disabled"), Control->IsControlEnabled());
	TestTrue(TEXT("Disabling response does not silently end the interaction session"), Control->IsUnderControl());
	Control->EndControl();
	TestFalse(TEXT("Interaction owner explicitly ends the control session"), Control->IsUnderControl());
	return true;
}

#endif
