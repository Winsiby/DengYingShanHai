#include "Core/DYDevEntryPlayerController.h"

#include "Puppets/DYPuppetPerformanceComponent.h"

#include "Animation/AnimationAsset.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Interaction/DYPuppetActor.h"
#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Blueprint/WidgetTree.h"
#include "Components/TextBlock.h"
#include "Core/DYEntryWalkTypes.h"
#include "Core/DYStageGameMode.h"
#include "DengYingShanHai.h"
#include "Engine/Engine.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/LightComponent.h"
#include "Components/LocalLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "EngineUtils.h"
#include "Engine/World.h"
#include "GameFramework/HUD.h"
#include "GameFramework/Pawn.h"
#include "InputCoreTypes.h"
#include "Interaction/DYInteractionComponent.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundWave.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Puzzles/DYPuzzleDirector.h"
#include "Stage/DYStagePresentation.h"
#include "UI/DYInteractionHUD.h"
#include "UI/DYInteractionHUDWidget.h"
#include "Misc/App.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "TimerManager.h"
#include "UObject/UObjectIterator.h"

namespace DYDevEntry
{
	static const TCHAR* EntryMap = TEXT("/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev");
	static const TCHAR* ReadabilityMap = TEXT("/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab");
	static const TCHAR* AlignmentMap = TEXT("/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab");
	static const TCHAR* EnvironmentMap = TEXT("/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab");
	static const TCHAR* FramePostPlacementMap = TEXT("/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab");
	static const TCHAR* FrameBeamPlacementMap = TEXT("/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab");
	static const TCHAR* FrameBeamCandidateMap = TEXT("/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab");
	static const TCHAR* FrameBeamTopUVMap = TEXT("/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab");
	static const TCHAR* P02KuafuGuideMap = TEXT("/Game/DengYingShanHai/Dev/P02KuafuGuide/Maps/LV_P02KuafuGuideLab");
}

ADYDevEntryPlayerController::ADYDevEntryPlayerController()
{
	MenuWidgetClass = UDYDevEntryWidget::StaticClass();
}

FName ADYDevEntryPlayerController::ResolveDevEntryMapName(const FString& PackageName, const EWorldType::Type WorldType)
{
#if UE_BUILD_SHIPPING
	return NAME_None;
#else
	if (WorldType != EWorldType::Game && WorldType != EWorldType::PIE) { return NAME_None; }
	const FString Canonical = UWorld::RemovePIEPrefix(PackageName);
	if (Canonical == DYDevEntry::EntryMap) { return FName(DYDevEntry::EntryMap); }
	if (Canonical == DYDevEntry::ReadabilityMap) { return FName(DYDevEntry::ReadabilityMap); }
	if (Canonical == DYDevEntry::AlignmentMap) { return FName(DYDevEntry::AlignmentMap); }
	if (Canonical == DYDevEntry::EnvironmentMap) { return FName(DYDevEntry::EnvironmentMap); }
	if (Canonical == DYDevEntry::FramePostPlacementMap) { return FName(DYDevEntry::FramePostPlacementMap); }
	if (Canonical == DYDevEntry::FrameBeamPlacementMap) { return FName(DYDevEntry::FrameBeamPlacementMap); }
	if (Canonical == DYDevEntry::FrameBeamCandidateMap) { return FName(DYDevEntry::FrameBeamCandidateMap); }
	if (Canonical == DYDevEntry::FrameBeamTopUVMap) { return FName(DYDevEntry::FrameBeamTopUVMap); }
	if (Canonical == DYDevEntry::P02KuafuGuideMap) { return FName(DYDevEntry::P02KuafuGuideMap); }
	return NAME_None;
#endif
}

FName ADYDevEntryPlayerController::GetCurrentDevEntryMap() const
{
	const UWorld* World = GetWorld();
	return World ? ResolveDevEntryMapName(World->GetOutermost()->GetName(), World->WorldType) : NAME_None;
}

bool ADYDevEntryPlayerController::IsEntryLoopWorld() const { return !GetCurrentDevEntryMap().IsNone(); }

void ADYDevEntryPlayerController::StartTheatreAmbience()
{
	// Procedural BGM (made in-house, no third-party samples); skipped when the level has no audio device.
	if (AmbienceComponent || !IsTheaterEntryMap() || !GetWorld()) { return; }
	if (FPlatformMisc::GetEnvironmentVariable(TEXT("DY_MUTE_BGM")).Equals(TEXT("1"), ESearchCase::IgnoreCase)) { return; }
	if (!AmbienceWave)
	{
		AmbienceWave = LoadObject<USoundWave>(nullptr,
			TEXT("/Game/DengYingShanHai/Dev/Audio/Music/BGM_DY_MountainSea.BGM_DY_MountainSea"), nullptr,
			LOAD_NoWarn | LOAD_Quiet);
	}
	if (!AmbienceWave) { UE_LOG(LogTemp, Warning, TEXT("DY BGM: wave failed to load")); return; }
	AmbienceComponent = UGameplayStatics::SpawnSound2D(this, AmbienceWave, 0.45f, 1.f, 0.f, nullptr, false, false);
	if (AmbienceComponent) { AmbienceComponent->OnAudioFinished.AddDynamic(this, &ADYDevEntryPlayerController::HandleAmbienceFinished); }
	UE_LOG(LogTemp, Log, TEXT("DY BGM: playing duration=%.2f comp=%s"), AmbienceWave->GetDuration(), AmbienceComponent ? TEXT("ok") : TEXT("null"));
}

void ADYDevEntryPlayerController::HandleAmbienceFinished()
{
	// USoundWave has no loop flag of its own here, so the bed is re-armed on completion.
	if (AmbienceWave && GetWorld())
	{
		AmbienceComponent = UGameplayStatics::SpawnSound2D(this, AmbienceWave, 0.45f, 1.f, 0.f, nullptr, false, false);
		if (AmbienceComponent) { AmbienceComponent->OnAudioFinished.AddDynamic(this, &ADYDevEntryPlayerController::HandleAmbienceFinished); }
	}
}



void ADYDevEntryPlayerController::PlayStageCue(const int32 CueIndex)
{
	if (FPlatformMisc::GetEnvironmentVariable(TEXT("DY_MUTE_SFX")).Equals(TEXT("1"))) { return; }
	static const TCHAR* CuePaths[] = {
		TEXT("/Game/DengYingShanHai/Dev/Audio/SFX/SFX_DY_Gong.SFX_DY_Gong"),
		TEXT("/Game/DengYingShanHai/Dev/Audio/SFX/SFX_DY_Drum.SFX_DY_Drum"),
		TEXT("/Game/DengYingShanHai/Dev/Audio/SFX/SFX_DY_Resolve.SFX_DY_Resolve")
	};
	const int32 CueCount = UE_ARRAY_COUNT(CuePaths);
	if (CueIndex < 0 || CueIndex >= CueCount || !GetWorld()) { return; }
	if (CueWaves.Num() != CueCount) { CueWaves.SetNum(CueCount); }
	USoundWave* Wave = CueWaves[CueIndex];
	if (!Wave)
	{
		Wave = LoadObject<USoundWave>(nullptr, CuePaths[CueIndex], nullptr, LOAD_NoWarn | LOAD_Quiet);
		CueWaves[CueIndex] = Wave;
		if (!Wave) { UE_LOG(LogTemp, Warning, TEXT("DY SFX: cue %d failed to load"), CueIndex); return; }
	}
	// Cues are atmosphere, not a completion channel: the puzzles stay solvable with sound off.
	UGameplayStatics::SpawnSound2D(this, Wave, CueIndex == 1 ? 0.30f : 0.45f, 1.f, 0.f, nullptr, false, false);
	UE_LOG(LogTemp, Log, TEXT("DY SFX: cue=%d"), CueIndex);
	if (FPlatformMisc::GetEnvironmentVariable(TEXT("DY_SFX_PROBE")).Equals(TEXT("1")))
	{
		// Durable evidence: Shipping compiles UE_LOG out, so cues also leave a line in a probe file.
		const FString Line = FString::Printf(TEXT("cue=%d t=%.1f chapter=%d phase=%d"),
			CueIndex, GetWorld()->GetTimeSeconds(), LastCuedChapterIndex, static_cast<int32>(LastCuedPhase));
		FFileHelper::SaveStringToFile(Line + LINE_TERMINATOR,
			*(FPaths::ProjectSavedDir() / TEXT("SfxProbe.log")),
			FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), EFileWrite::FILEWRITE_Append);
	}
}

