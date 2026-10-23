#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Components/StaticMeshComponent.h"
#include "Core/DYReleaseEntryPlayerController.h"
#include "Core/DYStageGameMode.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformProperties.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Stage/DYForestPresentationActor.h"
#include "Stage/DYStagePresentation.h"
#include "UnrealClient.h"

namespace DYFormalMainTests
{
	static const TCHAR* MainMap = TEXT("/Game/DengYingShanHai/Maps/L_DY_Main");
	static const TCHAR* BranchAsset = TEXT("/Game/DengYingShanHai/Dev/ForestArt/Meshes/SM_DY_ForestBranch_Tapered.SM_DY_ForestBranch_Tapered");
	static const TCHAR* CanopyAsset = TEXT("/Game/DengYingShanHai/Dev/ForestCanopyM04/Meshes/SM_DY_M04_Canopy_A_v04.SM_DY_M04_Canopy_A_v04");

	UWorld* FindMainGameWorld()
	{
		if (!GEngine) { return nullptr; }
		for (const FWorldContext& Context : GEngine->GetWorldContexts())
		{
			UWorld* World = Context.World();
			if (Context.WorldType == EWorldType::Game && World && World->WorldType == EWorldType::Game
				&& World->GetOutermost()->GetName() == MainMap) { return World; }
		}
		return nullptr;
	}

	enum class EStep : uint8
	{
		Title, Start, P01, P02Lamp, P02Puppet, P02Holding, P02Capture,
		P02Reset, P02Redo, P03, CompleteCapture, Replay, FinalCapture
	};

	struct FCheck
	{
		FAutomationTestBase* Test = nullptr;
		TWeakObjectPtr<UWorld> World, PreviousWorld;
		TWeakObjectPtr<ADYReleaseEntryPlayerController> Controller;
		TWeakObjectPtr<ADYStagePresentation> Stage;
		TWeakObjectPtr<ADYPuzzleDirector> Director;
		TWeakObjectPtr<ADYForestPresentationActor> Forest;
		TWeakObjectPtr<UDYLightControlComponent> Light;
		TWeakObjectPtr<UDYPuppetControlComponent> Puppet;
		FGuid OldToken;
		EStep Step = EStep::Title;
		int32 Cycle = 1;
		double Deadline = 0, CycleDeadline = 0, StepTime = 0;
		bool bFailed = false, bP01Holding = false, bP01Resolved = false;
		bool bP02RedoHolding = false, bP02Resolved = false, bP03Holding = false, bP03Resolved = false;
		bool bContact = false, bGrowth = false;
		FString CaptureDirectory, PendingCapture;
		uint64 CaptureFrame = 0;

