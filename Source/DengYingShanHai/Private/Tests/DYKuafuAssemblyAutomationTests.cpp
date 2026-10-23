#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/SkeletalMesh.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Animation/AnimSingleNodeInstance.h"

namespace DYKuafuAssemblyTests
{
	constexpr EAutomationTestFlags TestFlags =
		EAutomationTestFlags::EditorContext |
		EAutomationTestFlags::EngineFilter;

	const TCHAR* const KuafuBpPath =
		TEXT("/Game/DengYingShanHai/Dev/KuafuAppearance/Presentation/BP_DYKuafuPuppet_Fitted.BP_DYKuafuPuppet_Fitted_C");

	struct FScopedTestWorld
	{
		FScopedTestWorld()
		{
			if (!GEngine)
			{
				return;
			}

			const FName WorldName = MakeUniqueObjectName(
				nullptr,
				UWorld::StaticClass(),
				TEXT("DYKuafuAssemblyWorld"),
				EUniqueObjectNameOptions::GloballyUnique);
			FWorldContext& WorldContext = GEngine->CreateNewWorldContext(EWorldType::Game);
			World = UWorld::CreateWorld(EWorldType::Game, false, WorldName, GetTransientPackage());
			if (!World)
			{
				return;
			}

			World->AddToRoot();
			bIsRooted = true;
			WorldContext.SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
		}

		~FScopedTestWorld()
		{
			if (!World || !GEngine)
			{
				return;
			}

			GEngine->DestroyWorldContext(World);
			World->DestroyWorld(false);
			if (bIsRooted)
			{
				World->RemoveFromRoot();
			}
			World = nullptr;
		}

		UWorld* World = nullptr;

	private:
		bool bIsRooted = false;
	};

	AActor* SpawnKuafu(UWorld* World)
	{
		UClass* KuafuClass = LoadObject<UClass>(nullptr, DYKuafuAssemblyTests::KuafuBpPath);
		if (!KuafuClass)
		{
			return nullptr;
		}

		FActorSpawnParameters SpawnParameters;
		SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		AActor* Actor = World->SpawnActor<AActor>(
			KuafuClass,
			FTransform(FRotator::ZeroRotator, FVector::ZeroVector),
			SpawnParameters);
		if (Actor)
		{
			Actor->RegisterAllComponents();
		}
		return Actor;
	}

	USkeletalMeshComponent* FindKuafuMesh(AActor* Actor)
	{
		TArray<USkeletalMeshComponent*> SkeletalComps;
		Actor->GetComponents<USkeletalMeshComponent>(SkeletalComps);
		for (USkeletalMeshComponent* Component : SkeletalComps)
		{
			if (Component && Component->GetFName() == TEXT("KuafuMesh"))
			{
				return Component;
			}
		}
		return nullptr;
	}

	UStaticMeshComponent* FindNamedStaticMesh(AActor* Actor, const TCHAR* Name)
	{
		TArray<UStaticMeshComponent*> StaticComps;
		Actor->GetComponents<UStaticMeshComponent>(StaticComps);
		for (UStaticMeshComponent* Component : StaticComps)
		{
			if (Component && Component->GetFName() == Name)
			{
				return Component;
			}
		}
		return nullptr;
	}

	int32 CountSkeletalMeshComponents(AActor* Actor)
	{
		TArray<USkeletalMeshComponent*> SkeletalComps;
		Actor->GetComponents<USkeletalMeshComponent>(SkeletalComps);
		return SkeletalComps.Num();
	}

	UAnimationAsset* GetPlayingAnimation(USkeletalMeshComponent* Mesh)
	{
		if (!Mesh)
		{
			return nullptr;
		}
		if (UAnimSingleNodeInstance* Single = Cast<UAnimSingleNodeInstance>(Mesh->GetAnimInstance()))
		{
			return Single->GetAnimationAsset();
		}
		return nullptr;
	}
}

// Stage A1/A2 machine verification: spawn the fitted Kuafu BP (Construction Script runs
// during spawn) and assert the SCS-created KuafuMesh, its skeletal mesh assignment, the
// inherited grey-box components, their visibility and the animation mode.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYKuafuSCSAssemblyDefaultsTest,
	"DengYingShanHai.StageA.KuafuFitted.SCSAssemblyDefaults",
	DYKuafuAssemblyTests::TestFlags)

