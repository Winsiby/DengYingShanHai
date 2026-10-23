#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Core/DYReleaseEntryPlayerController.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UObjectGlobals.h"

struct FDYReleaseEntryTestSeam
{
	static FName MenuMap(const FString& PackageName, EWorldType::Type WorldType)
	{
		return ADYReleaseEntryPlayerController::ResolveReleaseEntryMapName(PackageName, WorldType);
	}
	static FName CurrentMap(const ADYReleaseEntryPlayerController& Controller)
	{
		return Controller.GetCurrentDevEntryMap();
	}
};

namespace DYReleaseEntryTests
{
	constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext
		| EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter;
	const FString MainMap = TEXT("/Game/DengYingShanHai/Maps/L_DY_Main");
	const FString PIEMap = TEXT("/Game/DengYingShanHai/Maps/UEDPIE_19_L_DY_Main");

	/** Unsaved, isolated real world. Its PIE-prefixed package cannot collide with the authored map. */
	struct FScopedWorld
	{
		TStrongObjectPtr<UPackage> Package;
		TStrongObjectPtr<UWorld> World;
		ADYReleaseEntryPlayerController* Controller = nullptr;

		FScopedWorld()
		{
			if (!GEngine) { return; }
			static uint32 NextPackageId = 10000;
			FString PackageName;
			do
			{
				PackageName = FString::Printf(TEXT("/Game/DengYingShanHai/Maps/UEDPIE_%u_L_DY_Main"), NextPackageId++);
			} while (FindPackage(nullptr, *PackageName));
			Package.Reset(CreatePackage(*PackageName));
			if (!Package) { return; }
			Package->SetFlags(RF_Transient);
			const FName WorldName = MakeUniqueObjectName(Package.Get(), UWorld::StaticClass(), TEXT("DYReleaseEntryRoutingWorld"));
			World.Reset(UWorld::CreateWorld(EWorldType::Game, false, WorldName, Package.Get(), false));
			if (!World) { return; }
			GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World.Get());
			World->InitializeActorsForPlay(FURL());
			Controller = World->SpawnActor<ADYReleaseEntryPlayerController>();
		}

		~FScopedWorld()
		{
			if (World && GEngine)
			{
				if (World->HasBegunPlay()) { World->EndPlay(EEndPlayReason::Quit); }
				GEngine->DestroyWorldContext(World.Get());
				World->DestroyWorld(false);
			}
			World.Reset();
			Package.Reset();
		}
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYReleaseEntryMapIdentityTest,
	"DengYingShanHai.ReleaseEntry.ExactMainIdentityAndReplayTarget", DYReleaseEntryTests::Flags)
