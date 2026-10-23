#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Puzzles/DYPuzzleDefinition.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"

/** Set references only; tests must pass through the actual Director/Evaluator. */
struct FDYResolvedSnapshotTestSeam
{
	static void Configure(ADYPuzzleDirector& Director, ADYLightRigActor* Light,
		ADYPuppetActor* Puppet, UDYPuzzleDefinition* Definition)
	{
		Director.LightRig = Light;
		Director.PuppetActor = Puppet;
		Director.PuzzleDefinition = Definition;
	}
	static void End(ADYPuzzleDirector& Director) { Director.EndPlay(EEndPlayReason::Destroyed); }
};

namespace DYResolvedSnapshotTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;

	struct FFixture
	{
		explicit FFixture(bool bWithPuppet = true)
		{
			if (!GEngine) { return; }
			const FName Name = MakeUniqueObjectName(nullptr, UWorld::StaticClass(),
				TEXT("DYResolvedSnapshotWorld"), EUniqueObjectNameOptions::GloballyUnique);
			World = UWorld::CreateWorld(EWorldType::Game, false, Name, GetTransientPackage());
			StrongWorld.Reset(World);
			if (!World) { return; }
			GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
			Light = World->SpawnActor<ADYLightRigActor>(FVector(-460.0, -20.0, 310.0), FRotator::ZeroRotator);
			if (bWithPuppet)
			{
				Puppet = World->SpawnActor<ADYPuppetActor>(FVector(600.0, -80.0, 210.0), FRotator::ZeroRotator);
			}
			Director = World->SpawnActor<ADYPuzzleDirector>();
			if (!Light || !Director || (bWithPuppet && !Puppet)) { return; }
			Definition = NewObject<UDYPuzzleDefinition>(Director);
			Definition->PuzzleId = bWithPuppet ? TEXT("SnapshotCombinedTest") : TEXT("SnapshotLightOnlyTest");
			Definition->LightPosition.bEnabled = true;
			Definition->LightPosition.Target = 0.72;
			Definition->LightPosition.EnterTolerance = 0.05;
			Definition->LightPosition.ExitTolerance = 0.09;
			if (bWithPuppet)
			{
				Definition->PuppetPosition.bEnabled = true;
				Definition->PuppetPosition.Target = 0.80;
				Definition->PuppetPosition.EnterTolerance = 0.05;
				Definition->PuppetPosition.ExitTolerance = 0.09;
				Definition->RequiredPuppetPoseId = TEXT("P02_StrideReach");
			}
			// Test-only zero hold: no clock manipulation, no new live P03 tuning.
			Definition->RequiredHoldSeconds = 0.0;
			FDYResolvedSnapshotTestSeam::Configure(*Director, Light, Puppet, Definition);
			Director->StartCurrentPuzzle();
		}

		~FFixture()
		{
			if (World && GEngine) { GEngine->DestroyWorldContext(World); World->DestroyWorld(false); }
			StrongWorld.Reset();
		}

		bool IsReady() const { return World && Light && Director && Definition; }
		void Resolve()
		{
			// Deliberately not the target centre: prove no forced answer transform.
			Light->GetLightControlComponent()->SetNormalizedValue(0.755);
			if (Puppet) { Puppet->GetPuppetControlComponent()->SetNormalizedValue(0.825); }
			Director->EvaluatePuzzleNow();
		}

		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> StrongWorld;
		ADYLightRigActor* Light = nullptr;
		ADYPuppetActor* Puppet = nullptr;
		ADYPuzzleDirector* Director = nullptr;
		UDYPuzzleDefinition* Definition = nullptr;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYResolvedActualStateTest,
	"DengYingShanHai.P03.Foundation.ActualStateAndCopy", DYResolvedSnapshotTests::Flags)