void ADYDevEntryPlayerController::PlaySequenceCue(const FDYActSequenceSnapshot& Snapshot)
{
	if (!Snapshot.bSequenceEnabled) { return; }
	const uint8 PhaseNow = static_cast<uint8>(Snapshot.Phase);
	if (Snapshot.Phase == EDYActSequencePhase::Playing && Snapshot.ChapterIndex != LastCuedChapterIndex)
	{
		LastCuedChapterIndex = Snapshot.ChapterIndex;
		PlayStageCue(1); // drum: a new chapter opens
	}
	else if (Snapshot.Phase == EDYActSequencePhase::AwaitingFinale && LastCuedPhase != PhaseNow)
	{
		PlayStageCue(2); // resolve chime: one act has settled
	}
	else if (Snapshot.Phase == EDYActSequencePhase::Complete && LastCuedPhase != PhaseNow)
	{
		PlayStageCue(0); // gong: the four acts are done
	}
	LastCuedPhase = PhaseNow;
}
void ADYDevEntryPlayerController::StartArtProbe()
{
	if (!GetWorld()) { return; }
	if (!FPlatformMisc::GetEnvironmentVariable(TEXT("DY_ART_PROBE")).Equals(TEXT("1"))) { return; }
	GetWorld()->GetTimerManager().SetTimer(ArtProbeHandle, this, &ADYDevEntryPlayerController::SampleArtProbe, 1.0f, true, 1.0f);
}

void ADYDevEntryPlayerController::SampleArtProbe()
{
	UWorld* World = GetWorld();
	if (!World) { return; }
	++ArtProbeSamples;
	const APawn* ControlledPawn = GetPawn();
	const FVector PawnLoc = ControlledPawn ? ControlledPawn->GetActorLocation() : FVector::ZeroVector;
	FVector CamLoc = FVector::ZeroVector;
	FVector CamFwd = FVector::ForwardVector;
	if (PlayerCameraManager)
	{
		CamLoc = PlayerCameraManager->GetCameraLocation();
		CamFwd = PlayerCameraManager->GetCameraRotation().Vector();
	}
	FString HitText = TEXT("none");
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(DYArtProbe), false, ControlledPawn);
	if (World->LineTraceSingleByChannel(Hit, CamLoc, CamLoc + CamFwd * 6000.0, ECC_Visibility, Params) && Hit.GetActor())
	{
		FString MeshName = TEXT("?");
		FString MatName = TEXT("?");
		if (const UStaticMeshComponent* MeshComp = Cast<UStaticMeshComponent>(Hit.GetComponent()))
		{
			if (MeshComp->GetStaticMesh()) { MeshName = MeshComp->GetStaticMesh()->GetName(); }
			if (MeshComp->GetMaterial(0)) { MatName = MeshComp->GetMaterial(0)->GetName(); }
		}
		HitText = FString::Printf(TEXT("dist=%.0f actor=%s mesh=%s mat=%s"),
			Hit.Distance, *Hit.GetActor()->GetName(), *MeshName, *MatName);
	}
	FString LightText;
	int32 LightsLogged = 0;
	for (TObjectIterator<ULocalLightComponent> It; It; ++It)
	{
		ULocalLightComponent* Light = *It;
		if (!IsValid(Light) || Light->GetWorld() != World || !Light->IsVisible()) { continue; }
		const FVector LightLoc = Light->GetComponentLocation();
		const double Dist = FVector::Dist(LightLoc, CamLoc);
		if (Dist > 2500.0) { continue; }
		const ULightComponent* BaseLight = Cast<ULightComponent>(Light);
		const float Intensity = BaseLight ? BaseLight->Intensity : 0.f;
		LightText += FString::Printf(TEXT(" | light=%s int=%.0f dist=%.0f"),
			*Light->GetName(), static_cast<double>(Intensity), Dist);
		if (++LightsLogged >= 4) { break; }
	}
	const FString Line = FString::Printf(TEXT("t=%.1f pawn=(%.0f,%.0f,%.0f) cam=(%.0f,%.0f,%.0f) hit=%s%s"),
		World->GetTimeSeconds(), PawnLoc.X, PawnLoc.Y, PawnLoc.Z,
		CamLoc.X, CamLoc.Y, CamLoc.Z, *HitText, *LightText);
	FFileHelper::SaveStringToFile(Line + LINE_TERMINATOR, *(FPaths::ProjectSavedDir() / TEXT("ArtProbe.log")),
		FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), EFileWrite::FILEWRITE_Append);
}

void ADYDevEntryPlayerController::StartPerformanceProbe()
{
	if (PerfProbeSamples > 0 || !GetWorld()) { return; }
	if (!FPlatformMisc::GetEnvironmentVariable(TEXT("DY_PERF_PROBE")).Equals(TEXT("1"))) { return; }
	GetWorld()->GetTimerManager().SetTimer(PerfProbeHandle, this, &ADYDevEntryPlayerController::SamplePerformance, 0.25f, true, 0.25f);
}

void ADYDevEntryPlayerController::SamplePerformance()
{
	UWorld* World = GetWorld();
	if (!World) { return; }
	const float Instant = static_cast<float>(1.0 / FMath::Max(FApp::GetDeltaTime(), 1.0e-4));
	PerfProbeFps = PerfProbeFps <= 0.f ? Instant : FMath::Lerp(PerfProbeFps, Instant, 0.25f);
	const float Sample = PerfProbeFps;
	++PerfProbeSamples;
	if ((PerfProbeSamples % 4) != 0) { return; }
	PerfProbeMin = FMath::Min(PerfProbeMin, Sample);
	PerfProbeMax = FMath::Max(PerfProbeMax, Sample);
	PerfProbeSeconds = World->GetTimeSeconds();
	const FString Line = FString::Printf(TEXT("t=%.1f fps=%.1f min=%.1f max=%.1f frames=%d"),
		PerfProbeSeconds, Sample, PerfProbeMin, PerfProbeMax, PerfProbeSamples);
	FFileHelper::SaveStringToFile(Line + LINE_TERMINATOR, *(FPaths::ProjectSavedDir() / TEXT("PerfProbe.log")),
		FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), EFileWrite::FILEWRITE_Append);
}
namespace DYEntryReplay
{
	/** Set by PerformReplay before OpenLevel; consumed by the reloaded controller in BeginPlay. */
	static bool bPending = false;
}

namespace DYFlowVerification
{
	// Only initialized by the opt-in harness; survives the real OpenLevel replay, not process exit.
	static bool bInitialized = false;
	static bool bFinished = false;
	static bool bSkip = false;
	static int32 CompletedRuns = 0;
	static double StartedSeconds = 0.0;
	static uint32 StepMasks[2] = {0, 0};
	static uint32 PerformanceMasks[2] = {0, 0};
	static uint32 SkippedMasks[2] = {0, 0};
}

