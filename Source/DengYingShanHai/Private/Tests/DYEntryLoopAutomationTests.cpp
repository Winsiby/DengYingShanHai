#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Core/DYDevEntryPlayerController.h"
#include "Components/TextBlock.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Puzzles/DYPuzzleDefinition.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Stage/DYStagePresentation.h"
#include "Stage/DYStageEnvironment.h"
#include "TimerManager.h"
#include "UI/DYDevEntryWidget.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"

/** Authoring setup and observation only. No fabricated phase, token or success. */
struct FDYEntryLoopTestSeam
{
	static FName MenuMap(const FString& Name, EWorldType::Type Type) { return ADYDevEntryPlayerController::ResolveDevEntryMapName(Name, Type); }
	/** Pure value policy only: never injects a phase into any runtime actor. */
	static bool ReleaseControlForActEntry(const FDYActSequenceSnapshot& Snapshot, int32 LastPlayingActIndex)
	{
		return ADYDevEntryPlayerController::ShouldReleaseControlForActEntry(Snapshot, LastPlayingActIndex);
	}
	static void BuildMenuView(UDYDevEntryWidget& View) { View.BuildView(); }
	static void Configure(ADYPuzzleDirector& D, ADYLightRigActor* L, ADYPuppetActor* P,
		const TArray<FDYActSequenceEntry>& Entries, bool bAuto)
	{
		D.LightRig = L; D.PuppetActor = P; D.ActSequence = Entries;
		D.PuzzleDefinition = Entries[0].Definition; D.bAutoStartOnBeginPlay = bAuto;
	}
	static bool Ready(const ADYPuzzleDirector& D, const ADYStagePresentation* S) { return D.CanStartManualSequence(S); }
	static bool Start(ADYPuzzleDirector& D, ADYStagePresentation* S) { return D.StartManualSequence(S); }
	static void EnableCampaign(ADYPuzzleDirector& D)
	{
		D.bFourActCampaign = true;
		D.BaseActSequence = D.ActSequence;
		D.EnsureCampaignChapters();
	}
	static bool StartChapter(ADYPuzzleDirector& D, ADYStagePresentation* S, int32 Index) { return D.StartCampaignChapter(Index, S); }
	static FGuid Token(const ADYPuzzleDirector& D) { return D.ActivationToken; }
	static bool Timer(const ADYPuzzleDirector& D) { return D.GetWorld() && D.GetWorld()->GetTimerManager().TimerExists(D.EvaluationTimerHandle); }
};

namespace DYEntryTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext
		| EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter;
	struct FFixture
	{
		UWorld* World = nullptr;
		TStrongObjectPtr<UWorld> Strong;
		ADYLightRigActor* Light = nullptr;
		ADYPuppetActor* Puppet = nullptr;
		ADYPuzzleDirector* Director = nullptr;
		ADYStagePresentation* Stage = nullptr;
		ADYStageEnvironment* Environment = nullptr;
		TArray<FDYActSequenceEntry> Entries;
		explicit FFixture(bool bAuto = false, bool bDependencies = true)
		{
			if (!GEngine) { return; }
			World = UWorld::CreateWorld(EWorldType::Game, false,
				MakeUniqueObjectName(nullptr, UWorld::StaticClass(), TEXT("DYEntryTestWorld")), GetTransientPackage());
			Strong.Reset(World);
			if (!World) { return; }
			GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
			Light = World->SpawnActor<ADYLightRigActor>();
			Puppet = World->SpawnActor<ADYPuppetActor>();
			Director = World->SpawnActor<ADYPuzzleDirector>();
			Stage = World->SpawnActor<ADYStagePresentation>();
			Environment = World->SpawnActor<ADYStageEnvironment>();
			if (!Light || !Puppet || !Director || !Stage || !Environment) { return; }
			for (int32 I = 0; I < 3; ++I)
			{
				FDYActSequenceEntry Entry;
				Entry.Definition = NewObject<UDYPuzzleDefinition>(Director);
				Entry.Definition->PuzzleId = FName(*FString::Printf(TEXT("EntryFixture%d"), I));
				Entry.Definition->LightPosition.bEnabled = true;
				Entry.Definition->LightPosition.Target = .7;
				Entry.Definition->RequiredHoldSeconds = 1.25;
				Entry.ActTitle = FText::FromString(FString::Printf(TEXT("Entry %d"), I));
				Entries.Add(Entry);
			}
			FDYEntryLoopTestSeam::Configure(*Director, Light, Puppet, Entries, bAuto);
			FObjectPropertyBase* Ref = FindFProperty<FObjectPropertyBase>(Stage->GetClass(), TEXT("PuzzleDirector"));
			check(Ref); Ref->SetObjectPropertyValue_InContainer(Stage, Director);
			Ref = FindFProperty<FObjectPropertyBase>(Stage->GetClass(), TEXT("StageEnvironment"));
			check(Ref); Ref->SetObjectPropertyValue_InContainer(Stage, Environment);
			if (bDependencies) { Light->DispatchBeginPlay(); Puppet->DispatchBeginPlay(); }
			Stage->DispatchBeginPlay(); Director->DispatchBeginPlay();
		}
		~FFixture()
		{
			if (World && GEngine) { World->EndPlay(EEndPlayReason::Quit); GEngine->DestroyWorldContext(World); World->DestroyWorld(false); }
			Strong.Reset();
		}
		bool Valid() const { return World && Director && Light && Puppet && Stage && Environment && Entries.Num() == 3; }
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryInactiveTest, "DengYingShanHai.EntryLoop.GenuinelyInactiveTitle", DYEntryTests::Flags)
bool FDYEntryInactiveTest::RunTest(const FString& Parameters)
{
	DYEntryTests::FFixture F;
	if (!TestTrue(TEXT("World and actor fixture"), F.Valid())) { return false; }
	TestFalse(TEXT("Opt-out is explicit"), F.Director->IsAutoStartOnBeginPlay());
	TestEqual(TEXT("No first act before start"), F.Director->GetActSequenceSnapshot().ActIndex, INDEX_NONE);
	TestEqual(TEXT("Inactive, not just paused"), F.Director->GetActSequenceSnapshot().Phase, EDYActSequencePhase::Inactive);
	TestFalse(TEXT("No evaluator timer"), FDYEntryLoopTestSeam::Timer(*F.Director));
	TestFalse(TEXT("Light control disabled"), F.Light->GetLightControlComponent()->IsControlEnabled());
	TestFalse(TEXT("Puppet control disabled"), F.Puppet->GetPuppetControlComponent()->IsControlEnabled());
	F.Director->StartCurrentPuzzle(); F.Director->ResetCurrentPuzzle();
	F.Light->GetLightControlComponent()->SetNormalizedValue(.7);
	for (int32 I = 0; I < 30; ++I) { F.World->Tick(LEVELTICK_All, .05f); F.Director->EvaluatePuzzleNow(); }
	TestEqual(TEXT("Public legacy start/reset cannot bypass title opt-in"), F.Director->GetActSequenceSnapshot().ActIndex, INDEX_NONE);
	TestFalse(TEXT("Even a matching value cannot resolve before start"), F.Director->GetResolvedPuzzleSnapshot().bIsResolved);
	TestFalse(TEXT("No accidental timer after waiting"), FDYEntryLoopTestSeam::Timer(*F.Director));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryStartTest, "DengYingShanHai.EntryLoop.TrustedStartExactlyOnce", DYEntryTests::Flags)