bool FDYResolvedActualStateTest::RunTest(const FString& Parameters)
{
	DYResolvedSnapshotTests::FFixture F;
	if (!TestTrue(TEXT("Actual Director fixture exists"), F.IsReady() && F.Puppet)) { return false; }
	TestFalse(TEXT("No snapshot before Resolve"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	F.Resolve();
	FDYResolvedPuzzleSnapshot Snapshot = F.Director->GetResolvedPuzzleSnapshot();
	TestTrue(TEXT("Actual evaluator produced a resolved snapshot"), Snapshot.bIsResolved);
	TestTrue(TEXT("Director accepts its own resolved token"), F.Director->IsResolvedTokenCurrent(Snapshot.Token));
	TestEqual(TEXT("Snapshot identifies actual puzzle"), Snapshot.PuzzleId, F.Definition->PuzzleId);
	TestEqual(TEXT("Keeps actual light, not target centre"), Snapshot.Light.PrimaryNormalized, 0.755);
	TestEqual(TEXT("Keeps actual puppet, not target centre"), Snapshot.Puppet.PrimaryNormalized, 0.825);
	TestEqual(TEXT("Keeps actual pose"), Snapshot.Puppet.PoseId, F.Puppet->GetPoseId());
	TestTrue(TEXT("Light transform is current visible actor transform"), Snapshot.Light.WorldTransform.Equals(F.Light->GetActorTransform()));
	TestTrue(TEXT("Puppet transform is current visible actor transform"), Snapshot.Puppet.WorldTransform.Equals(F.Puppet->GetActorTransform()));
	TestFalse(TEXT("Existing light Resolve lock retained"), F.Light->GetLightControlComponent()->IsControlEnabled());
	TestFalse(TEXT("Existing puppet Resolve lock retained"), F.Puppet->GetPuppetControlComponent()->IsControlEnabled());

	FDYControlIntent Intent;
	Intent.Value.X = 1.0;
	Intent.DeltaSeconds = 1.0;
	F.Light->GetLightControlComponent()->BeginControl();
	F.Puppet->GetPuppetControlComponent()->BeginControl();
	F.Light->GetLightControlComponent()->ApplyControlIntent(Intent);
	F.Puppet->GetPuppetControlComponent()->ApplyControlIntent(Intent);
	TestEqual(TEXT("Input cannot change frozen light"), F.Light->GetLightControlComponent()->GetNormalizedValue(), 0.755);
	TestEqual(TEXT("Input cannot change frozen puppet"), F.Puppet->GetPuppetControlComponent()->GetNormalizedValue(), 0.825);

	Snapshot.Light.PrimaryNormalized = -100.0;
	Snapshot.Puppet.PoseId = TEXT("MutatedCopy");
	const FDYResolvedPuzzleSnapshot Reread = F.Director->GetResolvedPuzzleSnapshot();
	TestEqual(TEXT("Read-only getter returns independent light copy"), Reread.Light.PrimaryNormalized, 0.755);
	TestEqual(TEXT("Read-only getter returns independent pose copy"), Reread.Puppet.PoseId, F.Puppet->GetPoseId());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYResolvedDuplicateTest,
	"DengYingShanHai.P03.Foundation.NoRecapture", DYResolvedSnapshotTests::Flags)

bool FDYResolvedDuplicateTest::RunTest(const FString& Parameters)
{
	DYResolvedSnapshotTests::FFixture F;
	if (!TestTrue(TEXT("Fixture ready"), F.IsReady() && F.Puppet)) { return false; }
	F.Resolve();
	const FDYResolvedPuzzleSnapshot Before = F.Director->GetResolvedPuzzleSnapshot();
	TestTrue(TEXT("Fixture really resolved"), Before.bIsResolved);
	F.Light->AddActorWorldOffset(FVector(0.0, 73.0, 0.0));
	F.Puppet->AddActorWorldOffset(FVector(0.0, -45.0, 0.0));
	F.Director->EvaluatePuzzleNow();
	const FDYResolvedPuzzleSnapshot After = F.Director->GetResolvedPuzzleSnapshot();
	TestTrue(TEXT("Same identity after repeated evaluation"), After.Token == Before.Token);
	TestTrue(TEXT("Light evidence not recaptured from changed visuals"), After.Light.WorldTransform.Equals(Before.Light.WorldTransform));
	TestTrue(TEXT("Puppet evidence not recaptured from changed visuals"), After.Puppet.WorldTransform.Equals(Before.Puppet.WorldTransform));
	TestEqual(TEXT("Resolve count remains one"), F.Director->GetLastEvaluation().ResolveCount, 1);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYResolvedTokenLifetimeTest,
	"DengYingShanHai.P03.Foundation.TokenLifetime", DYResolvedSnapshotTests::Flags)

bool FDYResolvedTokenLifetimeTest::RunTest(const FString& Parameters)
{
	DYResolvedSnapshotTests::FFixture F;
	DYResolvedSnapshotTests::FFixture Other;
	if (!TestTrue(TEXT("Both actual Director fixtures ready"), F.IsReady() && Other.IsReady())) { return false; }
	F.Resolve();
	Other.Resolve();
	const FGuid OldToken = F.Director->GetResolvedPuzzleSnapshot().Token;
	const FGuid OtherToken = Other.Director->GetResolvedPuzzleSnapshot().Token;
	TestTrue(TEXT("Resolved identities valid"), OldToken.IsValid() && OtherToken.IsValid());
	TestFalse(TEXT("Another Director's token is rejected"), F.Director->IsResolvedTokenCurrent(OtherToken));
	TestFalse(TEXT("Empty token is rejected"), F.Director->IsResolvedTokenCurrent(FGuid()));
	F.Director->ResetCurrentPuzzle();
	TestFalse(TEXT("Reset immediately rejects old token"), F.Director->IsResolvedTokenCurrent(OldToken));
	TestFalse(TEXT("Reset clears old evidence"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	F.Resolve();
	const FGuid NewToken = F.Director->GetResolvedPuzzleSnapshot().Token;
	TestTrue(TEXT("A new success gets a new identity"), NewToken.IsValid() && NewToken != OldToken);
	F.Director->StartCurrentPuzzle();
	TestFalse(TEXT("Direct restart rejects previous activation even with same values"), F.Director->IsResolvedTokenCurrent(NewToken));
	const FGuid RestartedToken = F.Director->GetResolvedPuzzleSnapshot().Token;
	TestTrue(TEXT("Zero-hold restart genuinely resolved under new identity"), RestartedToken.IsValid() && RestartedToken != NewToken);
	FDYResolvedSnapshotTestSeam::End(*F.Director);
	TestFalse(TEXT("EndPlay invalidates callback identity"), F.Director->IsResolvedTokenCurrent(RestartedToken));
	TestFalse(TEXT("EndPlay returns empty snapshot"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYResolvedP01CompatibilityTest,
	"DengYingShanHai.P03.Foundation.P01OptionalPuppet", DYResolvedSnapshotTests::Flags)

bool FDYResolvedP01CompatibilityTest::RunTest(const FString& Parameters)
{
	DYResolvedSnapshotTests::FFixture F(false);
	if (!TestTrue(TEXT("Light-only fixture ready"), F.IsReady())) { return false; }
	F.Resolve();
	const FDYResolvedPuzzleSnapshot Snapshot = F.Director->GetResolvedPuzzleSnapshot();
	TestTrue(TEXT("P01-style definition still resolves without puppet"), Snapshot.bIsResolved);
	TestTrue(TEXT("Light-only resolved token is valid"), F.Director->IsResolvedTokenCurrent(Snapshot.Token));
	TestTrue(TEXT("Light evidence captured"), Snapshot.Light.bIsValid);
	TestFalse(TEXT("Missing optional puppet does not invent evidence"), Snapshot.Puppet.bIsValid);
	TestFalse(TEXT("CDO has no runtime success state"), GetDefault<ADYPuzzleDirector>()->GetResolvedPuzzleSnapshot().bIsResolved);
	return true;
}

#endif