bool FDYKuafuSCSAssemblyDefaultsTest::RunTest(const FString& Parameters)
{
	DYKuafuAssemblyTests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}

	AActor* Kuafu = DYKuafuAssemblyTests::SpawnKuafu(TestWorld.World);
	TestNotNull(TEXT("BP_DYKuafuPuppet_Fitted spawns"), Kuafu);
	if (!Kuafu)
	{
		return false;
	}

	// A1: the SCS-created KuafuMesh must exist on the instance (CDO cannot show it,
	// the spawned instance's Construction Script must).
	USkeletalMeshComponent* KuafuMesh = DYKuafuAssemblyTests::FindKuafuMesh(Kuafu);
	TestNotNull(TEXT("SCS created the KuafuMesh skeletal mesh component on the instance"), KuafuMesh);
	if (!KuafuMesh)
	{
		Kuafu->Destroy();
		return false;
	}

	// A1: its skeletal mesh must be the M-01 v04 Kuafu, not null and not a fallback.
	const USkeletalMesh* AssignedMesh = KuafuMesh->GetSkeletalMeshAsset();
	TestNotNull(TEXT("KuafuMesh has a skeletal mesh assigned"), AssignedMesh);
	if (AssignedMesh)
	{
		TestTrue(
			TEXT("KuafuMesh is assigned SK_DY_Kuafu_M01_LeftGrip_v04"),
			AssignedMesh->GetPathName().Contains(TEXT("SK_DY_Kuafu_M01_LeftGrip_v04")));
	}

	// Transform evidence for the review record (values recorded, not judged here).
	AddInfo(FString::Printf(
		TEXT("KuafuMesh RelativeLocation=%s RelativeRotation=%s RelativeScale3D=%s"),
		*KuafuMesh->GetRelativeLocation().ToString(),
		*KuafuMesh->GetRelativeRotation().ToString(),
		*KuafuMesh->GetRelativeScale3D().ToString()));

	// A2: the inherited grey-box components must still exist (C++ owns them).
	UStaticMeshComponent* Torso = DYKuafuAssemblyTests::FindNamedStaticMesh(Kuafu, TEXT("Torso"));
	UStaticMeshComponent* Head = DYKuafuAssemblyTests::FindNamedStaticMesh(Kuafu, TEXT("Head"));
	UStaticMeshComponent* Staff = DYKuafuAssemblyTests::FindNamedStaticMesh(Kuafu, TEXT("Staff"));
	TestNotNull(TEXT("Inherited Torso component exists"), Torso);
	TestNotNull(TEXT("Inherited Head component exists"), Head);
	TestNotNull(TEXT("Inherited Staff component exists"), Staff);

	if (Staff)
	{
		const UStaticMesh* StaffMesh = Staff->GetStaticMesh();
		TestNotNull(TEXT("Staff has a static mesh assigned"), StaffMesh);
		if (StaffMesh)
		{
			TestTrue(
				TEXT("Staff uses the real SM_DY_Kuafu_Staff_M01_v04 asset"),
				StaffMesh->GetPathName().Contains(TEXT("SM_DY_Kuafu_Staff_M01_v04")));
		}
	}

	// A2: record the actual visibility of the grey-box parts. Both visible together
	// would be the "grey box overlapping the new mesh" risk from the review.
	const bool bTorsoVisible = Torso ? Torso->IsVisible() : false;
	const bool bHeadVisible = Head ? Head->IsVisible() : false;
	AddInfo(FString::Printf(
		TEXT("GreyBoxVisibility Torso=%d Head=%d (1=visible in construction state)"),
		bTorsoVisible ? 1 : 0,
		bHeadVisible ? 1 : 0));
	if (bTorsoVisible || bHeadVisible)
	{
		AddWarning(TEXT(
			"Torso/Head are visible in the construction state. Visual overlap with KuafuMesh "
			"must be judged in PIE by a human; this test records the state, it does not pass/fail it."));
	}

	// Animation mode evidence: the review expects AnimationSingleNode with authored poses.
	AddInfo(FString(TEXT("KuafuMesh AnimationMode is AnimationSingleNode: "))
		+ (KuafuMesh->GetAnimationMode() == EAnimationMode::AnimationSingleNode ? TEXT("true") : TEXT("false")));

	Kuafu->Destroy();
	return true;
}

// Stage A4 reconstruction consistency: rerunning the Construction Script must not
// duplicate the SCS component or change the assembled state.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYKuafuReconstructionConsistencyTest,
	"DengYingShanHai.StageA.KuafuFitted.ReconstructionConsistency",
	DYKuafuAssemblyTests::TestFlags)