void ADYDevEntryPlayerController::BeginPlay()
{
	Super::BeginPlay();
	if (!IsLocalPlayerController() || !IsEntryLoopWorld()) { return; }
	LoadContinueProgress();
	if (MenuWidgetClass)
	{
		MenuView = CreateWidget<UDYDevEntryWidget>(this, MenuWidgetClass);
		if (MenuView) { MenuView->AddToPlayerScreen(10000); }
	}
	ADYStageGameMode* Mode = GetWorld()->GetAuthGameMode<ADYStageGameMode>();
	if (Mode)
	{
		BoundMode = Mode;
		RegistrationHandle = Mode->OnStagePresentationChanged.AddUObject(this, &ADYDevEntryPlayerController::AttachPresentation);
		AttachPresentation(Mode->GetPlayerStagePresentation());
	}
#if !UE_BUILD_SHIPPING
	bPreviewEnding = FPlatformMisc::GetEnvironmentVariable(TEXT("DY_MENU_PANEL")).Equals(TEXT("end"), ESearchCase::IgnoreCase);
#endif
	// One next-frame refresh covers actor BeginPlay order, not a scanning/polling Tick.
	StartTheatreAmbience();
	StartPerformanceProbe();
	StartArtProbe();
	StartFlowVerification();
	ReadyRefreshHandle = GetWorld()->GetTimerManager().SetTimerForNextTick(
		FTimerDelegate::CreateWeakLambda(this, [this]() { RefreshMenu(); }));
	RefreshMenu();
	// 「重新复演」 reloads this map; instead of dropping the player back on the start plaque,
	// pick the new run up once the director is bound (a few frames after travel).
	if (DYEntryReplay::bPending)
	{
		DYEntryReplay::bPending = false;
		GetWorld()->GetTimerManager().SetTimer(AutoReplayHandle, this,
			&ADYDevEntryPlayerController::TryAutoStartAfterReplay, 0.6f, true, 0.6f);
	}
	// Review viewpoints stay available in packaged builds when the env var is set; they only
	// move the pawn and hide it, so the shipped flow is unchanged when DY_DEBUG_VIEW is absent.
	DebugViewIndex = FCString::Atoi(*FPlatformMisc::GetEnvironmentVariable(TEXT("DY_DEBUG_VIEW")));
	if (DebugViewIndex > 0)
	{
		FTimerHandle DebugViewHandle;
		GetWorld()->GetTimerManager().SetTimer(
			DebugViewHandle, this, &ADYDevEntryPlayerController::ApplyDebugReviewView, 6.f, false);
	}
}

void ADYDevEntryPlayerController::ApplyDebugReviewView()
{
	APawn* ReviewPawn = GetPawn();
	if (!ReviewPawn)
	{
		return;
	}
	struct FReviewSpot
	{
		FVector Location;
		FRotator Rotation;
	};
	static const FReviewSpot Spots[] = {
		{ FVector(-3600.f, 0.f, 190.f), FRotator::ZeroRotator },          // 1: approach the theater from outside
		{ FVector(-1500.f, 0.f, 190.f), FRotator::ZeroRotator },          // 2: entry hall looking at the stage
		{ FVector(1550.f, 0.f, 560.f), FRotator(2.f, 180.f, 0.f) },       // 3: rear seat, looking at the proscenium
		{ FVector(700.f, 0.f, 430.f), FRotator(0.f, 180.f, 0.f) },        // 4: from the stage back to the audience
		{ FVector(-3600.f, -2700.f, 700.f), FRotator(-5.f, 90.f, 0.f) },   // 5: exterior grove (left of the path)
		{ FVector(-6000.f, -3200.f, 1400.f), FRotator(-10.f, 35.f, 0.f) }, // 6: wide exterior establishing shot
		{ FVector(1650.f, 0.f, 830.f), FRotator(-4.f, 180.f, 0.f) }, // 7: behind the seats, full proscenium
		{ FVector(1500.f, -1000.f, 260.f), FRotator(3.f, 155.f, 0.f) }, // 8: side aisle toward the stage
		{ FVector(-980.f, -80.f, 250.f), FRotator(0.f, 0.f, 0.f) }, // 9: audience side of the screen (forest beat)
	};
	const int32 Index = FMath::Clamp(DebugViewIndex, 1, UE_ARRAY_COUNT(Spots)) - 1;
	ReviewPawn->SetActorLocation(Spots[Index].Location, false, nullptr, ETeleportType::TeleportPhysics);
	ReviewPawn->SetActorHiddenInGame(true);
	SetControlRotation(Spots[Index].Rotation);
	UE_LOG(LogTemp, Warning, TEXT("[MenuV2] debugview=%d loc=%s"),
		DebugViewIndex, *Spots[Index].Location.ToString());
}

void ADYDevEntryPlayerController::EndPlay(const EEndPlayReason::Type Reason)
{
	bEndingPlay = true;
	if (bPausedSession)
	{
		bPausedSession = false;
		UGameplayStatics::SetGamePaused(this, false);
	}
	if (GetWorld())
	{
		GetWorld()->GetTimerManager().ClearTimer(ReadyRefreshHandle);
		GetWorld()->GetTimerManager().ClearTimer(ReplayHandle);
		GetWorld()->GetTimerManager().ClearTimer(EntryWalkHandle);
		GetWorld()->GetTimerManager().ClearTimer(FlowVerificationHandle);
	}
	if (GEngine) { GEngine->OnTravelFailure().Remove(TravelFailureHandle); }
	TravelFailureHandle.Reset();
	if (ADYStageGameMode* Mode = BoundMode.Get()) { Mode->OnStagePresentationChanged.Remove(RegistrationHandle); }
	RegistrationHandle.Reset();
	BoundMode.Reset();
	AttachPresentation(nullptr);
	if (MenuView) { MenuView->RemoveFromParent(); MenuView = nullptr; }
	Super::EndPlay(Reason);
}

void ADYDevEntryPlayerController::AttachPresentation(ADYStagePresentation* Stage)
{
	if (ADYStagePresentation* Old = BoundStage.Get()) { Old->OnPlayerActDisplayChanged().Remove(ActHandle); }
	ActHandle.Reset();
	BoundStage.Reset();
	LastObservedPlayingActIndex = INDEX_NONE;
	if (!bEndingPlay && IsValid(Stage) && Stage->GetWorld() == GetWorld())
	{
		BoundStage = Stage;
		ActHandle = Stage->OnPlayerActDisplayChanged().AddUObject(this, &ADYDevEntryPlayerController::HandleActDisplay);
		const auto Current = Stage->GetPlayerActDisplay();
		if (Current.bSequenceEnabled && Current.Phase == EDYActSequencePhase::Playing
			&& Current.ActIndex >= 0 && Current.ActIndex < Current.ActCount)
		{
			LastObservedPlayingActIndex = Current.ActIndex; // A late attachment establishes a baseline, not a new act.
		}
	}
	RefreshMenu();
}

namespace DYContinueProgress
{
	/** Two plain ints next to the other Saved/ probes: no save-game asset, no act-level state, trivially inspectable. */
	static FString ProgressPath()
	{
		return FPaths::ProjectSavedDir() / TEXT("DYProgress.txt");
	}
	static const TCHAR* Key = TEXT("ProgressChapter=");
	static const TCHAR* MaskKey = TEXT("PlayedMask=");
	static int32 ReadInt(const FString& Text, const TCHAR* InKey)
	{
		const int32 At = Text.Find(InKey, ESearchCase::IgnoreCase);
		if (At == INDEX_NONE) { return 0; }
		return FCString::Atoi(*Text.Mid(At + FCString::Strlen(InKey)));
	}
	/** PlayedMask is stored with %02x, so it must be read back in base 16: Atoi("0f") is 0, which silently drops all four ticks. */
	static int32 ReadHex(const FString& Text, const TCHAR* InKey)
	{
		const int32 At = Text.Find(InKey, ESearchCase::IgnoreCase);
		if (At == INDEX_NONE) { return 0; }
		const FString Value = Text.Mid(At + FCString::Strlen(InKey));
		return FCString::Strtoi(*Value, nullptr, 16);
	}
}