bool FDYEntryStartTest::RunTest(const FString& Parameters)
{
	DYEntryTests::FFixture F;
	if (!TestTrue(TEXT("Fixture"), F.Valid())) { return false; }
	TestTrue(TEXT("Registered ready presentation"), FDYEntryLoopTestSeam::Ready(*F.Director, F.Stage));
	TestTrue(TEXT("First actual start accepted"), FDYEntryLoopTestSeam::Start(*F.Director, F.Stage));
	const FGuid Token = FDYEntryLoopTestSeam::Token(*F.Director);
	TestTrue(TEXT("Actual activation identity"), Token.IsValid());
	TestEqual(TEXT("First act"), F.Director->GetActSequenceSnapshot().ActIndex, 0);
	TestEqual(TEXT("Actual playing"), F.Director->GetActSequenceSnapshot().Phase, EDYActSequencePhase::Playing);
	TestEqual(TEXT("Existing light baseline"), F.Light->GetLightControlComponent()->GetNormalizedValue(), .15);
	TestEqual(TEXT("Existing puppet baseline"), F.Puppet->GetPuppetControlComponent()->GetNormalizedValue(), .15);
	TestTrue(TEXT("Evaluator starts only now"), FDYEntryLoopTestSeam::Timer(*F.Director));
	TestFalse(TEXT("Duplicate click rejected"), FDYEntryLoopTestSeam::Start(*F.Director, F.Stage));
	TestEqual(TEXT("Duplicate preserves identity"), FDYEntryLoopTestSeam::Token(*F.Director), Token);
	F.Director->ResetCurrentPuzzle();
	TestEqual(TEXT("Accepted current-act reset still works"), F.Director->GetActSequenceSnapshot().ActIndex, 0);
	TestTrue(TEXT("Reset receives new identity"), FDYEntryLoopTestSeam::Token(*F.Director) != Token);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryCallerTest, "DengYingShanHai.EntryLoop.WrongCallerAndReadiness", DYEntryTests::Flags)
bool FDYEntryCallerTest::RunTest(const FString& Parameters)
{
	DYEntryTests::FFixture F, Other, Pending(false, false);
	if (!TestTrue(TEXT("Fixtures"), F.Valid() && Other.Valid() && Pending.Valid())) { return false; }
	TestFalse(TEXT("Null caller"), FDYEntryLoopTestSeam::Start(*F.Director, nullptr));
	TestFalse(TEXT("Other world"), FDYEntryLoopTestSeam::Start(*F.Director, Other.Stage));
	ADYStagePresentation* Rogue = F.World->SpawnActor<ADYStagePresentation>();
	TestFalse(TEXT("Unregistered same-world actor"), FDYEntryLoopTestSeam::Start(*F.Director, Rogue));
	TestFalse(TEXT("Dependencies must finish BeginPlay"), FDYEntryLoopTestSeam::Start(*Pending.Director, Pending.Stage));
	Pending.Light->DispatchBeginPlay(); Pending.Puppet->DispatchBeginPlay();
	TestTrue(TEXT("Explicit ready retry"), FDYEntryLoopTestSeam::Start(*Pending.Director, Pending.Stage));
	TestEqual(TEXT("Rejected caller never changes act"), F.Director->GetActSequenceSnapshot().ActIndex, INDEX_NONE);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryLegacyTest, "DengYingShanHai.EntryLoop.LegacyAutoStartUnchanged", DYEntryTests::Flags)
bool FDYEntryLegacyTest::RunTest(const FString& Parameters)
{
	TestTrue(TEXT("Default auto-start remains true"), GetDefault<ADYPuzzleDirector>()->IsAutoStartOnBeginPlay());
	DYEntryTests::FFixture F(true);
	if (!TestTrue(TEXT("Fixture"), F.Valid())) { return false; }
	TestEqual(TEXT("Old sequence still automatically plays"), F.Director->GetActSequenceSnapshot().Phase, EDYActSequencePhase::Playing);
	TestFalse(TEXT("Menu caller cannot restart old automatic mode"), FDYEntryLoopTestSeam::Start(*F.Director, F.Stage));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryReentryTest, "DengYingShanHai.EntryLoop.ReentrantStartAndTeardown", DYEntryTests::Flags)