		bool Require(bool Value, const TCHAR* Message)
		{
			if (!Value)
			{
				Test->AddError(FString::Printf(TEXT("DY_FORMAL_PACKAGED cycle=%d step=%d: %s"), Cycle, static_cast<int32>(Step), Message));
				bFailed = true;
			}
			return Value;
		}
		void Log(const TCHAR* Event) const
		{
			UE_LOG(LogTemp, Display, TEXT("DY_FORMAL_PACKAGED cycle=%d %s"), Cycle, Event);
		}
		void MoveTo(EStep Next) { Step = Next; StepTime = FPlatformTime::Seconds(); }
		bool Capture(const FString& Name)
		{
			if (CaptureDirectory.IsEmpty()) { return true; }
			PendingCapture = FPaths::Combine(CaptureDirectory, Name);
			if (!Require(!IFileManager::Get().FileExists(*PendingCapture), TEXT("Capture would overwrite existing evidence"))
				|| !Require(!FScreenshotRequest::IsScreenshotRequested(), TEXT("Another screenshot request is pending"))) { return false; }
			FScreenshotRequest::RequestScreenshot(PendingCapture, true, false);
			CaptureFrame = GFrameCounter;
			return true;
		}
		bool CaptureReady()
		{
			if (PendingCapture.IsEmpty()) { return true; }
			if (GFrameCounter - CaptureFrame < 3 || FScreenshotRequest::IsScreenshotRequested()
				|| IFileManager::Get().FileSize(*PendingCapture) <= 0) { return false; }
			Test->AddInfo(FString::Printf(TEXT("DY_FORMAL_PACKAGED screenshot=%s"), *PendingCapture));
			PendingCapture.Reset();
			return true;
		}
		bool Attach()
		{
			UWorld* Current = FindMainGameWorld();
			if (!Current || !Current->HasBegunPlay() || Current == PreviousWorld.Get()) { return false; }
			ADYStageGameMode* Mode = Current->GetAuthGameMode<ADYStageGameMode>();
			ADYReleaseEntryPlayerController* PC = Cast<ADYReleaseEntryPlayerController>(Current->GetFirstPlayerController());
			// The legacy GetStagePresentation is deliberately Dev-tree-only; the entry
			// controller uses this same public registration in the formal map.
			ADYStagePresentation* Presentation = Mode ? Mode->GetPlayerStagePresentation() : nullptr;
			ADYPuzzleDirector* Puzzle = IsValid(Presentation) ? Presentation->GetPuzzleDirector() : nullptr;
			ADYForestPresentationActor* Resource = IsValid(Presentation) ? Presentation->GetForestPresentationActor() : nullptr;
			ADYLightRigActor* Lamp = IsValid(Puzzle) ? Puzzle->GetLightRigActor() : nullptr;
			ADYPuppetActor* PuppetActor = IsValid(Puzzle) ? Puzzle->GetPuppetActor() : nullptr;
			if (!IsValid(PC) || !IsValid(Puzzle) || !IsValid(Resource) || !IsValid(Lamp) || !IsValid(PuppetActor)
				|| !IsValid(Lamp->GetLightControlComponent()) || !IsValid(PuppetActor->GetPuppetControlComponent())) { return false; }
			if (!Require(PC->GetWorld() == Current && Presentation->GetWorld() == Current && Puzzle->GetWorld() == Current
				&& Resource->GetWorld() == Current && Lamp->GetWorld() == Current && PuppetActor->GetWorld() == Current,
				TEXT("Registered formal-map dependencies must belong to the current Game world"))) { return false; }
			World = Current; Controller = PC; Stage = Presentation; Director = Puzzle; Forest = Resource;
			Light = Lamp->GetLightControlComponent(); Puppet = PuppetActor->GetPuppetControlComponent();
			return true;
		}
		bool CleanTitle()
		{
			const auto Sequence = Director->GetActSequenceSnapshot();
			return Require(Controller->GetEntryPanel() == EDYDevEntryPanel::Start && Sequence.bSequenceEnabled
				&& Sequence.ActIndex == INDEX_NONE && Sequence.ActCount == 3 && Sequence.Phase == EDYActSequencePhase::Inactive,
				TEXT("Title must expose Start with an inactive three-act sequence"))
				&& Require(!Director->IsAutoStartOnBeginPlay() && Director->GetEvaluationFrequencyHz() == 15.0,
					TEXT("Formal entry must retain manual start and 15 Hz evaluation"))
				&& Require(!Forest->HasForestSession() && Forest->GetBranchMeshComponents().IsEmpty()
					&& Forest->GetCanopyMeshComponents().IsEmpty() && !Stage->GetStaffContactPresentationSnapshot().bHasContact,
					TEXT("Title retained contact or forest resources"))
				&& Require(!Director->GetResolvedPuzzleSnapshot().bIsResolved, TEXT("Title retained a resolved puzzle"));
		}
		bool Baseline() { return Require(FMath::IsNearlyEqual(Light->GetNormalizedValue(), .15, UE_DOUBLE_SMALL_NUMBER)
			&& FMath::IsNearlyEqual(Puppet->GetNormalizedValue(), .15, UE_DOUBLE_SMALL_NUMBER), TEXT("Act/reset must restore both controls to 0.15")); }
		/** Within a chapter the next act now opens on the previous act's settled Target. */
		bool Carried(double Lamp, double Figure)
		{
			return Require(FMath::IsNearlyEqual(Light->GetNormalizedValue(), Lamp, UE_DOUBLE_SMALL_NUMBER)
				&& FMath::IsNearlyEqual(Puppet->GetNormalizedValue(), Figure, UE_DOUBLE_SMALL_NUMBER),
				TEXT("Act transition must carry the previous act's settled values"));
		}
		void Values(double Lamp, double Figure)
		{
			Light->SetNormalizedValue(Lamp); Puppet->SetNormalizedValue(Figure);
		}
		bool Playing(int32 Index)
		{
			const auto Sequence = Director->GetActSequenceSnapshot();
			return Require(Sequence.ActIndex == Index && Sequence.Phase == EDYActSequencePhase::Playing,
				TEXT("Expected current act to remain Playing"));
		}
		bool Targets(double Lamp, double Figure, bool bPuppetRequired)
		{
			const auto Result = Director->GetLastEvaluation();
			return Require(Result.LightPosition.bEnabled && Result.LightPosition.Target == Lamp
				&& Result.PuppetPosition.bEnabled == bPuppetRequired
				&& (!bPuppetRequired || Result.PuppetPosition.Target == Figure)
				&& Result.HoldRequiredSeconds == 1.25, TEXT("Authored targets or real 1.25-second hold changed"));
		}
		void ObserveFinale()
		{
			const auto Contact = Stage->GetStaffContactPresentationSnapshot();
			if (Contact.bHasContact && !bContact)
			{
				Require(Contact.Token.IsValid() && Director->IsResolvedTokenCurrent(Contact.Token), TEXT("Actual contact has no current resolved identity"));
				bContact = true; Log(TEXT("ActualStaffContact"));
			}
			if (Forest->HasForestSession())
			{
				if (!Require(Contact.bHasContact, TEXT("Forest appeared before actual Staff contact"))) { return; }
				const auto Sample = Forest->GetForestGeometrySample();
				if (!Require(Sample.Status == EDYForestGeometryStatus::Valid && Sample.ContactToken == Contact.Token,
					TEXT("Forest growth does not belong to the actual contact"))) { return; }
				for (const auto& Branch : Sample.Branches)
				{
					if (!bGrowth && Branch.bVisible && Branch.Portion > 0 && Branch.Portion < 1)
					{
						bGrowth = true; Log(TEXT("ActualIntermediateForestGrowth"));
					}
				}
			}
		}
		bool Mesh(const UStaticMeshComponent* Component, const TCHAR* Asset)
		{
			return Require(IsValid(Component) && Component->GetOwner() == Forest.Get() && Component->GetWorld() == World.Get()
				&& Component->IsRegistered() && Component->IsVisible() && !Component->bHiddenInGame && Component->CastShadow
				&& Component->Mobility == EComponentMobility::Movable && Component->GetCollisionEnabled() == ECollisionEnabled::NoCollision
				&& !Component->GetGenerateOverlapEvents() && IsValid(Component->GetStaticMesh())
				&& Component->GetStaticMesh()->GetPathName() == Asset,
				TEXT("Final forest mesh must be registered, visible, shadow-casting, collision-free and use the expected asset"));
		}
		bool FinalForest()
		{
			if (!Require(bP03Holding && bP03Resolved && bContact && bGrowth, TEXT("Finale skipped observed real Holding, Resolve, contact or intermediate growth"))
				|| !Require(Controller->GetEntryPanel() == EDYDevEntryPanel::End && Forest->HasForestSession(), TEXT("Complete must expose the End menu with a live forest"))) { return false; }
			const auto Branches = Forest->GetBranchMeshComponents();
			const auto Canopies = Forest->GetCanopyMeshComponents();
			const auto Sample = Forest->GetForestGeometrySample();
			if (!Require(Branches.Num() == 15 && Canopies.Num() == 5 && Sample.Branches.Num() == 15
				&& Sample.Status == EDYForestGeometryStatus::Valid, TEXT("Final forest must contain 15 branches and five M04 canopies"))) { return false; }
			for (int32 Index = 0; Index < Branches.Num(); ++Index)
			{
				if (!Mesh(Branches[Index], BranchAsset)
					|| !Require(Sample.Branches[Index].bVisible && FMath::IsNearlyEqual(Sample.Branches[Index].Portion, 1.0, UE_DOUBLE_SMALL_NUMBER)
						&& Branches[Index]->GetComponentTransform().Equals(Sample.Branches[Index].MeshWorldTransform, UE_DOUBLE_SMALL_NUMBER),
						TEXT("Completed branch does not match the fully expanded native geometry"))) { return false; }
			}
			for (const UStaticMeshComponent* Canopy : Canopies) { if (!Mesh(Canopy, CanopyAsset)) { return false; } }
			OldToken = Director->GetResolvedPuzzleSnapshot().Token;
			return Require(OldToken.IsValid() && Director->IsResolvedTokenCurrent(OldToken), TEXT("Final resolved identity missing"));
		}
		void ResetP02()
		{
			if (!Playing(1)) { return; }
			Director->ResetCurrentPuzzle();
			Log(TEXT("P02ResetRequestedDuringRealHolding")); MoveTo(EStep::P02Reset);
		}
		bool Update()
		{
			if (bFailed) { return true; }
			const double Now = FPlatformTime::Seconds();
			if (!Require(Now < Deadline, TEXT("Three-cycle 180-second deadline exceeded"))
				|| !Require(Now < CycleDeadline, TEXT("Current cycle/replay 60-second deadline exceeded"))) { return true; }
			if (Step == EStep::Title || Step == EStep::Replay)
			{
				if (!Attach() || bFailed) { return bFailed; }
				if (Controller->GetEntryPanel() != EDYDevEntryPanel::Start) { return false; }
				if (!CleanTitle()) { return true; }
				if (Step == EStep::Replay)
				{
					if (!Require(!Director->IsResolvedTokenCurrent(OldToken) && !Stage->TryAcceptStaffContact(OldToken), TEXT("Same-map replay accepted the old resolved identity"))) { return true; }
					Log(TEXT("SameMapReplayCleanTitleOldTokenRejected"));
					if (Cycle == 3)
					{
						Capture(TEXT("99_ReplayTitle.png")); MoveTo(EStep::FinalCapture); return bFailed;
					}
					++Cycle; CycleDeadline = Now + 60;
				}
				else { Capture(TEXT("00_Title.png")); }
				Log(TEXT("TitleReady")); MoveTo(EStep::Start); return bFailed;
			}
			if (!Require(World.IsValid() && Controller.IsValid() && Stage.IsValid() && Director.IsValid()
				&& Forest.IsValid() && Light.IsValid() && Puppet.IsValid(), TEXT("Current-world fixture disappeared outside replay travel"))) { return true; }
			const auto Sequence = Director->GetActSequenceSnapshot();
			const auto Result = Director->GetLastEvaluation();
			const auto Alignment = Stage->GetPlayerAlignmentDisplay();
			switch (Step)
			{
			case EStep::Start:
				if (!CaptureReady()) { break; }
				if (!Require(Controller->RequestStartExperience(), TEXT("Real controller start intent rejected"))
					|| !Require(!Controller->RequestStartExperience(), TEXT("Duplicate start intent accepted"))
					|| !Playing(0) || !Baseline() || !Targets(.68, .5, false)
					|| !Require(!Puppet->IsControlEnabled(), TEXT("P01 must disable puppet control"))) { break; }
				bP01Holding = bP01Resolved = bP02RedoHolding = bP02Resolved = bP03Holding = bP03Resolved = bContact = bGrowth = false;
				Light->SetNormalizedValue(.68); Log(TEXT("StartAcceptedP01PuppetDisabledLamp068")); MoveTo(EStep::P01); break;
			case EStep::P01:
				if (Sequence.ActIndex == 0)
				{
					if (!bP01Holding && Result.State == EDYPuzzleRuntimeState::Holding && Result.HoldElapsedSeconds > .12)
					{ bP01Holding = true; Log(TEXT("P01RealHolding")); }
					if (!bP01Resolved && Result.ResolveCount == 1) { bP01Resolved = true; Log(TEXT("P01NaturalResolve")); }
					break;
				}
				if (!Require(bP01Holding && bP01Resolved, TEXT("P01 advanced without observed natural Holding and Resolve"))
					|| !Playing(1) || !Carried(.68, .15) || !Targets(.72, .8, true)
					|| !Require(Puppet->IsControlEnabled(), TEXT("P02 must enable puppet control"))) { break; }
				Values(.72, .15); Log(TEXT("P02EntryLampOnly")); MoveTo(EStep::P02Lamp); break;
			case EStep::P02Lamp:
			case EStep::P02Puppet:
				if (!Playing(1)) { break; }
				if (Now - StepTime < 1.5) { break; }
				if (!Require(Result.ResolveCount == 0 && Result.State != EDYPuzzleRuntimeState::Holding && !Alignment.bHolding,
					TEXT("A single P02 target must not hold or resolve"))) { break; }
				if (Step == EStep::P02Lamp)
				{
					if (!Require(Alignment.bLightReady && !Alignment.bPuppetReady, TEXT("P02 lamp-only readiness mismatch"))) { break; }
					Log(TEXT("P02LampAloneRejected")); Values(.15, .8); MoveTo(EStep::P02Puppet);
				}
				else
				{
					if (!Require(Alignment.bPuppetReady && !Alignment.bLightReady, TEXT("P02 puppet-only readiness mismatch"))) { break; }
					Log(TEXT("P02PuppetAloneRejected")); Values(.72, .8); MoveTo(EStep::P02Holding);
				}
				break;
			case EStep::P02Holding:
				if (!Playing(1)) { break; }
				if (Alignment.bHolding && Result.State == EDYPuzzleRuntimeState::Holding && Result.HoldElapsedSeconds > .12)
				{
					Log(TEXT("P02JointTargetRealHolding"));
					if (!Capture(FString::Printf(TEXT("Cycle%02d_P02.png"), Cycle))) { break; }
					MoveTo(EStep::P02Capture);
				}
				break;
			case EStep::P02Capture:
				if (CaptureReady()) { ResetP02(); }
				break;
			case EStep::P02Reset:
				if (Now - StepTime < .5) { break; }
				if (!Playing(1) || !Baseline() || !Require(Result.ResolveCount == 0 && Result.HoldElapsedSeconds == 0
					&& !Alignment.bHolding && Result.State != EDYPuzzleRuntimeState::Holding, TEXT("P02 reset retained hold or resolve"))) { break; }
				Log(TEXT("P02ResetBaseline015_015SameAct")); Values(.72, .8); MoveTo(EStep::P02Redo); break;
			case EStep::P02Redo:
				if (Sequence.ActIndex == 1)
				{
					if (!bP02RedoHolding && Result.State == EDYPuzzleRuntimeState::Holding && Result.HoldElapsedSeconds > .12)
					{ bP02RedoHolding = true; Log(TEXT("P02RedoRealHolding")); }
					if (!bP02Resolved && Result.ResolveCount == 1) { bP02Resolved = true; Log(TEXT("P02RedoNaturalResolve")); }
					break;
				}
				if (!Require(bP02RedoHolding && bP02Resolved, TEXT("P02 advanced without reset redo Holding and Resolve"))
					|| !Playing(2) || !Carried(.72, .8) || !Targets(.72, .92, true)) { break; }
				Values(.72, .92); Log(TEXT("P03EntryLamp072Puppet092")); MoveTo(EStep::P03); break;
			case EStep::P03:
				if (!Require(Sequence.ActIndex == 2, TEXT("P03 final act index changed"))) { break; }
				if (!bP03Holding && Result.State == EDYPuzzleRuntimeState::Holding && Result.HoldElapsedSeconds > .12)
				{ bP03Holding = true; Log(TEXT("P03RealHolding")); }
				if (!bP03Resolved && Result.ResolveCount == 1) { bP03Resolved = true; Log(TEXT("P03NaturalResolve")); }
				ObserveFinale();
				if (Sequence.Phase == EDYActSequencePhase::Complete && !bFailed && FinalForest())
				{
					Log(TEXT("ForestCompleteEndMenu15Branches5M04Canopies"));
					Capture(FString::Printf(TEXT("Cycle%02d_ForestComplete.png"), Cycle)); MoveTo(EStep::CompleteCapture);
				}
				break;
			case EStep::CompleteCapture:
				if (!CaptureReady()) { break; }
				PreviousWorld = World;
				if (!Require(Controller->RequestReplayExperience(), TEXT("Real controller replay intent rejected"))) { break; }
				Log(TEXT("ReplayRequested"));
				World.Reset(); Controller.Reset(); Stage.Reset(); Director.Reset(); Forest.Reset(); Light.Reset(); Puppet.Reset();
				MoveTo(EStep::Replay); break;
			case EStep::FinalCapture:
				if (!CaptureReady()) { break; }
				if (!CleanTitle()) { break; }
				Log(TEXT("PASS ThreeCompleteFlowsAndThreeSameMapReplays; programmatic interfaces only")); return true;
			default: break;
			}
			return bFailed;
		}
	};
}

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FDYFormalMainCommand, TSharedPtr<DYFormalMainTests::FCheck>, Check);
bool FDYFormalMainCommand::Update() { return Check->Update(); }

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFormalMainPackagedFlowTest,
	"DengYingShanHai.FormalMain.PackagedThreeActsAndReplay",
	EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter)