bool FDYKuafuReconstructionConsistencyTest::RunTest(const FString& Parameters)
{
	DYKuafuAssemblyTests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}

	AActor* Kuafu = DYKuafuAssemblyTests::SpawnKuafu(TestWorld.World);
	TestNotNull(TEXT("BP_DYKuafuPuppet_Fitted spawns"), Kuafu);
	if (!Kuafu)
	{
		return false;
	}

	USkeletalMeshComponent* KuafuMeshBefore = DYKuafuAssemblyTests::FindKuafuMesh(Kuafu);
	TestNotNull(TEXT("KuafuMesh exists after spawn"), KuafuMeshBefore);
	const int32 SkeletalCountBefore = DYKuafuAssemblyTests::CountSkeletalMeshComponents(Kuafu);
	TestEqual(TEXT("Exactly one skeletal mesh component after spawn"), SkeletalCountBefore, 1);

	// Rerun the Construction Script on the same instance.
	Kuafu->RerunConstructionScripts();

	USkeletalMeshComponent* KuafuMeshAfter = DYKuafuAssemblyTests::FindKuafuMesh(Kuafu);
	TestNotNull(TEXT("KuafuMesh still exists after RerunConstructionScripts"), KuafuMeshAfter);
	const int32 SkeletalCountAfter = DYKuafuAssemblyTests::CountSkeletalMeshComponents(Kuafu);
	TestEqual(
		TEXT("RerunConstructionScripts does not duplicate the skeletal mesh component"),
		SkeletalCountAfter, 1);

	if (KuafuMeshBefore && KuafuMeshAfter)
	{
		const USkeletalMesh* MeshAfter = KuafuMeshAfter->GetSkeletalMeshAsset();
		TestNotNull(TEXT("KuafuMesh keeps a skeletal mesh after rerun"), MeshAfter);
		if (MeshAfter)
		{
			TestTrue(
					TEXT("KuafuMesh keeps SK_DY_Kuafu_M01_LeftGrip_v04 after rerun"),
					MeshAfter->GetPathName().Contains(TEXT("SK_DY_Kuafu_M01_LeftGrip_v04")));
		}
	}

	UStaticMeshComponent* TorsoAfter = DYKuafuAssemblyTests::FindNamedStaticMesh(Kuafu, TEXT("Torso"));
	UStaticMeshComponent* HeadAfter = DYKuafuAssemblyTests::FindNamedStaticMesh(Kuafu, TEXT("Head"));
	UStaticMeshComponent* StaffAfter = DYKuafuAssemblyTests::FindNamedStaticMesh(Kuafu, TEXT("Staff"));
	TestNotNull(TEXT("Torso survives the rerun"), TorsoAfter);
	TestNotNull(TEXT("Head survives the rerun"), HeadAfter);
	TestNotNull(TEXT("Staff survives the rerun"), StaffAfter);

	Kuafu->Destroy();
	return true;
}

// Stage A3 pose mapping: driving PuppetControl through SetNormalizedValue broadcasts
// OnControlChanged; the BP's ApplyKuafuPose must switch KuafuMesh between the three
// authored pose animations (P02_StrideReach / P02_StrideMid / P02_StrideBack).
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYKuafuPoseMappingTest,
	"DengYingShanHai.StageA.KuafuFitted.PoseMapping",
	DYKuafuAssemblyTests::TestFlags)