bool ADYDevEntryPlayerController::WasChapterPlayed(const int32 ChapterIndex) const
{
	return ChapterIndex >= 0 && ChapterIndex < 8 && (PlayedChapterMask & (1 << ChapterIndex)) != 0;
}

void ADYDevEntryPlayerController::LoadContinueProgress()
{
	FString Text;
	if (FFileHelper::LoadFileToString(Text, *DYContinueProgress::ProgressPath()))
	{
		ContinueChapterIndex = FMath::Clamp(DYContinueProgress::ReadInt(Text, DYContinueProgress::Key), 0, 8);
		PlayedChapterMask = DYContinueProgress::ReadHex(Text, DYContinueProgress::MaskKey) & 0xFF;
	}
	else
	{
		ContinueChapterIndex = 0;
		PlayedChapterMask = 0;
	}
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] progress loaded chapter=%d played=0x%02x"), ContinueChapterIndex, PlayedChapterMask);
}

void ADYDevEntryPlayerController::WriteContinueProgress()
{
	const FString Text = FString::Printf(TEXT("%s%d%s%s%02x%s"),
		DYContinueProgress::Key, ContinueChapterIndex, LINE_TERMINATOR,
		DYContinueProgress::MaskKey, PlayedChapterMask, LINE_TERMINATOR);
	FFileHelper::SaveStringToFile(Text, *DYContinueProgress::ProgressPath(),
		FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] progress stored chapter=%d played=0x%02x"), ContinueChapterIndex, PlayedChapterMask);
}

void ADYDevEntryPlayerController::StoreContinueProgress(const int32 InChapterIndex)
{
	const int32 Clamped = FMath::Clamp(InChapterIndex, 0, 8);
	if (Clamped == ContinueChapterIndex) { return; }
	ContinueChapterIndex = Clamped;
	WriteContinueProgress();
}

void ADYDevEntryPlayerController::MarkChapterPlayed(const int32 ChapterIndex)
{
	const int32 Bit = 1 << FMath::Clamp(ChapterIndex, 0, 7);
	if ((PlayedChapterMask & Bit) != 0) { return; }
	PlayedChapterMask |= Bit;
	WriteContinueProgress();
}

void ADYDevEntryPlayerController::UpdateContinueProgress(const FDYActSequenceSnapshot& Snapshot)
{
	// Menu progress belongs to the theater map only; the dev labs must never write it.
	if (bEndingPlay || !IsTheaterEntryMap() || !Snapshot.bSequenceEnabled) { return; }
	if (Snapshot.Phase == EDYActSequencePhase::Complete)
	{
		// The campaign ends inside the last act, so the last act is marked here.
		MarkChapterPlayed(Snapshot.ChapterIndex);
		LastProgressChapterIndex = Snapshot.ChapterIndex;
		StoreContinueProgress(0);
		return;
	}
	if (Snapshot.Phase != EDYActSequencePhase::Inactive && Snapshot.ChapterIndex >= 0)
	{
		// Act N counts as played only once act N+1 has begun: a chapter can be picked
		// out of order from 演出篇章, so "started" is not the same as "played".
		if (LastProgressChapterIndex >= 0 && Snapshot.ChapterIndex > LastProgressChapterIndex)
		{
			MarkChapterPlayed(LastProgressChapterIndex);
		}
		LastProgressChapterIndex = Snapshot.ChapterIndex;
		StoreContinueProgress(Snapshot.ChapterIndex + 1);
	}
}
ADYPuzzleDirector* ADYDevEntryPlayerController::GetBoundDirector() const
{
	ADYStagePresentation* Stage = BoundStage.Get();
	ADYPuzzleDirector* Director = IsValid(Stage) ? Stage->GetPuzzleDirector() : nullptr;
	return IsValid(Director) && Director->GetWorld() == GetWorld() ? Director : nullptr;
}

EDYDevEntryPanel ADYDevEntryPlayerController::GetEntryPanel() const
{
	if (bEndingPlay || !IsEntryLoopWorld()) { return EDYDevEntryPanel::Hidden; }
#if !UE_BUILD_SHIPPING
	if (bPreviewEnding) { return EDYDevEntryPanel::End; }
#endif
	if (bReplayPending) { return EDYDevEntryPanel::Reloading; }
	if (bPausedSession) { return EDYDevEntryPanel::Paused; }
	ADYPuzzleDirector* Director = GetBoundDirector();
	ADYStagePresentation* Stage = BoundStage.Get();
	if (!Director || !Stage || !MenuView || !MenuView->HasReadyView()
		|| Director->IsAutoStartOnBeginPlay()) { return EDYDevEntryPanel::Waiting; }
	const FDYActSequenceSnapshot Snapshot = Stage->GetPlayerActDisplay();
	if (!Snapshot.bSequenceEnabled) { return EDYDevEntryPanel::Waiting; }
	if (Snapshot.Phase == EDYActSequencePhase::Complete) { return EDYDevEntryPanel::End; }
	if (Snapshot.Phase == EDYActSequencePhase::Inactive)
	{
		return Director->CanStartManualSequence(Stage) ? EDYDevEntryPanel::Start : EDYDevEntryPanel::Waiting;
	}
	return EDYDevEntryPanel::Hidden;
}

void ADYDevEntryPlayerController::HandleActDisplay(const FDYActSequenceSnapshot& Snapshot)
{
	UpdateContinueProgress(Snapshot);
	PlaySequenceCue(Snapshot);
	// Read the registered stage again; an earlier listener may have reset/replaced it.
	RefreshControlForActEntry();
	RefreshMenu();
}

bool ADYDevEntryPlayerController::ShouldReleaseControlForActEntry(
	const FDYActSequenceSnapshot& Current, const int32 LastPlayingActIndex)
{
	return Current.bSequenceEnabled && Current.Phase == EDYActSequencePhase::Playing
		&& Current.ActCount > 0 && Current.ActIndex >= 0 && Current.ActIndex < Current.ActCount
		&& LastPlayingActIndex >= 0 && LastPlayingActIndex < Current.ActCount
		&& Current.ActIndex > LastPlayingActIndex;
}

void ADYDevEntryPlayerController::RefreshControlForActEntry()
{
	if (bEndingPlay || bReplayPending || !IsLocalPlayerController()) { return; }
	ADYStagePresentation* Stage = BoundStage.Get();
	ADYPuzzleDirector* Director = GetBoundDirector();
	if (!IsValid(Stage) || !Director || Stage->GetWorld() != GetWorld()) { return; }
	const auto Current = Director->GetActSequenceSnapshot();
	const auto Display = Stage->GetPlayerActDisplay();
	if (!Current.bSequenceEnabled || Current.Phase != EDYActSequencePhase::Playing
		|| Current.ActIndex < 0 || Current.ActIndex >= Current.ActCount
		|| Display.bSequenceEnabled != Current.bSequenceEnabled || Display.Phase != Current.Phase
		|| Display.ActIndex != Current.ActIndex || Display.ActCount != Current.ActCount
		|| !Display.ActTitle.EqualTo(Current.ActTitle)) { return; }
	const bool bNewAct = ShouldReleaseControlForActEntry(Current, LastObservedPlayingActIndex);
	// Consume before EndActiveControl's callbacks. Reentrant synchronization/reset
	// must not release a newly acquired session twice. No state writes after that call.
	LastObservedPlayingActIndex = Current.ActIndex;
	if (!bNewAct) { return; }
	APawn* ControlledPawn = GetPawn();
	if (!IsValid(ControlledPawn) || ControlledPawn->GetWorld() != GetWorld() || ControlledPawn->GetController() != this) { return; }
	if (UDYInteractionComponent* Interaction = ControlledPawn->FindComponentByClass<UDYInteractionComponent>())
	{
		Interaction->EndActiveControl(); // Existing Pawn callback restores Explore; no reset or input remapping here.
	}
}