bool FDYFormalMainPackagedFlowTest::RunTest(const FString& Parameters)
{
	if (!TestTrue(TEXT("Requires the cooked Game executable"), FPlatformProperties::RequiresCookedData())
		|| !TestFalse(TEXT("Editor processes cannot satisfy packaged acceptance"), GIsEditor)
		|| !TestFalse(TEXT("Requires a rendering Game process"), FParse::Param(FCommandLine::Get(), TEXT("nullrhi")))
		|| !TestNotNull(TEXT("Must launch exact /Game/DengYingShanHai/Maps/L_DY_Main as EWorldType::Game"), DYFormalMainTests::FindMainGameWorld())) { return false; }
	auto Check = MakeShared<DYFormalMainTests::FCheck>();
	Check->Test = this;
	const double Now = FPlatformTime::Seconds();
	Check->Deadline = Now + 180; Check->CycleDeadline = Now + 60;
	FParse::Value(FCommandLine::Get(), TEXT("DYFormalCaptureDir="), Check->CaptureDirectory);
	if (!Check->CaptureDirectory.IsEmpty()
		&& (!TestFalse(TEXT("DYFormalCaptureDir must be absolute"), FPaths::IsRelative(Check->CaptureDirectory))
			|| !TestTrue(TEXT("Capture directory is available"), IFileManager::Get().MakeDirectory(*Check->CaptureDirectory, true)))) { return false; }
	AddInfo(TEXT("DY_FORMAL_PACKAGED Three natural-time cooked Game flows through existing control/menu APIs; no physical input, blind playtest, performance or Shipping claim."));
	ADD_LATENT_AUTOMATION_COMMAND(FDYFormalMainCommand(Check));
	return true;
}

#endif
