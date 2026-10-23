#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetCastTypes.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Puppets/DYPuppetPerformanceComponent.h"
#include "TimerManager.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"

namespace DYPuppetPerformanceTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;

	struct FFixture
	{
		FFixture()
		{
			if (!GEngine) { return; }
			World = UWorld::CreateWorld(EWorldType::Game, false,
				MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYPuppetPerformanceTestWorld")));
			StrongWorld.Reset(World);
			if (!World) { return; }
			GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
			Puppet = World->SpawnActor<ADYPuppetActor>();
			if (!Puppet) { return; }
			Performance = Puppet->GetPerformanceComponent();
			Cast = LoadObject<UDYPuppetCastData>(nullptr, TEXT("/Game/DengYingShanHai/Puppets/DA_DYPuppetCast.DA_DYPuppetCast"));
			Data = LoadObject<UDYPuppetPerformanceData>(nullptr, TEXT("/Game/DengYingShanHai/Puppets/DA_DYPuppetPerformance.DA_DYPuppetPerformance"));
			FSoftObjectProperty* AssignedData = FindFProperty<FSoftObjectProperty>(Performance->GetClass(), TEXT("PerformanceData"));
			if (!AssignedData || !Data || !Cast) { return; }
			AssignedData->SetObjectPropertyValue_InContainer(Performance, Data);
			Puppet->DispatchBeginPlay();
			Puppet->ApplyChapterFigure(1, true);
			Mesh = Puppet->GetActivePuppetMesh();
		}
		~FFixture()
		{
			if (World && GEngine)
			{
				World->EndPlay(EEndPlayReason::Quit);
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
			StrongWorld.Reset();
		}
		bool Ready() const
		{
			return World && Puppet && Performance && Mesh && Cast && Data
				&& Data->FindAct(1) && !Data->FindAct(1)->Feedback.IsEmpty();
		}
		UAnimationAsset* Playing() const
		{
			const UAnimSingleNodeInstance* Instance = Mesh ? Mesh->GetSingleNodeInstance() : nullptr;
			return Instance ? Instance->GetAnimationAsset() : nullptr;
		}
		UAnimSequence* CurrentPose() const
		{
			if (!Cast || !Cast->Figures.IsValidIndex(1)) { return nullptr; }
			const TSoftObjectPtr<UAnimSequence>* Clip = Cast->Figures[1].PoseAnimations.Find(Puppet->GetPoseId());
			return Clip ? Clip->LoadSynchronous() : nullptr;
		}
		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> StrongWorld;
		ADYPuppetActor* Puppet = nullptr;
		UDYPuppetPerformanceComponent* Performance = nullptr;
		USkeletalMeshComponent* Mesh = nullptr;
		UDYPuppetCastData* Cast = nullptr;
		UDYPuppetPerformanceData* Data = nullptr;
	};

	class FFeedbackCommand : public IAutomationLatentCommand
	{
	public:
		FFeedbackCommand(FAutomationTestBase* InTest, bool bInCancel)
			: Test(InTest), bCancel(bInCancel), Fixture(MakeShared<FFixture>()) {}
		virtual bool Update() override
		{
			if (!Fixture->Ready()) { Test->AddError(TEXT("Authored puppet/performance fixture is missing")); return true; }
			if (!bStarted)
			{
				bStarted = true;
				Fixture->Performance->TriggerFeedback(1);
				UAnimationAsset* Reaction = Fixture->Playing();
				Test->TestTrue(TEXT("Feedback takes animation ownership"), Fixture->Performance->OwnsAnimation());
				Test->TestTrue(TEXT("Feedback really plays a Perf clip"), Reaction && Reaction->GetName().Contains(TEXT("Perf_")));
				Fixture->Puppet->GetPuppetControlComponent()->SetNormalizedValue(0.86);
				Test->TestEqual(TEXT("Rail changes do not replace the reaction"), Fixture->Playing(), Reaction);
				Fixture->World->GetTimerManager().Tick(0.01f);
				if (bCancel)
				{
					Fixture->Performance->CancelPlayback();
					Test->TestFalse(TEXT("Cancel releases reaction ownership"), Fixture->Performance->OwnsAnimation());
					Test->TestEqual(TEXT("Cancel restores latest rail pose"), Fixture->Playing(), static_cast<UAnimationAsset*>(Fixture->CurrentPose()));
					// A later owner must not be replaced by the old reaction's expiry callback.
					Sentinel = LoadObject<UAnimSequence>(nullptr, TEXT("/Game/DengYingShanHai/Puppets/Animations/A_DY_Jingwei_Perf_Dive.A_DY_Jingwei_Perf_Dive"));
					Test->TestNotNull(TEXT("Sentinel clip exists"), Sentinel);
					if (!Sentinel) { return true; }
					Fixture->Mesh->PlayAnimation(Sentinel, true);
				}
				LastFrame = GFrameCounter;
				return false;
			}
			if (GFrameCounter == LastFrame) { return false; }
			Fixture->World->GetTimerManager().Tick(2.f);
			if (bCancel)
			{
				Test->TestEqual(TEXT("Canceled reaction leaves no stale restore timer"), Fixture->Playing(), static_cast<UAnimationAsset*>(Sentinel));
			}
			else
			{
				Test->TestFalse(TEXT("Real reaction timer releases ownership"), Fixture->Performance->OwnsAnimation());
				Test->TestEqual(TEXT("Real reaction timer restores the latest pose"), Fixture->Playing(), static_cast<UAnimationAsset*>(Fixture->CurrentPose()));
			}
			return true;
		}
	private:
		FAutomationTestBase* Test;
		bool bCancel = false;
		bool bStarted = false;
		uint64 LastFrame = 0;
		TSharedPtr<FFixture> Fixture;
		UAnimSequence* Sentinel = nullptr;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYPuppetReactionOwnsPlayback, "DengYingShanHai.Puppets.Performance.ReactionOwnsPlayback", DYPuppetPerformanceTests::Flags)
bool FDYPuppetReactionOwnsPlayback::RunTest(const FString&)
{
	FAutomationTestFramework::Get().EnqueueLatentCommand(MakeShared<DYPuppetPerformanceTests::FFeedbackCommand>(this, false));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYPuppetReactionCancelClearsTimer, "DengYingShanHai.Puppets.Performance.CancelReactionClearsTimer", DYPuppetPerformanceTests::Flags)
bool FDYPuppetReactionCancelClearsTimer::RunTest(const FString&)
{
	FAutomationTestFramework::Get().EnqueueLatentCommand(MakeShared<DYPuppetPerformanceTests::FFeedbackCommand>(this, true));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYPuppetShowOwnership, "DengYingShanHai.Puppets.Performance.ShowOwnershipCancelAndSkip", DYPuppetPerformanceTests::Flags)
bool FDYPuppetShowOwnership::RunTest(const FString&)
{
	DYPuppetPerformanceTests::FFixture Fixture;
	if (!TestTrue(TEXT("Authored fixture exists"), Fixture.Ready())) { return false; }
	int32 FinishedCount = 0;
	bool bLastSkipped = false;
	Fixture.Performance->OnPerformanceFinished.AddLambda([&](int32 Chapter, bool bSkipped)
	{
		TestEqual(TEXT("Completion refers to active chapter"), Chapter, 1);
		++FinishedCount;
		bLastSkipped = bSkipped;
	});
	Fixture.Performance->TriggerFeedback(1);
	TestTrue(TEXT("Full show supersedes feedback"), Fixture.Performance->StartChapterPerformance(1));
	UAnimationAsset* FirstBeat = Fixture.Playing();
	Fixture.Puppet->GetPuppetControlComponent()->SetNormalizedValue(0.86);
	TestEqual(TEXT("Direct rail update cannot replace a full show"), Fixture.Playing(), FirstBeat);
	TestFalse(TEXT("A running show cannot reenter"), Fixture.Performance->StartChapterPerformance(1));
	Fixture.Performance->CancelPlayback();
	TestEqual(TEXT("Cancel does not publish a solved/finished event"), FinishedCount, 0);
	TestFalse(TEXT("Cancel releases full show ownership"), Fixture.Performance->OwnsAnimation());
	TestEqual(TEXT("Cancel restores latest pose"), Fixture.Playing(), static_cast<UAnimationAsset*>(Fixture.CurrentPose()));
	TestTrue(TEXT("New show can start after cancel"), Fixture.Performance->StartChapterPerformance(1));
	Fixture.Performance->SkipPerformance();
	TestEqual(TEXT("User skip publishes completion exactly once"), FinishedCount, 1);
	TestTrue(TEXT("User skip retains skipped semantic"), bLastSkipped);
	Fixture.Performance->SkipPerformance();
	Fixture.Performance->CancelPlayback();
	TestEqual(TEXT("Repeated skip/cancel cannot republish completion"), FinishedCount, 1);
	Fixture.Performance->OnPerformanceFinished.Clear();
	return true;
}

#endif