void ADYDevEntryPlayerController::RefreshMenu()
{
	if (bEndingPlay || !IsLocalPlayerController() || !IsEntryLoopWorld()) { return; }
	const EDYDevEntryPanel Panel = GetEntryPanel();
	if (MenuView) { MenuView->ApplyPanel(Panel); }
	const bool bNeedsMenu = Panel != EDYDevEntryPanel::Hidden;
	AHUD* ViewHUD = GetHUD();
	if (!bLoggedHud) {
		bLoggedHud = true;
		UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] hud=%s myhud=%s"), ViewHUD ? *ViewHUD->GetClass()->GetName() : TEXT("null"), MyHUD ? *MyHUD->GetClass()->GetName() : TEXT("null"));
	}
	if (ViewHUD) { ViewHUD->bShowHUD = !bNeedsMenu; }
	if (bNeedsMenu == bMenuInputApplied) { return; }
	bMenuInputApplied = bNeedsMenu;
	FlushPressedKeys();
	bShowMouseCursor = bNeedsMenu;
	if (bNeedsMenu)
	{
		FInputModeUIOnly Mode;
		Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		if (MenuView && MenuView->GetPrimaryFocusWidget())
		{
			Mode.SetWidgetToFocus(MenuView->GetPrimaryFocusWidget()->TakeWidget());
		}
		SetInputMode(Mode);
	}
	else
	{
		SetInputMode(FInputModeGameOnly());
		UWidgetBlueprintLibrary::SetFocusToGameViewport();
	}
}

bool ADYDevEntryPlayerController::RequestStartExperience()
{
	// Review hook: DY_CHAPTER=N opens campaign chapter N-1 directly. Env-gated, so a normal
	// launch (no variable) keeps the plain three-act first chapter.
	if (!bRequestInFlight)
	{
		const FString ChapterEnv = FPlatformMisc::GetEnvironmentVariable(TEXT("DY_CHAPTER"));
		if (!ChapterEnv.IsEmpty())
		{
			UE_LOG(LogDengYingShanHai, Display, TEXT("DY_CHAPTER=%s requested from the entry menu."), *ChapterEnv);
			return RequestChapterExperience(FCString::Atoi(*ChapterEnv));
		}
	}
	if (bEndingPlay || bRequestInFlight || !IsLocalPlayerController() || GetEntryPanel() != EDYDevEntryPanel::Start) { return false; }
	ADYPuzzleDirector* Director = GetBoundDirector();
	if (!Director) { return false; }
	TGuardValue<bool> RequestGuard(bRequestInFlight, true);
	const bool bStarted = Director->StartManualSequence(BoundStage.Get());
	if (bStarted) { BeginEntryWalkGuidance(); }
	if (!bEndingPlay && IsValid(this)) { RefreshMenu(); }
	return bStarted;
}

bool ADYDevEntryPlayerController::RequestChapterExperience(const int32 ChapterIndex)
{
	if (bEndingPlay || bRequestInFlight || !IsLocalPlayerController()) { return false; }
	const EDYDevEntryPanel Panel = GetEntryPanel();
	if (Panel != EDYDevEntryPanel::Start && Panel != EDYDevEntryPanel::Paused) { return false; }
	ADYPuzzleDirector* Director = GetBoundDirector();
	if (!Director || ChapterIndex < 0 || ChapterIndex >= Director->GetChapterCount()) { return false; }
	TGuardValue<bool> RequestGuard(bRequestInFlight, true);
	if (APawn* ControlledPawn = GetPawn())
	{
		if (UDYInteractionComponent* Interaction = ControlledPawn->FindComponentByClass<UDYInteractionComponent>())
		{
			Interaction->EndActiveControl();
		}
	}
	if (bPausedSession)
	{
		bPausedSession = false;
		UGameplayStatics::SetGamePaused(this, false);
	}
	const bool bStarted = Director->StartCampaignChapter(ChapterIndex, BoundStage.Get());
	if (bStarted) { BeginEntryWalkGuidance(); }
	if (!bEndingPlay && IsValid(this)) { RefreshMenu(); }
	return bStarted;
}

namespace DYEntryWalk
{
	/**
	 * Shipping swallows UE_LOG output (abslog never lands on disk for the packaged game), so entry-walk
	 * diagnosis appends one line to Saved/EntryWalkProbe.log when DY_ENTRY_PROBE=1 is set. Off by default.
	 */
	void Probe(const FString& Line)
	{
		if (!FPlatformMisc::GetEnvironmentVariable(TEXT("DY_ENTRY_PROBE")).Equals(TEXT("1"))) { return; }
		const FString Path = FPaths::ProjectSavedDir() / TEXT("EntryWalkProbe.log");
		FFileHelper::SaveStringToFile(Line + LINE_TERMINATOR, *Path,
			FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), EFileWrite::FILEWRITE_Append);
	}
}

bool ADYDevEntryPlayerController::IsTheaterEntryMap() const
{
	const UWorld* World = GetWorld();
	return World && World->GetMapName().Contains(TEXT("L_DY_Main"));
}

void ADYDevEntryPlayerController::SetPerformancePresentation(const bool bActive)
{
	bPerformancePresentationActive = bActive;
	SetEntryIntroCueVisible(!bActive && bEntryWalkSettled);
}

int32 ADYDevEntryPlayerController::SetEntryIntroCueVisible(bool bVisible)
{
	bVisible = bVisible && !bPerformancePresentationActive;
	UWorld* World = GetWorld();
	if (!World) { return 0; }
	// The act hint line is authored inside BP presentation widgets and its text is fed at runtime,
	// so there are two handles: collapse the known presentation widgets by class name (pure ASCII,
	// immune to source-encoding surprises) and, as a fallback, collapse matching text labels.
	static bool bLoggedPresentationWidgets = false;
	int32 Touched = 0;
	for (TObjectIterator<UUserWidget> It; It; ++It)
	{
		UUserWidget* Widget = *It;
		if (!IsValid(Widget) || Widget->GetWorld() != World || !Widget->WidgetTree) { continue; }
		// The native HUD owns its performance children; keep its subtitle root visible.
		if (bPerformancePresentationActive && Widget->IsA<UDYInteractionHUDWidget>()) { continue; }
		const FString WidgetClass = Widget->GetClass()->GetName();
		TArray<UWidget*> Widgets;
		Widget->WidgetTree->GetAllWidgets(Widgets);
		if (!bVisible && !bLoggedPresentationWidgets)
		{
			FString TextSample;
			int32 Samples = 0;
			for (UWidget* Child : Widgets)
			{
				if (const UTextBlock* Block = Cast<UTextBlock>(Child))
				{
					if (Samples++ < 3) { TextSample += Block->GetText().ToString().Left(24) + TEXT(" | "); }
				}
			}
			UE_LOG(LogDengYingShanHai, Log, TEXT("Entry walk widget: class=%s children=%d texts=%s"),
				*WidgetClass, Widgets.Num(), *TextSample);
		}
		const bool bPresentationWidget =
			WidgetClass.Contains(TEXT("ThreeActHUD")) || WidgetClass.Contains(TEXT("ThreeActCue"));
		if (bPresentationWidget)
		{
			Widget->SetRenderOpacity(bVisible ? 1.0f : 0.0f);
			Widget->SetVisibility(bVisible ? ESlateVisibility::SelfHitTestInvisible : ESlateVisibility::Collapsed);
			++Touched;
		}
		for (UWidget* Child : Widgets)
		{
			UTextBlock* Block = Cast<UTextBlock>(Child);
			if (!Block) { continue; }
			// V2.3 runs four acts, but the act-count wording is baked into BP presentation text.
			// Only rewrite the presentation widgets: this loop also walks the native menu widget, and a
			// blanket "三幕"->"四幕" turned the chapter list entry 「第三幕 · 刑天舞干戚」 into 「第四幕」
			// every time the player entered the hall (Run38-codex run exposed it).
			FString BlockText = Block->GetText().ToString();
			if (bPresentationWidget && BlockText.Contains(TEXT("三幕")))
			{
				BlockText = BlockText.Replace(TEXT("三幕"), TEXT("四幕"));
				Block->SetText(FText::FromString(BlockText));
			}
			// The live readability cue is 「操纵灯 用 A / D 将头部影子送入浅色缺口…」.
			// Hiding only the text block loses to the blueprint calling SetVisibility again.
			if (!BlockText.Contains(TEXT("操纵灯")) && !BlockText.Contains(TEXT("浅色缺口"))) { continue; }
			Widget->SetRenderOpacity(bVisible ? 1.0f : 0.0f);
			Widget->SetVisibility(bVisible ? ESlateVisibility::SelfHitTestInvisible : ESlateVisibility::Collapsed);
			Block->SetVisibility(bVisible ? ESlateVisibility::SelfHitTestInvisible : ESlateVisibility::Collapsed);
			++Touched;
		}
	}
	if (!bVisible) { bLoggedPresentationWidgets = true; }
	return Touched;
}