bool FDYKuafuPoseMappingTest::RunTest(const FString& Parameters)
{
	DYKuafuAssemblyTests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}

	AActor* Kuafu = DYKuafuAssemblyTests::SpawnKuafu(TestWorld.World);
	TestNotNull(TEXT("BP_DYKuafuPuppet_Fitted spawns"), Kuafu);
	if (!Kuafu)
	{
		return false;
	}

	USkeletalMeshComponent* KuafuMesh = DYKuafuAssemblyTests::FindKuafuMesh(Kuafu);
	TestNotNull(TEXT("KuafuMesh exists for the pose mapping"), KuafuMesh);
	if (!KuafuMesh)
	{
		Kuafu->Destroy();
		return false;
	}

	// The BP binds OnControlChanged inside ReceiveBeginPlay; the transient fixture must
	// dispatch it, otherwise the binding never runs and the pose pipeline looks broken.
	Kuafu->DispatchBeginPlay();

	UDYPuppetControlComponent* Control = Kuafu->FindComponentByClass<UDYPuppetControlComponent>();
	TestNotNull(TEXT("PuppetControl component exists"), Control);
	if (!Control)
	{
		Kuafu->Destroy();
		return false;
	}

	const FName InitialPoseId = Control->GetPoseId();
	AddInfo(FString::Printf(
		TEXT("Initial NormalizedValue=%.4f PoseId=%s AnimToPlay=%s"),
		Control->GetNormalizedValue(),
		*InitialPoseId.ToString(),
		DYKuafuAssemblyTests::GetPlayingAnimation(KuafuMesh)
			? *DYKuafuAssemblyTests::GetPlayingAnimation(KuafuMesh)->GetPathName()
			: TEXT("None")));

	// Drive the rail to the left end and the right end. Each change broadcasts
	// OnControlChanged, which the BP's ApplyKuafuPose must answer with a new animation.
	Control->SetNormalizedValue(0.0);
	const FName PoseIdLow = Control->GetPoseId();
	UAnimationAsset* AnimLow = DYKuafuAssemblyTests::GetPlayingAnimation(KuafuMesh);
	AddInfo(FString::Printf(
		TEXT("Low NormalizedValue=0.0 PoseId=%s AnimToPlay=%s"),
		*PoseIdLow.ToString(),
		AnimLow ? *AnimLow->GetPathName() : TEXT("None")));

	Control->SetNormalizedValue(1.0);
	const FName PoseIdHigh = Control->GetPoseId();
	UAnimationAsset* AnimHigh = DYKuafuAssemblyTests::GetPlayingAnimation(KuafuMesh);
	AddInfo(FString::Printf(
		TEXT("High NormalizedValue=1.0 PoseId=%s AnimToPlay=%s"),
		*PoseIdHigh.ToString(),
		AnimHigh ? *AnimHigh->GetPathName() : TEXT("None")));

	// The rail endpoints must map to different pose ids.
	TestTrue(
		TEXT("Rail endpoints map to different PoseIds"),
		PoseIdLow != PoseIdHigh);
	TestTrue(
		TEXT("Both endpoint PoseIds are configured (not NAME_None)"),
		PoseIdLow != NAME_None && PoseIdHigh != NAME_None);

	// Each pose must select one of the three authored Kuafu pose animations.
	auto IsKuafuPoseAsset = [](const UAnimationAsset* Asset)
	{
		if (!Asset)
		{
			return false;
		}
		const FString Path = Asset->GetPathName();
		return Path.Contains(TEXT("A_DY_Kuafu_Poses"))
			&& (Path.Contains(TEXT("Reach")) || Path.Contains(TEXT("StrideMid")) || Path.Contains(TEXT("StrideBack")));
	};
	TestTrue(TEXT("Low endpoint selects an authored Kuafu pose animation"), IsKuafuPoseAsset(AnimLow));
	TestTrue(TEXT("High endpoint selects an authored Kuafu pose animation"), IsKuafuPoseAsset(AnimHigh));
	TestTrue(
		TEXT("Different PoseIds select different animations"),
		AnimLow != AnimHigh);

	// The animation mode must stay in single-node play, per the review's expectation.
	TestTrue(
		TEXT("KuafuMesh uses AnimationSingleNode"),
		KuafuMesh->GetAnimationMode() == EAnimationMode::AnimationSingleNode);

	Kuafu->Destroy();
	return true;
}

// Stage A root-cause diagnosis: separate "delegate never bound" from "event internal
// short-circuit". ProcessEvent calls the BP's ApplyKuafuPose directly, bypassing the
// OnControlChanged delegate entirely.
//   If a direct call switches the animation -> the event works; the delegate binding
//   is the broken link (hypothesis 1).
//   If a direct call does not switch -> the short-circuit/branch inside the event is
//   the broken link (hypothesis 2).
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYKuafuDelegateBindingDiagnosisTest,
	"DengYingShanHai.StageA.KuafuFitted.DelegateBindingDiagnosis",
	DYKuafuAssemblyTests::TestFlags)