bool FDYReleaseEntryMapIdentityTest::RunTest(const FString& Parameters)
{
	const FName MainName(*DYReleaseEntryTests::MainMap);
	for (const EWorldType::Type Type : {EWorldType::Game, EWorldType::PIE})
	{
		TestEqual(TEXT("Main map opens and replays to its exact canonical identity"),
			FDYReleaseEntryTestSeam::MenuMap(DYReleaseEntryTests::MainMap, Type), MainName);
		TestEqual(TEXT("PIE prefix never escapes into the replay destination"),
			FDYReleaseEntryTestSeam::MenuMap(DYReleaseEntryTests::PIEMap, Type), MainName);
	}
	TestNull(TEXT("No reflected arbitrary release destination resolver"),
		ADYReleaseEntryPlayerController::StaticClass()->FindFunctionByName(TEXT("ResolveReleaseEntryMapName")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYReleaseEntryRejectedContextTest,
	"DengYingShanHai.ReleaseEntry.RejectWrongPathsAndWorldContexts", DYReleaseEntryTests::Flags)
bool FDYReleaseEntryRejectedContextTest::RunTest(const FString& Parameters)
{
	for (const FString& Package : {
		FString(), FString(TEXT("L_DY_Main")),
		DYReleaseEntryTests::MainMap + TEXT("_Other"), DYReleaseEntryTests::MainMap + TEXT(".umap"),
		DYReleaseEntryTests::MainMap + TEXT(".L_DY_Main"), DYReleaseEntryTests::MainMap + TEXT("?game=Other"),
		DYReleaseEntryTests::PIEMap + TEXT("_Other"), DYReleaseEntryTests::PIEMap + TEXT("?game=Other"),
		FString(TEXT("/Game/Other/Maps/L_DY_Main")),
		FString(TEXT("/Game/DengYingShanHai/Other/L_DY_Main")),
		FString(TEXT("/Game/DengYingShanHai/Dev/Maps/L_DY_Main")),
		FString(TEXT("/Game/DengYingShanHai/Maps/L_DY_Main/Other")),
		FString(TEXT("/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev")),
		FString(TEXT("/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab")),
		FString(TEXT("/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab"))})
	{
		for (const EWorldType::Type Type : {EWorldType::Game, EWorldType::PIE})
		{
			TestTrue(FString::Printf(TEXT("Release menu and replay reject wrong package %s in type %d"),
				*Package, static_cast<int32>(Type)), FDYReleaseEntryTestSeam::MenuMap(Package, Type).IsNone());
		}
		if (Package.StartsWith(TEXT("/Game/DengYingShanHai/Dev/")))
		{
			int32 SlashIndex = INDEX_NONE;
			if (!Package.FindLastChar(TEXT('/'), SlashIndex)) { AddError(TEXT("Dev rejection fixture must contain a directory")); continue; }
			const FString Prefixed = Package.Left(SlashIndex + 1) + TEXT("UEDPIE_19_") + Package.Mid(SlashIndex + 1);
			TestTrue(TEXT("PIE prefix never makes an old Dev map a formal destination"),
				FDYReleaseEntryTestSeam::MenuMap(Prefixed, EWorldType::PIE).IsNone());
		}
	}
	for (const EWorldType::Type Type : {EWorldType::None, EWorldType::Editor, EWorldType::EditorPreview,
		EWorldType::GamePreview, EWorldType::GameRPC, EWorldType::Inactive, static_cast<EWorldType::Type>(255)})
	{
		TestTrue(TEXT("Nonplay world cannot open a menu or travel"),
			FDYReleaseEntryTestSeam::MenuMap(DYReleaseEntryTests::MainMap, Type).IsNone());
		TestTrue(TEXT("PIE-looking package cannot bypass world type"),
			FDYReleaseEntryTestSeam::MenuMap(DYReleaseEntryTests::PIEMap, Type).IsNone());
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYReleaseEntryInheritedWorldRoutingTest,
	"DengYingShanHai.ReleaseEntry.InheritedFlowUsesActualWorldIdentity", DYReleaseEntryTests::Flags)
bool FDYReleaseEntryInheritedWorldRoutingTest::RunTest(const FString& Parameters)
{
	UClass* ReleaseClass = ADYReleaseEntryPlayerController::StaticClass();
	UClass* DevClass = ADYDevEntryPlayerController::StaticClass();
	TestTrue(TEXT("Release controller inherits the accepted entry-loop implementation"), ReleaseClass->GetSuperClass() == DevClass);
	for (const FName Intent : {FName(TEXT("RequestStartExperience")), FName(TEXT("RequestReplayExperience")),
		FName(TEXT("RequestQuitExperience")), FName(TEXT("GetEntryPanel"))})
	{
		TestNotNull(TEXT("Accepted player intent remains available"), ReleaseClass->FindFunctionByName(Intent));
		TestTrue(TEXT("Release exposes the same inherited function, not a duplicate flow"),
			ReleaseClass->FindFunctionByName(Intent) == DevClass->FindFunctionByName(Intent));
	}
	const ADYReleaseEntryPlayerController* Default = GetDefault<ADYReleaseEntryPlayerController>();
	TestTrue(TEXT("CDO has no world and no replay destination"), FDYReleaseEntryTestSeam::CurrentMap(*Default).IsNone());
	TestEqual(TEXT("CDO cannot show a running-world panel"), Default->GetEntryPanel(), EDYDevEntryPanel::Hidden);

	DYReleaseEntryTests::FScopedWorld Fixture;
	if (!TestTrue(TEXT("Actual isolated world and spawned controller"), Fixture.World && Fixture.Controller)) { return false; }
	TestTrue(TEXT("Spawned controller belongs to this exact world"), Fixture.Controller->GetWorld() == Fixture.World.Get());
	TestEqual(TEXT("Runtime override reads the actual world package"), FDYReleaseEntryTestSeam::CurrentMap(*Fixture.Controller),
		FName(*DYReleaseEntryTests::MainMap));
	const ADYDevEntryPlayerController* SharedFlow = Fixture.Controller;
	TestEqual(TEXT("Inherited public panel reaches release routing and waits for actual dependencies"),
		SharedFlow->GetEntryPanel(), EDYDevEntryPanel::Waiting);
	TestFalse(TEXT("Ready-less inherited start cannot start a sequence"), Fixture.Controller->RequestStartExperience());
	TestFalse(TEXT("Ready-less inherited replay cannot queue travel"), Fixture.Controller->RequestReplayExperience());
	return true;
}

#endif