bool FDYEntryReentryTest::RunTest(const FString& Parameters)
{
	DYEntryTests::FFixture F;
	if (!TestTrue(TEXT("Fixture"), F.Valid())) { return false; }
	int32 Calls = 0;
	const FDelegateHandle H = F.Director->OnActSequenceChanged().AddLambda([&](const FDYActSequenceSnapshot& S)
	{
		if (S.Phase != EDYActSequencePhase::Playing) { return; }
		++Calls;
		TestFalse(TEXT("Nested start rejected"), FDYEntryLoopTestSeam::Start(*F.Director, F.Stage));
		F.Director->Destroy();
	});
	TestFalse(TEXT("Destroyed activation cannot report start success"), FDYEntryLoopTestSeam::Start(*F.Director, F.Stage));
	TestEqual(TEXT("One real notification"), Calls, 1);
	TestFalse(TEXT("No timer resurrection"), FDYEntryLoopTestSeam::Timer(*F.Director));
	TestFalse(TEXT("Late request after EndPlay"), FDYEntryLoopTestSeam::Start(*F.Director, F.Stage));
	F.Director->OnActSequenceChanged().Remove(H);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryInterfaceTest, "DengYingShanHai.EntryLoop.PublicUIBoundaryAndChineseLabels", DYEntryTests::Flags)