bool FDYKuafuDelegateBindingDiagnosisTest::RunTest(const FString& Parameters)
{
	DYKuafuAssemblyTests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}

	AActor* Kuafu = DYKuafuAssemblyTests::SpawnKuafu(TestWorld.World);
	TestNotNull(TEXT("BP_DYKuafuPuppet_Fitted spawns"), Kuafu);
	if (!Kuafu)
	{
		return false;
	}

	USkeletalMeshComponent* KuafuMesh = DYKuafuAssemblyTests::FindKuafuMesh(Kuafu);
	TestNotNull(TEXT("KuafuMesh exists"), KuafuMesh);
	UDYPuppetControlComponent* Control = Kuafu ? Kuafu->FindComponentByClass<UDYPuppetControlComponent>() : nullptr;
	TestNotNull(TEXT("PuppetControl exists"), Control);
	if (!KuafuMesh || !Control || !Kuafu)
	{
		Kuafu->Destroy();
		return false;
	}

	// Evidence 1: binding state before and after the real BeginPlay lifecycle step.
	const bool bBoundBefore = Control->OnControlChanged.IsBound();
	AddInfo(FString::Printf(TEXT("DIAG before BeginPlay: IsBound=%d"), bBoundBefore ? 1 : 0));
	Kuafu->DispatchBeginPlay();
	const bool bDelegateBound = Control->OnControlChanged.IsBound();
	AddInfo(FString::Printf(TEXT("DIAG after BeginPlay: IsBound=%d"), bDelegateBound ? 1 : 0));
	TestTrue(
		TEXT("ReceiveBeginPlay binds OnControlChanged"),
		bDelegateBound);

	// Evidence 2: call the BP event directly, bypassing the delegate.
	UFunction* ApplyPoseFn = Kuafu->FindFunction(TEXT("ApplyKuafuPose"));
	TestNotNull(TEXT("BP exposes ApplyKuafuPose as a callable function"), ApplyPoseFn);
	if (!ApplyPoseFn)
	{
		Kuafu->Destroy();
		return false;
	}

	struct FPoseParams
	{
		double NormalizedValue;
		FName PoseId;
	};

	// Direct call with a known PoseId that differs from the initial one.
	const FName ReachId(TEXT("P02_StrideReach"));
	FPoseParams ReachParams{ 1.0, ReachId };
	Kuafu->ProcessEvent(ApplyPoseFn, &ReachParams);

	UAnimationAsset* AfterDirectReach = DYKuafuAssemblyTests::GetPlayingAnimation(KuafuMesh);
	AddInfo(FString::Printf(
		TEXT("DIAG after direct ApplyKuafuPose(1.0, P02_StrideReach): playing=%s"),
		AfterDirectReach ? *AfterDirectReach->GetPathName() : TEXT("None")));
	const bool bDirectReachSwitched = AfterDirectReach
		&& AfterDirectReach->GetPathName().Contains(TEXT("Reach"));
	TestTrue(
		TEXT("Direct ApplyKuafuPose switches the playing animation to Reach"),
		bDirectReachSwitched);

	// Evidence 3: repeat the SAME pose notification (dedup branch must not retrigger).
	Kuafu->ProcessEvent(ApplyPoseFn, &ReachParams);
	UAnimationAsset* AfterRepeat = DYKuafuAssemblyTests::GetPlayingAnimation(KuafuMesh);
	AddInfo(FString::Printf(
		TEXT("DIAG after repeat same-pose call: playing=%s"),
		AfterRepeat ? *AfterRepeat->GetPathName() : TEXT("None")));
	TestTrue(
		TEXT("Repeating the same pose keeps the same animation (no mis-dedup of a real change)"),
		AfterRepeat && AfterRepeat->GetPathName().Contains(TEXT("Reach")));

	// Evidence 4: a different pose must switch again.
	const FName BackId(TEXT("P02_StrideBack"));
	FPoseParams BackParams{ 0.0, BackId };
	Kuafu->ProcessEvent(ApplyPoseFn, &BackParams);
	UAnimationAsset* AfterDirectBack = DYKuafuAssemblyTests::GetPlayingAnimation(KuafuMesh);
	AddInfo(FString::Printf(
		TEXT("DIAG after direct ApplyKuafuPose(0.0, P02_StrideBack): playing=%s"),
		AfterDirectBack ? *AfterDirectBack->GetPathName() : TEXT("None")));
	const bool bDirectBackSwitched = AfterDirectBack
		&& AfterDirectBack->GetPathName().Contains(TEXT("StrideBack"));
	TestTrue(
		TEXT("Direct ApplyKuafuPose switches the playing animation to StrideBack"),
		bDirectBackSwitched);

	// Verdict (updated after the lifecycle experiment): the event works and the
	// delegate is bound during ReceiveBeginPlay; the earlier IsBound()=0 was the
	// fixture never dispatching BeginPlay, not a product defect.
	if (bDirectReachSwitched && bDirectBackSwitched)
	{
		AddInfo(TEXT(
			"VERDICT: ApplyKuafuPose works when called directly, and OnControlChanged binds "
			"during ReceiveBeginPlay. The pose pipeline is functional in the real lifecycle."));
	}
	else
	{
		AddInfo(TEXT(
			"VERDICT: ApplyKuafuPose does not switch even when called directly; inspect the "
			"dedup branch and SetAnimation target inside the event."));
	}

	Kuafu->Destroy();
	return true;
}