void ADYDevEntryPlayerController::EnsureEntryWalkHint()
{
	if (bEntryWalkSettled) { return; }
	// The exterior cue must survive widget construction order: the presentation HUD can be
	// created after BeginPlay, and in that window ShowHint would silently drop the text.
	const double Now = FPlatformTime::Seconds();
	if (bEntryHintIssued && Now - LastEntryHintSeconds < 2.0) { return; }
	// The presentation HUD may be a Blueprint wrapper that owns the widget directly, so the
	// controller cannot assume ADYInteractionHUD; talk to the live widget instances instead.
	ADYInteractionHUD* EntryHud = Cast<ADYInteractionHUD>(GetHUD());
	UDYInteractionHUDWidget* DirectView = EntryHud ? EntryHud->GetView() : nullptr;
	if (DirectView == nullptr)
	{
		for (TObjectIterator<UDYInteractionHUDWidget> It; It; ++It)
		{
			UDYInteractionHUDWidget* Candidate = *It;
			if (!IsValid(Candidate) || Candidate->GetWorld() != GetWorld()) { continue; }
			DirectView = Candidate;
			break;
		}
	}
	int32 WidgetCount = 0;
	for (TObjectIterator<UDYInteractionHUDWidget> It; It; ++It) { if (IsValid(*It)) { ++WidgetCount; } }
	UE_LOG(LogDengYingShanHai, Log, TEXT("Entry walk: widgets=%d hud=%d direct=%d"), WidgetCount,
		Cast<ADYInteractionHUD>(GetHUD()) ? 1 : 0, DirectView ? 1 : 0);
	DYEntryWalk::Probe(FString::Printf(TEXT("EnsureEntryWalkHint widgets=%d hud=%d direct=%d issued=%d"),
		WidgetCount, Cast<ADYInteractionHUD>(GetHUD()) ? 1 : 0, DirectView ? 1 : 0, bEntryHintIssued ? 1 : 0));
	if (DirectView == nullptr) { return; }
	bEntryHintIssued = true;
	LastEntryHintSeconds = Now;
	const FText WalkHint = UDYInteractionHUDWidget::GetEntryWalkHint();
	if (EntryHud) { EntryHud->SetEntryWalkGuide(true, WalkHint); }
	else { DirectView->SetEntryWalkGuide(true, WalkHint); }
	UE_LOG(LogDengYingShanHai, Log, TEXT("Entry walk: hint issued through %s"), *DirectView->GetClass()->GetName());
}

void ADYDevEntryPlayerController::BeginEntryWalkGuidance()
{
	UWorld* World = GetWorld();
	if (bEndingPlay || !World || !IsTheaterEntryMap() || !IsLocalPlayerController()) { return; }
	APawn* ControlledPawn = GetPawn();
	const bool bAlreadyInside = ControlledPawn && ControlledPawn->GetActorLocation().X > DYEntryWalk::TheaterThresholdX;
	bEntryWalkSettled = bAlreadyInside;
	if (bAlreadyInside)
	{
		// A chapter picked from pause is already on stage. Show that chapter, don't replay the door hint.
		SetEntryIntroCueVisible(true);
		if (ADYInteractionHUD* Hud = Cast<ADYInteractionHUD>(GetHUD()))
		{
			Hud->SetEntryWalkGuide(false, FText::GetEmpty());
			Hud->SetStageHudVisible(true);
		}
		return;
	}
	EnsureEntryWalkHint();
	const int32 HiddenCues = SetEntryIntroCueVisible(false);
	UE_LOG(LogDengYingShanHai, Log, TEXT("Entry walk: stage cue labels hidden=%d"), HiddenCues);
	World->GetTimerManager().SetTimer(EntryWalkHandle, this, &ADYDevEntryPlayerController::HandleEntryWalkCheck, 0.25f, true);
	HandleEntryWalkCheck();
}

void ADYDevEntryPlayerController::HandleEntryWalkCheck()
{
	APawn* ControlledPawn = GetPawn();
	UWorld* World = GetWorld();
	if (bEndingPlay || !ControlledPawn || !World)
	{
		if (World) { World->GetTimerManager().ClearTimer(EntryWalkHandle); }
		return;
	}
	if (bEntryWalkSettled)
	{
		World->GetTimerManager().ClearTimer(EntryWalkHandle);
		return;
	}
	if (ControlledPawn->GetActorLocation().X <= DYEntryWalk::TheaterThresholdX)
	{
		SetEntryIntroCueVisible(false); // the presentation widget may rebuild its text while walking
		EnsureEntryWalkHint();
		return;
	}
	bEntryWalkSettled = true;
	SetEntryIntroCueVisible(true);
	World->GetTimerManager().ClearTimer(EntryWalkHandle);
	if (ADYInteractionHUD* Hud = Cast<ADYInteractionHUD>(GetHUD()))
	{
		Hud->SetEntryWalkGuide(false, FText::GetEmpty());
		// The arrival cue used to be pushed as a transient hint, but the presentation HUD owns a
		// second widget instance, so the player read two stacked plaques at the doorway (Run65
		// walk capture). The stage prompt already says what to do next: one plaque is enough.
		Hud->SetStageHudVisible(true);
	}
	UE_LOG(LogDengYingShanHai, Log, TEXT("Entry walk: player crossed into the theater at %s"),
		*ControlledPawn->GetActorLocation().ToCompactString());
}

bool ADYDevEntryPlayerController::RequestReplayExperience()
{
	if (bEndingPlay || bRequestInFlight || !IsLocalPlayerController() || GetEntryPanel() != EDYDevEntryPanel::End) { return false; }
	bReplayPending = true; // Consume once before EndControl's callbacks or any deferred travel.
	TGuardValue<bool> RequestGuard(bRequestInFlight, true);
	if (APawn* ControlledPawn = GetPawn())
	{
		if (UDYInteractionComponent* Interaction = ControlledPawn->FindComponentByClass<UDYInteractionComponent>()) { Interaction->EndActiveControl(); }
	}
	if (bEndingPlay || !IsValid(this) || !GetWorld()) { return false; }
	RefreshMenu();
	ReplayHandle = GetWorld()->GetTimerManager().SetTimerForNextTick(
		FTimerDelegate::CreateWeakLambda(this, [this]() { PerformReplay(); }));
	return true;
}

void ADYDevEntryPlayerController::PerformReplay()
{
	const FName ReplayMap = GetCurrentDevEntryMap();
	if (bEndingPlay || !bReplayPending || ReplayMap.IsNone()) { return; }
	if (GEngine)
	{
		TravelFailureHandle = GEngine->OnTravelFailure().AddUObject(this, &ADYDevEntryPlayerController::HandleTravelFailure);
	}
	DYEntryReplay::bPending = true;
	UGameplayStatics::OpenLevel(this, ReplayMap, true);
}