bool FDYEntryInterfaceTest::RunTest(const FString& Parameters)
{
	TestNull(TEXT("No Blueprint raw manual-start bypass"), ADYPuzzleDirector::StaticClass()->FindFunctionByName(TEXT("StartManualSequence")));
	TestNull(TEXT("View has no Director getter"), UDYDevEntryWidget::StaticClass()->FindFunctionByName(TEXT("GetPuzzleDirector")));
	TestNull(TEXT("View has no success command"), UDYDevEntryWidget::StaticClass()->FindFunctionByName(TEXT("AcceptFinaleCompletion")));
	TestNotNull(TEXT("Only player intent exposed"), ADYDevEntryPlayerController::StaticClass()->FindFunctionByName(TEXT("RequestStartExperience")));
	TestEqual(TEXT("Chinese start"), UDYDevEntryWidget::GetPrimaryLabel(EDYDevEntryPanel::Start).ToString(), FString(TEXT("开始游戏")));
	TestEqual(TEXT("Chinese replay"), UDYDevEntryWidget::GetPrimaryLabel(EDYDevEntryPanel::End).ToString(), FString(TEXT("重新复演")));
	TestEqual(TEXT("Authoritative completion wording"), UDYDevEntryWidget::GetTitle(EDYDevEntryPanel::End).ToString(), FString(TEXT("复演已成")));
	TestFalse(TEXT("Start never announces success"), UDYDevEntryWidget::GetBody(EDYDevEntryPanel::Start).ToString().Contains(TEXT("复演已成")));
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryMenuFontTest, "DengYingShanHai.EntryLoop.MenuButtonFontConsistency", DYEntryTests::Flags)
bool FDYEntryMenuFontTest::RunTest(const FString& Parameters)
{
	TStrongObjectPtr<UDYDevEntryWidget> View(NewObject<UDYDevEntryWidget>(GetTransientPackage()));
	if (!TestTrue(TEXT("Initialize real native WidgetTree"), View->Initialize())) { return false; }
	FDYEntryLoopTestSeam::BuildMenuView(*View);
	if (!TestTrue(TEXT("Real view has font and buttons"), View->HasReadyView())) { return false; }
	UTextBlock* Primary = Cast<UTextBlock>(View->GetWidgetFromName(TEXT("PrimaryLabel")));
	UTextBlock* Quit = Cast<UTextBlock>(View->GetWidgetFromName(TEXT("QuitLabel")));
	if (!TestNotNull(TEXT("Actual primary label"), Primary) || !TestNotNull(TEXT("Actual quit label"), Quit)) { return false; }
	for (const EDYDevEntryPanel Panel : { EDYDevEntryPanel::Start, EDYDevEntryPanel::End, EDYDevEntryPanel::Reloading })
	{
		View->ApplyPanel(Panel);
		TestEqual(TEXT("Primary uses menu plaque size"), Primary->GetFont().Size, 34.0f);
		TestEqual(TEXT("Quit uses menu plaque size"), Quit->GetFont().Size, 34.0f);
		TestTrue(TEXT("Same font asset, face, outline and size"), Primary->GetFont() == Quit->GetFont());
	}
	TestEqual(TEXT("Quit wording unchanged"), Quit->GetText().ToString(), FString(TEXT("退出游戏")));
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryMapIdentityTest, "DengYingShanHai.EntryLoop.ExactDevMapIdentityAndReplayTarget", DYEntryTests::Flags)
bool FDYEntryMapIdentityTest::RunTest(const FString& Parameters)
{
	const FString Alignment = TEXT("/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab");
	const FString Environment = TEXT("/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab");
	const FString Entry = TEXT("/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev");
	const FString Readability = TEXT("/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab");
	const FString KuafuGuide = TEXT("/Game/DengYingShanHai/Dev/P02KuafuGuide/Maps/LV_P02KuafuGuideLab");
#if UE_BUILD_SHIPPING
	TestTrue(TEXT("Shipping Kuafu guide menu rejected"), FDYEntryLoopTestSeam::MenuMap(KuafuGuide, EWorldType::Game).IsNone());
	TestTrue(TEXT("Shipping environment menu rejected"), FDYEntryLoopTestSeam::MenuMap(Environment, EWorldType::Game).IsNone());
	TestTrue(TEXT("Shipping alignment menu rejected"), FDYEntryLoopTestSeam::MenuMap(Alignment, EWorldType::Game).IsNone());
	TestTrue(TEXT("Shipping original menu rejected"), FDYEntryLoopTestSeam::MenuMap(Entry, EWorldType::Game).IsNone());
	TestTrue(TEXT("Shipping readability menu rejected"), FDYEntryLoopTestSeam::MenuMap(Readability, EWorldType::Game).IsNone());
#else
	TestEqual(TEXT("Kuafu guide replay returns to exactly its own map"), FDYEntryLoopTestSeam::MenuMap(KuafuGuide, EWorldType::Game), FName(*KuafuGuide));
	TestEqual(TEXT("Kuafu guide PIE prefix removed for replay"), FDYEntryLoopTestSeam::MenuMap(TEXT("/Game/DengYingShanHai/Dev/P02KuafuGuide/Maps/UEDPIE_4_LV_P02KuafuGuideLab"), EWorldType::PIE), FName(*KuafuGuide));
	TestTrue(TEXT("Kuafu guide editor world rejected"), FDYEntryLoopTestSeam::MenuMap(KuafuGuide, EWorldType::Editor).IsNone());
	TestEqual(TEXT("Environment replays to exactly its own map"), FDYEntryLoopTestSeam::MenuMap(Environment, EWorldType::Game), FName(*Environment));
	TestEqual(TEXT("Environment PIE canonical identity"), FDYEntryLoopTestSeam::MenuMap(TEXT("/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/UEDPIE_3_LV_EnvironmentStatesLab"), EWorldType::PIE), FName(*Environment));
	TestTrue(TEXT("Environment suffix rejected"), FDYEntryLoopTestSeam::MenuMap(Environment + TEXT("_Other"), EWorldType::Game).IsNone());
	TestTrue(TEXT("Environment editor world rejected"), FDYEntryLoopTestSeam::MenuMap(Environment, EWorldType::Editor).IsNone());
	TestTrue(TEXT("Environment similar path rejected"), FDYEntryLoopTestSeam::MenuMap(TEXT("/Game/Other/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab"), EWorldType::Game).IsNone());
	TestEqual(TEXT("Alignment replay returns to its own map"), FDYEntryLoopTestSeam::MenuMap(Alignment, EWorldType::Game), FName(*Alignment));
	TestEqual(TEXT("Alignment PIE canonical identity"), FDYEntryLoopTestSeam::MenuMap(TEXT("/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/UEDPIE_2_LV_AlignmentFeedbackLab"), EWorldType::PIE), FName(*Alignment));
	TestTrue(TEXT("Alignment suffix rejected"), FDYEntryLoopTestSeam::MenuMap(Alignment + TEXT("_Other"), EWorldType::Game).IsNone());
	TestEqual(TEXT("Original identity preserved"), FDYEntryLoopTestSeam::MenuMap(Entry, EWorldType::Game), FName(*Entry));
	TestEqual(TEXT("New identity replays to itself, not EntryLoop"), FDYEntryLoopTestSeam::MenuMap(Readability, EWorldType::Game), FName(*Readability));
	TestEqual(TEXT("PIE original canonical travel target"), FDYEntryLoopTestSeam::MenuMap(TEXT("/Game/DengYingShanHai/Dev/EntryLoop/Maps/UEDPIE_0_LV_EntryLoopDev"), EWorldType::PIE), FName(*Entry));
	TestEqual(TEXT("PIE readability canonical travel target"), FDYEntryLoopTestSeam::MenuMap(TEXT("/Game/DengYingShanHai/Dev/Readability/Maps/UEDPIE_7_LV_ReadabilityLab"), EWorldType::PIE), FName(*Readability));
#endif
	for (const FString& Rejected : {
		FString(), FString(TEXT("LV_ReadabilityLab")), FString(TEXT("/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab")),
		Entry + TEXT("_Other"), Readability + TEXT(".umap"), Readability + TEXT("?game=Other"),
		KuafuGuide + TEXT("_Other"), KuafuGuide + TEXT("?game=Other"), KuafuGuide + TEXT(".umap"),
		FString(TEXT("/Game/Other/Dev/Readability/Maps/LV_ReadabilityLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/Readability/Other/LV_ReadabilityLab")) })
	{
		TestTrue(TEXT("No Contains/short-name/path suffix widening"), FDYEntryLoopTestSeam::MenuMap(Rejected, EWorldType::Game).IsNone());
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryFramePostMapIdentityTest,
	"DengYingShanHai.EntryLoop.FramePostExactMapIdentityAndContexts", DYEntryTests::Flags)
bool FDYEntryFramePostMapIdentityTest::RunTest(const FString& Parameters)
{
	const FString FramePost = TEXT("/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab");
	const FString FramePostPIE = TEXT("/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/UEDPIE_4_LV_FramePostPlacementLab");
#if UE_BUILD_SHIPPING
	TestTrue(TEXT("Shipping frame-post Game menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FramePost, EWorldType::Game).IsNone());
	TestTrue(TEXT("Shipping frame-post PIE menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FramePostPIE, EWorldType::PIE).IsNone());
#else
	TestEqual(TEXT("Frame-post Game replays to exactly its own map"), FDYEntryLoopTestSeam::MenuMap(FramePost, EWorldType::Game), FName(*FramePost));
	TestEqual(TEXT("Frame-post canonical PIE identity"), FDYEntryLoopTestSeam::MenuMap(FramePost, EWorldType::PIE), FName(*FramePost));
	TestEqual(TEXT("Frame-post PIE prefix removed from same-map replay target"), FDYEntryLoopTestSeam::MenuMap(FramePostPIE, EWorldType::PIE), FName(*FramePost));
#endif
	for (const FString& Rejected : {
		FString(), FString(TEXT("LV_FramePostPlacementLab")),
		FramePost + TEXT("_Other"), FramePost + TEXT(".umap"), FramePost + TEXT("?game=Other"),
		FString(TEXT("/Game/Other/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FramePostPlacement/Other/LV_FramePostPlacementLab")),
		FramePostPIE + TEXT("_Other"), FramePostPIE + TEXT(".umap"), FramePostPIE + TEXT("?game=Other") })
	{
		TestTrue(FString::Printf(TEXT("Frame-post Game rejects nonexact package: %s"), *Rejected),
			FDYEntryLoopTestSeam::MenuMap(Rejected, EWorldType::Game).IsNone());
		TestTrue(FString::Printf(TEXT("Frame-post PIE rejects nonexact package: %s"), *Rejected),
			FDYEntryLoopTestSeam::MenuMap(Rejected, EWorldType::PIE).IsNone());
	}
	for (const EWorldType::Type Type : { EWorldType::None, EWorldType::Editor, EWorldType::EditorPreview, EWorldType::GamePreview, EWorldType::Inactive })
	{
		TestTrue(FString::Printf(TEXT("Frame-post canonical package rejects nonplay world type %d"), static_cast<int32>(Type)),
			FDYEntryLoopTestSeam::MenuMap(FramePost, Type).IsNone());
		TestTrue(FString::Printf(TEXT("Frame-post PIE package rejects nonplay world type %d"), static_cast<int32>(Type)),
			FDYEntryLoopTestSeam::MenuMap(FramePostPIE, Type).IsNone());
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryMapContextTest, "DengYingShanHai.EntryLoop.DevMapContextAndPrivateBoundary", DYEntryTests::Flags)
bool FDYEntryMapContextTest::RunTest(const FString& Parameters)
{
	const FString Readability = TEXT("/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab");
	for (const EWorldType::Type Type : { EWorldType::None, EWorldType::Editor, EWorldType::EditorPreview, EWorldType::GamePreview, EWorldType::Inactive })
	{
		TestTrue(TEXT("Authored editor/preview/inactive worlds cannot open menu or travel"), FDYEntryLoopTestSeam::MenuMap(Readability, Type).IsNone());
	}
	TestNull(TEXT("No Blueprint arbitrary destination resolver"), ADYDevEntryPlayerController::StaticClass()->FindFunctionByName(TEXT("ResolveDevEntryMapName")));
	TestNull(TEXT("No Blueprint raw travel entry"), ADYDevEntryPlayerController::StaticClass()->FindFunctionByName(TEXT("PerformReplay")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryActReleaseForwardPolicyTest,
	"DengYingShanHai.EntryLoop.ActEntryReleaseForwardPolicy", DYEntryTests::Flags)
bool FDYEntryActReleaseForwardPolicyTest::RunTest(const FString& Parameters)
{
	// Pure constructed snapshots are inputs to a side-effect-free predicate only.
	// This test does not create a LocalPlayer, press E, or prove a runtime release.
	struct FCase { int32 PreviousIndex; int32 NewIndex; bool Expected; };
	const FCase Cases[] = {
		{0, 1, true},
		{1, 2, true},
		{0, 2, true}, // Policy recognizes forward entry; Director still owns the actual legal order.
		{0, 0, false},
		{1, 1, false},
		{2, 2, false},
		{INDEX_NONE, 0, false}, // First start is not a transition from an already playing act.
		{2, 1, false},
		{1, 0, false},
		{2, 0, false}
	};
	for (const FCase& Case : Cases)
	{
		FDYActSequenceSnapshot Snapshot;
		Snapshot.bSequenceEnabled = true;
		Snapshot.Phase = EDYActSequencePhase::Playing;
		Snapshot.ActCount = 3;
		Snapshot.ActIndex = Case.NewIndex;
		TestEqual(FString::Printf(TEXT("Pure release decision previous %d -> Playing %d"), Case.PreviousIndex, Case.NewIndex),
			FDYEntryLoopTestSeam::ReleaseControlForActEntry(Snapshot, Case.PreviousIndex), Case.Expected);
		// Repeating the same settled entry cannot trigger a second release.
		TestFalse(TEXT("Settled duplicate Playing snapshot never re-releases control"),
			FDYEntryLoopTestSeam::ReleaseControlForActEntry(Snapshot, Case.NewIndex));
	}
	FDYActSequenceSnapshot OtherValidCount;
	OtherValidCount.bSequenceEnabled = true;
	OtherValidCount.Phase = EDYActSequencePhase::Playing;
	OtherValidCount.ActCount = 5;
	OtherValidCount.ActIndex = 4;
	TestTrue(TEXT("Pure policy validates indices against supplied positive count, not an unrelated hardcoded map count"),
		FDYEntryLoopTestSeam::ReleaseControlForActEntry(OtherValidCount, 3));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryActReleaseInvalidPolicyTest,
	"DengYingShanHai.EntryLoop.ActEntryReleaseInvalidSnapshotPolicy", DYEntryTests::Flags)
bool FDYEntryActReleaseInvalidPolicyTest::RunTest(const FString& Parameters)
{
	// Negative pure-policy coverage is not a synthetic runtime notification test.
	FDYActSequenceSnapshot ValidForward;
	ValidForward.bSequenceEnabled = true;
	ValidForward.Phase = EDYActSequencePhase::Playing;
	ValidForward.ActCount = 3;
	ValidForward.ActIndex = 1;
	FDYActSequenceSnapshot Disabled = ValidForward;
	Disabled.bSequenceEnabled = false;
	TestFalse(TEXT("Disabled sequence cannot request a release"), FDYEntryLoopTestSeam::ReleaseControlForActEntry(Disabled, 0));
	for (const EDYActSequencePhase Phase : {EDYActSequencePhase::Inactive, EDYActSequencePhase::AwaitingTransition,
		EDYActSequencePhase::AwaitingFinale, EDYActSequencePhase::Complete, static_cast<EDYActSequencePhase>(255)})
	{
		FDYActSequenceSnapshot Snapshot = ValidForward;
		Snapshot.Phase = Phase;
		TestFalse(TEXT("Non-Playing phase cannot request a release"),
			FDYEntryLoopTestSeam::ReleaseControlForActEntry(Snapshot, 0));
	}
	for (const int32 Count : {-2, -1, 0})
	{
		FDYActSequenceSnapshot Snapshot = ValidForward;
		Snapshot.ActCount = Count;
		TestFalse(TEXT("Non-positive act count fails safely"), FDYEntryLoopTestSeam::ReleaseControlForActEntry(Snapshot, 0));
	}
	const int32 InvalidIndices[] = {-2, INDEX_NONE, 3, 99};
	for (const int32 InvalidIndex : InvalidIndices)
	{
		FDYActSequenceSnapshot Snapshot = ValidForward;
		Snapshot.ActIndex = InvalidIndex;
		TestFalse(TEXT("Invalid incoming index cannot request a release"),
			FDYEntryLoopTestSeam::ReleaseControlForActEntry(Snapshot, 0));
		TestFalse(TEXT("Invalid previous Playing index cannot request a release"),
			FDYEntryLoopTestSeam::ReleaseControlForActEntry(ValidForward, InvalidIndex));
	}
	FDYActSequenceSnapshot TooSmallCount = ValidForward;
	TooSmallCount.ActCount = 1;
	TestFalse(TEXT("Incoming index equal to count is outside the valid interval"),
		FDYEntryLoopTestSeam::ReleaseControlForActEntry(TooSmallCount, 0));
	TooSmallCount.ActIndex = 0;
	TestFalse(TEXT("Previous index equal to count is outside the valid interval"),
		FDYEntryLoopTestSeam::ReleaseControlForActEntry(TooSmallCount, 1));
	TestFalse(TEXT("One-act same entry is not a forward transition"),
		FDYEntryLoopTestSeam::ReleaseControlForActEntry(TooSmallCount, 0));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryFrameBeamMapIdentityTest,
	"DengYingShanHai.EntryLoop.FrameBeamExactMapIdentityAndContexts", DYEntryTests::Flags)
bool FDYEntryFrameBeamMapIdentityTest::RunTest(const FString& Parameters)
{
	const FString FrameBeam = TEXT("/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab");
	const FString FrameBeamPIE = TEXT("/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/UEDPIE_6_LV_FrameBeamPlacementLab");
#if UE_BUILD_SHIPPING
	TestTrue(TEXT("Shipping frame-beam Game menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FrameBeam, EWorldType::Game).IsNone());
	TestTrue(TEXT("Shipping frame-beam canonical PIE menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FrameBeam, EWorldType::PIE).IsNone());
	TestTrue(TEXT("Shipping frame-beam prefixed PIE menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FrameBeamPIE, EWorldType::PIE).IsNone());
#else
	TestEqual(TEXT("Frame-beam Game replays to exactly its own map"), FDYEntryLoopTestSeam::MenuMap(FrameBeam, EWorldType::Game), FName(*FrameBeam));
	TestEqual(TEXT("Frame-beam canonical PIE identity"), FDYEntryLoopTestSeam::MenuMap(FrameBeam, EWorldType::PIE), FName(*FrameBeam));
	TestEqual(TEXT("Frame-beam PIE prefix removed from same-map replay target"), FDYEntryLoopTestSeam::MenuMap(FrameBeamPIE, EWorldType::PIE), FName(*FrameBeam));
#endif
	for (const FString& Rejected : {
		FString(), FString(TEXT("LV_FrameBeamPlacementLab")),
		FrameBeam + TEXT("_Other"), FrameBeam + TEXT(".umap"), FrameBeam + TEXT("?game=Other"),
		FString(TEXT("/Game/Other/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FrameBeamPlacement/Other/LV_FrameBeamPlacementLab")),
		FrameBeamPIE + TEXT("_Other"), FrameBeamPIE + TEXT(".umap"), FrameBeamPIE + TEXT("?game=Other") })
	{
		TestTrue(FString::Printf(TEXT("Frame-beam Game rejects nonexact package: %s"), *Rejected),
			FDYEntryLoopTestSeam::MenuMap(Rejected, EWorldType::Game).IsNone());
		TestTrue(FString::Printf(TEXT("Frame-beam PIE rejects nonexact package: %s"), *Rejected),
			FDYEntryLoopTestSeam::MenuMap(Rejected, EWorldType::PIE).IsNone());
	}
	for (const EWorldType::Type Type : { EWorldType::None, EWorldType::Editor, EWorldType::EditorPreview,
		EWorldType::GamePreview, EWorldType::GameRPC, EWorldType::Inactive, static_cast<EWorldType::Type>(255) })
	{
		TestTrue(FString::Printf(TEXT("Frame-beam canonical package rejects nonplay world type %d"), static_cast<int32>(Type)),
			FDYEntryLoopTestSeam::MenuMap(FrameBeam, Type).IsNone());
		TestTrue(FString::Printf(TEXT("Frame-beam PIE package rejects nonplay world type %d"), static_cast<int32>(Type)),
			FDYEntryLoopTestSeam::MenuMap(FrameBeamPIE, Type).IsNone());
	}
	for (const FString& ExistingMap : {
		FString(TEXT("/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev")),
		FString(TEXT("/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab")) })
	{
#if UE_BUILD_SHIPPING
		TestTrue(TEXT("Shipping still rejects every prior Game map"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::Game).IsNone());
		TestTrue(TEXT("Shipping still rejects every prior PIE map"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::PIE).IsNone());
#else
		TestEqual(TEXT("Each prior Game map keeps its exact replay identity"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::Game), FName(*ExistingMap));
		TestEqual(TEXT("Each prior PIE map keeps its canonical replay identity"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::PIE), FName(*ExistingMap));
#endif
	}
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryFrameBeamCandidateMapIdentityTest,
	"DengYingShanHai.EntryLoop.FrameBeamCandidateExactMapIdentityAndContexts", DYEntryTests::Flags)
bool FDYEntryFrameBeamCandidateMapIdentityTest::RunTest(const FString& Parameters)
{
	const FString FrameBeamCandidate = TEXT("/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab");
	const FString FrameBeamCandidatePIE = TEXT("/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/UEDPIE_8_LV_FrameBeamCandidateLab");
#if UE_BUILD_SHIPPING
	TestTrue(TEXT("Shipping frame-beam candidate Game menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FrameBeamCandidate, EWorldType::Game).IsNone());
	TestTrue(TEXT("Shipping frame-beam candidate canonical PIE menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FrameBeamCandidate, EWorldType::PIE).IsNone());
	TestTrue(TEXT("Shipping frame-beam candidate prefixed PIE menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FrameBeamCandidatePIE, EWorldType::PIE).IsNone());
#else
	TestEqual(TEXT("Frame-beam candidate Game replays to exactly its own map"), FDYEntryLoopTestSeam::MenuMap(FrameBeamCandidate, EWorldType::Game), FName(*FrameBeamCandidate));
	TestEqual(TEXT("Frame-beam candidate canonical PIE identity"), FDYEntryLoopTestSeam::MenuMap(FrameBeamCandidate, EWorldType::PIE), FName(*FrameBeamCandidate));
	TestEqual(TEXT("Frame-beam candidate PIE prefix removed from same-map replay target"), FDYEntryLoopTestSeam::MenuMap(FrameBeamCandidatePIE, EWorldType::PIE), FName(*FrameBeamCandidate));
#endif
	for (const FString& Rejected : {
		FString(), FString(TEXT("LV_FrameBeamCandidateLab")),
		FrameBeamCandidate + TEXT("_Other"), FrameBeamCandidate + TEXT(".umap"), FrameBeamCandidate + TEXT("?game=Other"),
		FString(TEXT("/Game/Other/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FrameBeamCandidate/Other/LV_FrameBeamCandidateLab")),
		FrameBeamCandidatePIE + TEXT("_Other"), FrameBeamCandidatePIE + TEXT(".umap"), FrameBeamCandidatePIE + TEXT("?game=Other") })
	{
		TestTrue(FString::Printf(TEXT("Frame-beam candidate Game rejects nonexact package: %s"), *Rejected),
			FDYEntryLoopTestSeam::MenuMap(Rejected, EWorldType::Game).IsNone());
		TestTrue(FString::Printf(TEXT("Frame-beam candidate PIE rejects nonexact package: %s"), *Rejected),
			FDYEntryLoopTestSeam::MenuMap(Rejected, EWorldType::PIE).IsNone());
	}
	for (const EWorldType::Type Type : { EWorldType::None, EWorldType::Editor, EWorldType::EditorPreview,
		EWorldType::GamePreview, EWorldType::GameRPC, EWorldType::Inactive, static_cast<EWorldType::Type>(255) })
	{
		TestTrue(FString::Printf(TEXT("Frame-beam candidate canonical package rejects nonplay world type %d"), static_cast<int32>(Type)),
			FDYEntryLoopTestSeam::MenuMap(FrameBeamCandidate, Type).IsNone());
		TestTrue(FString::Printf(TEXT("Frame-beam candidate PIE package rejects nonplay world type %d"), static_cast<int32>(Type)),
			FDYEntryLoopTestSeam::MenuMap(FrameBeamCandidatePIE, Type).IsNone());
	}
	for (const FString& ExistingMap : {
		FString(TEXT("/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev")),
		FString(TEXT("/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab")) })
	{
#if UE_BUILD_SHIPPING
		TestTrue(TEXT("Shipping still rejects every prior Game map"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::Game).IsNone());
		TestTrue(TEXT("Shipping still rejects every prior PIE map"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::PIE).IsNone());
#else
		TestEqual(TEXT("Each prior Game map keeps its exact replay identity"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::Game), FName(*ExistingMap));
		TestEqual(TEXT("Each prior PIE map keeps its canonical replay identity"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::PIE), FName(*ExistingMap));
#endif
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryFrameBeamTopUVMapIdentityTest,
	"DengYingShanHai.EntryLoop.FrameBeamTopUVExactMapIdentityAndContexts", DYEntryTests::Flags)
bool FDYEntryFrameBeamTopUVMapIdentityTest::RunTest(const FString& Parameters)
{
	const FString FrameBeamTopUV = TEXT("/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab");
	const FString FrameBeamTopUVPIE = TEXT("/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/UEDPIE_9_LV_FrameBeamTopUVLab");
#if UE_BUILD_SHIPPING
	TestTrue(TEXT("Shipping top-UV Game menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FrameBeamTopUV, EWorldType::Game).IsNone());
	TestTrue(TEXT("Shipping top-UV canonical PIE menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FrameBeamTopUV, EWorldType::PIE).IsNone());
	TestTrue(TEXT("Shipping top-UV prefixed PIE menu and replay rejected"), FDYEntryLoopTestSeam::MenuMap(FrameBeamTopUVPIE, EWorldType::PIE).IsNone());
#else
	TestEqual(TEXT("Top-UV Game replays to exactly its own map"), FDYEntryLoopTestSeam::MenuMap(FrameBeamTopUV, EWorldType::Game), FName(*FrameBeamTopUV));
	TestEqual(TEXT("Top-UV canonical PIE identity"), FDYEntryLoopTestSeam::MenuMap(FrameBeamTopUV, EWorldType::PIE), FName(*FrameBeamTopUV));
	TestEqual(TEXT("Top-UV PIE prefix removed from same-map replay target"), FDYEntryLoopTestSeam::MenuMap(FrameBeamTopUVPIE, EWorldType::PIE), FName(*FrameBeamTopUV));
#endif
	for (const FString& Rejected : {
		FString(), FString(TEXT("LV_FrameBeamTopUVLab")),
		FrameBeamTopUV + TEXT("_Other"), FrameBeamTopUV + TEXT(".umap"), FrameBeamTopUV + TEXT("?game=Other"),
		FString(TEXT("/Game/Other/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FrameBeamTopUV/Other/LV_FrameBeamTopUVLab")),
		FrameBeamTopUVPIE + TEXT("_Other"), FrameBeamTopUVPIE + TEXT(".umap"), FrameBeamTopUVPIE + TEXT("?game=Other") })
	{
		TestTrue(FString::Printf(TEXT("Top-UV Game rejects nonexact package: %s"), *Rejected),
			FDYEntryLoopTestSeam::MenuMap(Rejected, EWorldType::Game).IsNone());
		TestTrue(FString::Printf(TEXT("Top-UV PIE rejects nonexact package: %s"), *Rejected),
			FDYEntryLoopTestSeam::MenuMap(Rejected, EWorldType::PIE).IsNone());
	}
	for (const EWorldType::Type Type : { EWorldType::None, EWorldType::Editor, EWorldType::EditorPreview,
		EWorldType::GamePreview, EWorldType::GameRPC, EWorldType::Inactive, static_cast<EWorldType::Type>(255) })
	{
		TestTrue(FString::Printf(TEXT("Top-UV canonical package rejects nonplay world type %d"), static_cast<int32>(Type)),
			FDYEntryLoopTestSeam::MenuMap(FrameBeamTopUV, Type).IsNone());
		TestTrue(FString::Printf(TEXT("Top-UV PIE package rejects nonplay world type %d"), static_cast<int32>(Type)),
			FDYEntryLoopTestSeam::MenuMap(FrameBeamTopUVPIE, Type).IsNone());
	}
	for (const FString& ExistingMap : {
		FString(TEXT("/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev")),
		FString(TEXT("/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab")) })
	{
		int32 SlashIndex = INDEX_NONE;
		if (!ExistingMap.FindLastChar(TEXT('/'), SlashIndex))
		{
			AddError(TEXT("Prior exact map fixture must contain its package directory"));
			continue;
		}
		const FString ExistingPIE = ExistingMap.Left(SlashIndex + 1) + TEXT("UEDPIE_12_") + ExistingMap.Mid(SlashIndex + 1);
#if UE_BUILD_SHIPPING
		TestTrue(TEXT("Shipping still rejects every prior Game map"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::Game).IsNone());
		TestTrue(TEXT("Shipping still rejects every prior canonical PIE map"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::PIE).IsNone());
		TestTrue(TEXT("Shipping still rejects every prior prefixed PIE map"), FDYEntryLoopTestSeam::MenuMap(ExistingPIE, EWorldType::PIE).IsNone());
#else
		TestEqual(TEXT("Each prior Game map keeps its exact replay identity"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::Game), FName(*ExistingMap));
		TestEqual(TEXT("Each prior canonical PIE map keeps its replay identity"), FDYEntryLoopTestSeam::MenuMap(ExistingMap, EWorldType::PIE), FName(*ExistingMap));
		TestEqual(TEXT("Each prior prefixed PIE map keeps its canonical replay identity"), FDYEntryLoopTestSeam::MenuMap(ExistingPIE, EWorldType::PIE), FName(*ExistingMap));
#endif
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYEntryChapterReplaceTest, "DengYingShanHai.EntryLoop.ReplacePlayingChapter", DYEntryTests::Flags)
bool FDYEntryChapterReplaceTest::RunTest(const FString& Parameters)
{
	DYEntryTests::FFixture F;
	if (!TestTrue(TEXT("Fixture"), F.Valid())) { return false; }
	TestTrue(TEXT("Start the opening act"), FDYEntryLoopTestSeam::Start(*F.Director, F.Stage));
	F.Light->GetLightControlComponent()->SetNormalizedValue(0.9);
	FDYEntryLoopTestSeam::EnableCampaign(*F.Director);
	ADYStagePresentation* Rogue = F.World->SpawnActor<ADYStagePresentation>();
	TestFalse(TEXT("Another stage cannot replace the running chapter"), FDYEntryLoopTestSeam::StartChapter(*F.Director, Rogue, 2));
	const FGuid Token = FDYEntryLoopTestSeam::Token(*F.Director);
	TestTrue(TEXT("A playing chapter can be replaced"), FDYEntryLoopTestSeam::StartChapter(*F.Director, F.Stage, 2));
	const FDYActSequenceSnapshot Snap = F.Director->GetActSequenceSnapshot();
	TestEqual(TEXT("Third chapter"), Snap.ChapterIndex, 2);
	TestEqual(TEXT("Opens on its first step"), Snap.ActIndex, 0);
	TestEqual(TEXT("Playing"), Snap.Phase, EDYActSequencePhase::Playing);
	TestEqual(TEXT("Title"), Snap.ActTitle.ToString(), FString(TEXT("断首犹立")));
	TestTrue(TEXT("New activation"), FDYEntryLoopTestSeam::Token(*F.Director).IsValid() && FDYEntryLoopTestSeam::Token(*F.Director) != Token);
	TestEqual(TEXT("Light reset off the old value"), F.Light->GetLightControlComponent()->GetNormalizedValue(), 0.15);
	TestFalse(TEXT("Plain start still cannot restart a running chapter"), FDYEntryLoopTestSeam::Start(*F.Director, F.Stage));
	return true;
}
#endif