// v7 lifecycle experiment: the previous diagnosis spawned the actor WITHOUT BeginPlay
// (transient worlds never dispatch it automatically). If the BP binds OnControlChanged
// inside ReceiveBeginPlay, the earlier IsBound()=0 was a fixture artifact, not a product
// defect. This test dispatches BeginPlay explicitly and re-measures.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYKuafuBeginPlayBindingTest,
	"DengYingShanHai.StageA.KuafuFitted.BeginPlayBinding",
	DYKuafuAssemblyTests::TestFlags)

bool FDYKuafuBeginPlayBindingTest::RunTest(const FString& Parameters)
{
	DYKuafuAssemblyTests::FScopedTestWorld TestWorld;
	TestNotNull(TEXT("Transient game world is created"), TestWorld.World);
	if (!TestWorld.World)
	{
		return false;
	}

	AActor* Kuafu = DYKuafuAssemblyTests::SpawnKuafu(TestWorld.World);
	TestNotNull(TEXT("BP_DYKuafuPuppet_Fitted spawns"), Kuafu);
	if (!Kuafu)
	{
		return false;
	}

	UDYPuppetControlComponent* Control = Kuafu->FindComponentByClass<UDYPuppetControlComponent>();
	USkeletalMeshComponent* KuafuMesh = DYKuafuAssemblyTests::FindKuafuMesh(Kuafu);
	TestNotNull(TEXT("PuppetControl exists"), Control);
	TestNotNull(TEXT("KuafuMesh exists"), KuafuMesh);
	if (!Control || !KuafuMesh)
	{
		Kuafu->Destroy();
		return false;
	}

	// Measure BEFORE BeginPlay.
	const bool bBoundBefore = Control->OnControlChanged.IsBound();
	AddInfo(FString::Printf(TEXT("DIAG before BeginPlay: IsBound=%d"), bBoundBefore ? 1 : 0));

	// Dispatch BeginPlay on the same instance (the real PIE lifecycle step the earlier
	// fixture skipped). This must run the BP's ReceiveBeginPlay, where a binding node
	// would live if the BP binds during BeginPlay.
	Kuafu->DispatchBeginPlay();

	const bool bBoundAfter = Control->OnControlChanged.IsBound();
	AddInfo(FString::Printf(TEXT("DIAG after DispatchBeginPlay: IsBound=%d"), bBoundAfter ? 1 : 0));

	// If the BP binds during BeginPlay, the pose pipeline must now work end to end:
	// drive the rail and read the actually playing animation.
	UAnimationAsset* PlayingAfterDrive = nullptr;
	if (bBoundAfter)
	{
		Control->SetNormalizedValue(1.0);
		PlayingAfterDrive = DYKuafuAssemblyTests::GetPlayingAnimation(KuafuMesh);
		AddInfo(FString::Printf(
			TEXT("DIAG after BeginPlay + SetNormalizedValue(1.0): PoseId=%s playing=%s"),
			*Control->GetPoseId().ToString(),
			PlayingAfterDrive ? *PlayingAfterDrive->GetPathName() : TEXT("None")));
	}

	// Verdict for the report: distinguish fixture artifact from product defect.
	if (bBoundBefore)
	{
		AddInfo(TEXT("VERDICT: bound already before BeginPlay (binding lives in CS or earlier)."));
	}
	else if (bBoundAfter)
	{
		AddInfo(TEXT(
			"VERDICT: binding happens in ReceiveBeginPlay. The earlier IsBound()=0 was a fixture "
			"artifact (the transient fixture never dispatched BeginPlay). The BP binding logic "
			"itself works; full PIE must re-verify the visual result."));
	}
	else
	{
		AddInfo(TEXT(
			"VERDICT: still unbound even after BeginPlay. The binding node is missing, disabled, "
			"or on a non-executing path. Product defect confirmed; needs node-level GUI review."));
	}

	Kuafu->Destroy();
	return true;
}

#endif