void ADYDevEntryPlayerController::TryAutoStartAfterReplay()
{
	UWorld* World = GetWorld();
	if (!World) { return; }
	if (++AutoReplayAttempts > 12)
	{
		World->GetTimerManager().ClearTimer(AutoReplayHandle);
		UE_LOG(LogDengYingShanHai, Warning, TEXT("Replay: auto start gave up after 12 attempts."));
		return;
	}
	if (bEndingPlay || bRequestInFlight || GetEntryPanel() != EDYDevEntryPanel::Start) { return; }
	if (!GetBoundDirector()) { return; }
	if (RequestStartExperience())
	{
		World->GetTimerManager().ClearTimer(AutoReplayHandle);
		UE_LOG(LogDengYingShanHai, Log, TEXT("Replay: new run started automatically after map reload."));
	}
}

void ADYDevEntryPlayerController::HandleTravelFailure(UWorld* World, ETravelFailure::Type Failure, const FString& Error)
{
	if (bEndingPlay || !bReplayPending || World != GetWorld()) { return; }
	if (GEngine) { GEngine->OnTravelFailure().Remove(TravelFailureHandle); }
	TravelFailureHandle.Reset();
	bReplayPending = false;
	UE_LOG(LogDengYingShanHai, Error, TEXT("Dev same-map replay failed; existing finale retained: %s"), *Error);
	RefreshMenu();
}

void ADYDevEntryPlayerController::RequestQuitExperience()
{
	if (!bEndingPlay && IsLocalPlayerController() && IsEntryLoopWorld())
	{
		UKismetSystemLibrary::QuitGame(this, this, EQuitPreference::Quit, false);
	}
}

void ADYDevEntryPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
	if (InputComponent)
	{
		InputComponent->BindKey(EKeys::Escape, IE_Pressed, this, &ADYDevEntryPlayerController::HandleEscape);
		// The chapter show is skippable from any state; Ship builds keep this binding.
		InputComponent->BindKey(EKeys::SpaceBar, IE_Pressed, this, &ADYDevEntryPlayerController::HandleSkipPerformance);
#if !UE_BUILD_SHIPPING
		// PageUp / PageDown cycle the dev viewpoints; the F-row is reserved by the engine for view modes.
		FInputKeyBinding NextView(EKeys::PageDown, IE_Pressed);
		NextView.KeyDelegate.GetDelegateForManualSet().BindLambda([this]()
		{
			DebugViewIndex = DebugViewIndex % 8 + 1;
			ApplyDebugReviewView();
		});
		InputComponent->KeyBindings.Add(NextView);
		FInputKeyBinding PrevView(EKeys::PageUp, IE_Pressed);
		PrevView.KeyDelegate.GetDelegateForManualSet().BindLambda([this]()
		{
			DebugViewIndex = (DebugViewIndex + 6) % 8 + 1;
			ApplyDebugReviewView();
		});
		InputComponent->KeyBindings.Add(PrevView);
#endif
	}
}

bool ADYDevEntryPlayerController::RequestPauseExperience()
{
	if (bEndingPlay || bPausedSession || !IsLocalPlayerController() || !IsEntryLoopWorld()) { return false; }
	ADYStagePresentation* Stage = BoundStage.Get();
	if (!IsValid(Stage) || Stage->GetWorld() != GetWorld()) { return false; }
	const FDYActSequenceSnapshot Snapshot = Stage->GetPlayerActDisplay();
	if (!Snapshot.bSequenceEnabled || Snapshot.Phase != EDYActSequencePhase::Playing) { return false; }
	bPausedSession = true;
	UGameplayStatics::SetGamePaused(this, true);
	RefreshMenu();
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] pause act=%d"), Snapshot.ActIndex);
	return true;
}

bool ADYDevEntryPlayerController::RequestContinueExperience()
{
	if (!bPausedSession) { return false; }
	bPausedSession = false;
	UGameplayStatics::SetGamePaused(this, false);
	RefreshMenu();
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] continue"));
	return true;
}

void ADYDevEntryPlayerController::HandleSkipPerformance()
{
	if (UDYPuppetPerformanceComponent::SkipAnyPerformanceInWorld(GetWorld()))
	{
		UE_LOG(LogDengYingShanHai, Display, TEXT("[PuppetPerformance] skipped by player."));
	}
}

void ADYDevEntryPlayerController::HandleEscape()
{
	UE_LOG(LogDengYingShanHai, Warning, TEXT("[MenuV2] esc panel=%d paused=%d"), static_cast<int32>(GetEntryPanel()), bPausedSession ? 1 : 0);
	const double Now = FPlatformTime::Seconds();
	if (Now - LastEscapeSeconds < 0.35) { return; }
	LastEscapeSeconds = Now;
	if (bEndingPlay) { return; }
	if (bPausedSession) { RequestContinueExperience(); return; }
	if (GetEntryPanel() == EDYDevEntryPanel::Hidden) { RequestPauseExperience(); }
}

bool ADYDevEntryPlayerController::FlowVerificationHasCompleteEvidence(
	const uint32 StepMask, const uint32 PerformanceMask, const bool bWalkedInside)
{
	return StepMask == 0xFFF && PerformanceMask == 0xF && bWalkedInside;
}

void ADYDevEntryPlayerController::WriteFlowVerificationProbe(const FString& Event) const
{
	if (!bFlowVerificationEnabled) { return; }
	IFileManager::Get().MakeDirectory(*FPaths::ProjectSavedDir(), true);
	const FString Line = FString::Printf(TEXT("elapsed=%.3f run=%d %s\n"),
		FPlatformTime::Seconds() - DYFlowVerification::StartedSeconds,
		FMath::Min(DYFlowVerification::CompletedRuns + 1, 2), *Event);
	FFileHelper::SaveStringToFile(Line, *(FPaths::ProjectSavedDir() / TEXT("FlowVerifyProbe.log")),
		FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), EFileWrite::FILEWRITE_Append);
}

void ADYDevEntryPlayerController::StartFlowVerification()
{
	const FString Mode = FPlatformMisc::GetEnvironmentVariable(TEXT("DY_FLOW_VERIFY"));
	if (Mode != TEXT("1") && Mode != TEXT("full") && Mode != TEXT("skip")) { return; }
	if (!IsLocalPlayerController() || !GetWorld() || !IsTheaterEntryMap()) { return; }
	bFlowVerificationEnabled = true;
	if (!DYFlowVerification::bInitialized)
	{
		DYFlowVerification::bInitialized = true;
		DYFlowVerification::bSkip = Mode == TEXT("skip");
		DYFlowVerification::StartedSeconds = FPlatformTime::Seconds();
	}
	WriteFlowVerificationProbe(FString::Printf(TEXT("world-begin mode=%s saved=%s"), *Mode,
		*FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir())));
	if (!FPlatformMisc::GetEnvironmentVariable(TEXT("DY_CAMPAIGN_AUTOPLAY")).Equals(TEXT("1")))
	{
		FinishFlowVerification(false, TEXT("autoplay-not-explicitly-enabled"));
		return;
	}
	GetWorld()->GetTimerManager().SetTimer(FlowVerificationHandle, this,
		&ADYDevEntryPlayerController::TickFlowVerification, 0.2f, true, 0.5f);
}

void ADYDevEntryPlayerController::PlayerTick(const float DeltaSeconds)
{
	Super::PlayerTick(DeltaSeconds);
	if (!bFlowVerificationEnabled || !bFlowVerificationStarted || DYFlowVerification::bFinished
		|| bReplayPending || bEndingPlay || bFlowVerificationWalkedInside) { return; }
	if (APawn* ControlledPawn = GetPawn())
	{
		if (ControlledPawn->GetActorLocation().X <= DYEntryWalk::TheaterThresholdX + 60.0)
		{
			// Same collision-aware pawn input as exploration; no transform or POV writes.
			ControlledPawn->AddMovementInput(FVector::ForwardVector, 1.0f);
		}
		else
		{
			bFlowVerificationWalkedInside = true;
			WriteFlowVerificationProbe(FString::Printf(TEXT("walk-crossed location=%s"),
				*ControlledPawn->GetActorLocation().ToCompactString()));
		}
	}
}

void ADYDevEntryPlayerController::TickFlowVerification()
{
	if (!bFlowVerificationEnabled || DYFlowVerification::bFinished || bEndingPlay || bReplayPending) { return; }
	if (FPlatformTime::Seconds() - DYFlowVerification::StartedSeconds > 600.0)
	{
		FinishFlowVerification(false, TEXT("timeout-600s"));
		return;
	}
	ADYPuzzleDirector* Director = GetBoundDirector();
	if (!Director) { return; }
	const EDYDevEntryPanel Panel = GetEntryPanel();
	if (Panel == EDYDevEntryPanel::Start)
	{
		if (RequestStartExperience())
		{
			bFlowVerificationStarted = true;
			WriteFlowVerificationProbe(TEXT("start-request-accepted"));
		}
		return;
	}
	const FDYActSequenceSnapshot Snapshot = Director->GetActSequenceSnapshot();
	const int32 RunIndex = FMath::Clamp(DYFlowVerification::CompletedRuns, 0, 1);
	if (Snapshot.Phase == EDYActSequencePhase::Playing)
	{
		bFlowVerificationStarted = true; // Includes the controller's normal post-replay auto-start.
		if (Snapshot.ChapterIndex >= 0 && Snapshot.ChapterIndex < 4 && Snapshot.ActIndex >= 0 && Snapshot.ActIndex < 3)
		{
			DYFlowVerification::StepMasks[RunIndex] |= 1u << (Snapshot.ChapterIndex * 3 + Snapshot.ActIndex);
		}
	}
	ADYPuppetActor* Puppet = Director->GetPuppetActor();
	UDYPuppetPerformanceComponent* Performance = Puppet ? Puppet->GetPerformanceComponent() : nullptr;
	USkeletalMeshComponent* Mesh = Puppet ? Puppet->GetActivePuppetMesh() : nullptr;
	UAnimSingleNodeInstance* Instance = Mesh ? Mesh->GetSingleNodeInstance() : nullptr;
	UAnimationAsset* Clip = Instance ? Instance->GetCurrentAsset() : nullptr;
	const bool bPerforming = Performance && Performance->IsPerforming();
	const FString State = FString::Printf(TEXT("phase=%d chapter=%d step=%d panel=%d show=%d mesh=%s mode=%d instance=%s clip=%s"),
		static_cast<int32>(Snapshot.Phase), Snapshot.ChapterIndex, Snapshot.ActIndex,
		static_cast<int32>(Panel), bPerforming ? 1 : 0, *GetNameSafe(Mesh),
		Mesh ? static_cast<int32>(Mesh->GetAnimationMode()) : -1, *GetNameSafe(Instance), *GetNameSafe(Clip));
	if (State != LastFlowVerificationState)
	{
		LastFlowVerificationState = State;
		WriteFlowVerificationProbe(State + FString::Printf(TEXT(" position=%.3f"), Mesh && Instance ? Mesh->GetPosition() : -1.f));
	}
	if (bPerforming)
	{
		if (!Instance || !Clip || Mesh->GetAnimationMode() != EAnimationMode::AnimationSingleNode
			|| !Clip->GetName().Contains(TEXT("_Perf_")))
		{
			FinishFlowVerification(false, TEXT("show-missing-live-single-node-perf-clip"));
			return;
		}
		const int32 Chapter = Performance->GetPerformingChapter();
		if (Chapter >= 0 && Chapter < 4)
		{
			DYFlowVerification::PerformanceMasks[RunIndex] |= 1u << Chapter;
			if (FlowVerificationShowStarted <= 0.0) { FlowVerificationShowStarted = FPlatformTime::Seconds(); }
			if (DYFlowVerification::bSkip && !(DYFlowVerification::SkippedMasks[RunIndex] & (1u << Chapter))
				&& FPlatformTime::Seconds() - FlowVerificationShowStarted >= 1.0)
			{
				DYFlowVerification::SkippedMasks[RunIndex] |= 1u << Chapter;
				WriteFlowVerificationProbe(FString::Printf(TEXT("skip-request chapter=%d"), Chapter));
				Performance->SkipPerformance();
			}
		}
	}
	else { FlowVerificationShowStarted = 0.0; }
	if (Panel != EDYDevEntryPanel::End) { return; }
	WriteFlowVerificationProbe(FString::Printf(TEXT("end-panel steps=%u performances=%u walked=%d"),
		DYFlowVerification::StepMasks[RunIndex], DYFlowVerification::PerformanceMasks[RunIndex], bFlowVerificationWalkedInside ? 1 : 0));
	if (!FlowVerificationHasCompleteEvidence(DYFlowVerification::StepMasks[RunIndex],
		DYFlowVerification::PerformanceMasks[RunIndex], bFlowVerificationWalkedInside)
		|| (DYFlowVerification::bSkip && DYFlowVerification::SkippedMasks[RunIndex] != 0xF))
	{
		FinishFlowVerification(false, TEXT("incomplete-four-chapter-evidence"));
		return;
	}
	if (DYFlowVerification::CompletedRuns == 0)
	{
		if (!RequestReplayExperience()) { FinishFlowVerification(false, TEXT("replay-request-rejected")); return; }
		WriteFlowVerificationProbe(TEXT("replay-request-accepted"));
		++DYFlowVerification::CompletedRuns;
		return;
	}
	++DYFlowVerification::CompletedRuns;
	FinishFlowVerification(true, TEXT("two-complete-four-chapter-runs-and-real-replay"));
}

void ADYDevEntryPlayerController::FinishFlowVerification(const bool bSuccess, const TCHAR* Reason)
{
	if (!bFlowVerificationEnabled || DYFlowVerification::bFinished) { return; }
	DYFlowVerification::bFinished = true;
	WriteFlowVerificationProbe(FString::Printf(TEXT("result=%s reason=%s completed-runs=%d"),
		bSuccess ? TEXT("PASS") : TEXT("FAIL"), Reason, DYFlowVerification::CompletedRuns));
	const FString Json = FString::Printf(TEXT("{\"Succeeded\":%s,\"Mode\":\"%s\",\"Reason\":\"%s\",\"CompletedRuns\":%d,\"StepMasks\":[%u,%u],\"PerformanceMasks\":[%u,%u],\"SkippedMasks\":[%u,%u],\"ForcedTermination\":false,\"HumanVisualAcceptance\":false}\n"),
		bSuccess ? TEXT("true") : TEXT("false"), DYFlowVerification::bSkip ? TEXT("skip") : TEXT("full"), Reason,
		DYFlowVerification::CompletedRuns, DYFlowVerification::StepMasks[0], DYFlowVerification::StepMasks[1],
		DYFlowVerification::PerformanceMasks[0], DYFlowVerification::PerformanceMasks[1],
		DYFlowVerification::SkippedMasks[0], DYFlowVerification::SkippedMasks[1]);
	FFileHelper::SaveStringToFile(Json, *(FPaths::ProjectSavedDir() / TEXT("FlowVerifyResult.json")),
		FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
	// Let the existing CSV profiler finalize before using the same quit action as the menu.
	ConsoleCommand(TEXT("csvprofile stop"), false);
	GetWorld()->GetTimerManager().ClearTimer(FlowVerificationHandle);
	GetWorld()->GetTimerManager().SetTimer(FlowVerificationHandle,
		FTimerDelegate::CreateWeakLambda(this, [this]()
		{
			WriteFlowVerificationProbe(TEXT("normal-quit-request"));
			RequestQuitExperience();
		}), 3.0f, false);
}
