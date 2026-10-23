#include "Stage/DYStageEnvironment.h"

#include "Components/AudioComponent.h"
#include "Components/LocalLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "CollisionQueryParams.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Sound/SoundBase.h"
#include "TimerManager.h"

namespace DYStageEnvironmentVisuals
{
	constexpr float DormantIntensityLumens = 0.0f;
	constexpr float SunAwakenedIntensityLumens = 5000.0f;
	constexpr float ChaseSunAccentIntensityLumens = 3500.0f;
	constexpr float ChaseWingAccentIntensityLumens = 4500.0f;
}

ADYStageEnvironment::ADYStageEnvironment()
{
	PrimaryActorTick.bCanEverTick = false;
	PrimaryActorTick.bStartWithTickEnabled = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);

	SunAwakenedAccent = CreateDefaultSubobject<UPointLightComponent>(TEXT("SunAwakenedAccent"));
	SunAwakenedAccent->SetupAttachment(SceneRoot);
	SunAwakenedAccent->SetMobility(EComponentMobility::Movable);
	SunAwakenedAccent->SetIntensityUnits(ELightUnits::Lumens);
	SunAwakenedAccent->SetIntensity(DYStageEnvironmentVisuals::DormantIntensityLumens);
	SunAwakenedAccent->SetAttenuationRadius(750.0f);
	SunAwakenedAccent->SetSourceRadius(18.0f);
	SunAwakenedAccent->SetCastShadows(false);
	SunAwakenedAccent->SetLightColor(FLinearColor(1.0f, 0.32f, 0.06f));

	ChaseAwakenedAccent = CreateDefaultSubobject<UPointLightComponent>(TEXT("ChaseAwakenedAccent"));
	ChaseAwakenedAccent->SetupAttachment(SceneRoot);
	ChaseAwakenedAccent->SetRelativeLocation(FVector(0.0, -320.0, -40.0));
	ChaseAwakenedAccent->SetMobility(EComponentMobility::Movable);
	ChaseAwakenedAccent->SetIntensityUnits(ELightUnits::Lumens);
	ChaseAwakenedAccent->SetIntensity(DYStageEnvironmentVisuals::DormantIntensityLumens);
	ChaseAwakenedAccent->SetAttenuationRadius(1050.0f);
	ChaseAwakenedAccent->SetSourceRadius(24.0f);
	ChaseAwakenedAccent->SetCastShadows(false);
	ChaseAwakenedAccent->SetLightColor(FLinearColor(1.0f, 0.18f, 0.025f));

	ExteriorWindSound = TSoftObjectPtr<USoundBase>(FSoftObjectPath(TEXT("/Game/DengYingShanHai/Dev/Audio/Sounds/SFX_DevWind.SFX_DevWind")));
	ExteriorLeavesSound = TSoftObjectPtr<USoundBase>(FSoftObjectPath(TEXT("/Game/DengYingShanHai/Dev/Audio/Sounds/SFX_DevForestLeaves.SFX_DevForestLeaves")));
}

namespace
{
	void LayReadableEntry(AActor* Owner)
	{
		UWorld* World = Owner ? Owner->GetWorld() : nullptr;
		if (!World || !World->GetOutermost()->GetName().Contains(TEXT("L_DY_Main"))) { return; }

		UStaticMesh* SlabMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
		UMaterialInterface* StoneBase = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/DengYingShanHai/Dev/ArtPolish_20261022/Materials/MI_DY_StonePathTex.MI_DY_StonePathTex"));
		if (SlabMesh && Owner->GetRootComponent())
		{
			// One long plane cut through the hills and showed up as a white edge.
			// Each pad sits on the ground trace instead.
			// The pads used to be flat BasicShapeMaterial planes: untextured cream rectangles that read as
			// placeholder geometry in every composition. They are now warm sandstone inlay stones that use
			// the same world-aligned stone material as the path, only tinted lighter so the 灯径 stays legible.
			FRandomStream InlayJitter(20261022);
			FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(DYEntryPath), false, Owner);
			for (int32 Step = 0; Step < 8; ++Step)
			{
				const float X = -4500.f + Step * 320.f;
				FHitResult Hit;
				if (!World->LineTraceSingleByChannel(Hit, FVector(X, -210.f, 400.f), FVector(X, -210.f, -400.f), ECC_Visibility, QueryParams))
				{
					continue;
				}
				UStaticMeshComponent* Slab = NewObject<UStaticMeshComponent>(Owner);
				Slab->SetStaticMesh(SlabMesh);
				if (StoneBase)
				{
					UMaterialInstanceDynamic* SlabMat = UMaterialInstanceDynamic::Create(StoneBase, Owner);
					if (SlabMat)
					{
						SlabMat->SetVectorParameterValue(TEXT("Tint"), FLinearColor(1.46f, 1.34f, 1.12f));
						SlabMat->SetScalarParameterValue(TEXT("Roughness"), 0.94f);
						SlabMat->SetScalarParameterValue(TEXT("Specular"), 0.02f);
						Slab->SetMaterial(0, SlabMat);
					}
					else
					{
						Slab->SetMaterial(0, StoneBase);
					}
				}
				Slab->SetCollisionEnabled(ECollisionEnabled::NoCollision);
				Slab->SetCastShadow(false);
				Slab->SetupAttachment(Owner->GetRootComponent());
				Slab->RegisterComponent();
				// Flush-ish inlay: only a couple of centimetres proud of the paving so the side faces do not
				// read as a dark picture frame around every stone.
				const float SlabWidth = 2.24f + InlayJitter.FRandRange(0.f, 0.12f);
				const float SlabLength = 1.14f + InlayJitter.FRandRange(0.f, 0.05f);
				Slab->SetWorldLocation(Hit.ImpactPoint + FVector(0.f, 0.f, 1.1f));
				Slab->SetWorldScale3D(FVector(SlabWidth, SlabLength, 0.02f));
			}
		}

		for (TActorIterator<AActor> It(World); It; ++It)
		{
			TInlineComponentArray<ULocalLightComponent*> Lights;
			It->GetComponents(Lights);
			for (ULocalLightComponent* Light : Lights)
			{
				if (!Light) { continue; }
				const FLinearColor Color = Light->GetLightColor();
				const bool bWhite = Color.R > 0.9f && Color.G > 0.9f && Color.B > 0.9f;
				if (bWhite && Light->Intensity > 12000.f && Light->GetComponentLocation().X < -1000.f)
				{
					Light->SetIntensity(4000.f);
					Light->SetLightColor(FLinearColor(1.f, 0.82f, 0.55f));
				}
			}
		}
	}
}

void ADYStageEnvironment::BeginPlay()
{
	Super::BeginPlay();
	ApplyVisualState();
	LayReadableEntry(this);
}

void ADYStageEnvironment::ApplyState(const EDYStageEnvironmentState NewState)
{
	UE_LOG(LogTemp, Warning, TEXT("[DYExterior] apply state new=%d cur=%d"), static_cast<int32>(NewState), static_cast<int32>(CurrentState));
	if (static_cast<uint8>(NewState) > static_cast<uint8>(EDYStageEnvironmentState::ForestComplete)) { return; }
	if (CurrentState == NewState)
	{
		ApplyVisualState();
		return;
	}

	const EDYStageEnvironmentState PreviousState = CurrentState;
	CurrentState = NewState;
	ApplyVisualState();
	OnStateChanged.Broadcast(PreviousState, CurrentState);

	// 杖落成林: the world outside the theater answers the performance. Presentation-only reaction.
	if (CurrentState == EDYStageEnvironmentState::ForestComplete && PreviousState != EDYStageEnvironmentState::ForestComplete)
	{
		TriggerExteriorGreening();
	}
	else if (CurrentState == EDYStageEnvironmentState::Dormant && PreviousState != EDYStageEnvironmentState::Dormant)
	{
		ResetExteriorGreening();
	}
}

void ADYStageEnvironment::ResetToDormant()
{
	ApplyState(EDYStageEnvironmentState::Dormant);
}

void ADYStageEnvironment::TriggerExteriorGreening()
{
	UWorld* World = GetWorld();
	if (!World || ExteriorTreeTag.IsNone())
	{
		return;
	}

	if (bExteriorGreeningDone && ExteriorCanopyMaterials.Num() > 0)
	{
		for (UMaterialInstanceDynamic* const Dynamic : ExteriorCanopyMaterials)
		{
			if (Dynamic)
			{
				Dynamic->SetVectorParameterValue(TEXT("BaseColor"), ExteriorAliveTint);
			}
		}
		SpawnExteriorAmbience();
		return;
	}

	if (ExteriorCanopyMaterials.Num() == 0)
	{
		for (TActorIterator<AStaticMeshActor> It(World); It; ++It)
		{
			AStaticMeshActor* MeshActor = *It;
			if (!MeshActor || !MeshActor->ActorHasTag(ExteriorTreeTag) || !MeshActor->ActorHasTag(ExteriorCanopyTag))
			{
				continue;
			}
			UStaticMeshComponent* MeshComponent = MeshActor->GetStaticMeshComponent();
			if (!MeshComponent || MeshComponent->GetNumMaterials() == 0)
			{
				continue;
			}
			if (UMaterialInstanceDynamic* const Dynamic = MeshComponent->CreateAndSetMaterialInstanceDynamic(0))
			{
				Dynamic->SetVectorParameterValue(TEXT("BaseColor"), ExteriorDeadTint);
				ExteriorCanopyMaterials.Add(Dynamic);
				UE_LOG(LogTemp, Log, TEXT("[DYExterior] canopy %s loc=%s prev=%s"),
					*MeshActor->GetName(), *MeshActor->GetActorLocation().ToCompactString(),
					*GetNameSafe(MeshComponent->GetMaterial(0)));
			}
		}
	}

	ExteriorGreeningStartSeconds = FPlatformTime::Seconds();
	if (ExteriorCanopyMaterials.Num() > 0)
	{
		bExteriorGreeningActive = true;
		// Actor tick may be disabled on Blueprint subclasses; drive the fade from the world timer instead.
		GetWorldTimerManager().SetTimer(ExteriorGreeningHandle, this, &ADYStageEnvironment::AdvanceExteriorGreening, 0.05f, true);
		UE_LOG(LogTemp, Log, TEXT("[DYExterior] greening %d canopies over %.1fs"), ExteriorCanopyMaterials.Num(), ExteriorGreeningSeconds);
	}

	SpawnExteriorAmbience();
}

void ADYStageEnvironment::ResetExteriorGreening()
{
	UE_LOG(LogTemp, Log, TEXT("[DYExterior] reset called state=%d"), static_cast<int32>(CurrentState));
	bExteriorGreeningDone = false;
	bExteriorGreeningActive = false;
	bExteriorGreeningActive = false;
	GetWorldTimerManager().ClearTimer(ExteriorGreeningHandle);
	for (UMaterialInstanceDynamic* const Dynamic : ExteriorCanopyMaterials)
	{
		if (Dynamic)
		{
			Dynamic->SetVectorParameterValue(TEXT("BaseColor"), ExteriorDeadTint);
		}
	}
	if (ExteriorAmbienceComponent && ExteriorAmbienceComponent->IsPlaying())
	{
		ExteriorAmbienceComponent->FadeOut(1.5f, 0.0f);
	}
}

void ADYStageEnvironment::SpawnExteriorAmbience()
{
	if (ExteriorAmbienceComponent && ExteriorAmbienceComponent->IsPlaying())
	{
		return;
	}
	USoundBase* const Wind = ExteriorWindSound.LoadSynchronous();
	if (!Wind)
	{
		return;
	}
	ExteriorAmbienceComponent = UGameplayStatics::SpawnSound2D(this, Wind, 0.7f, 1.0f, 0.15f, nullptr, true);
	if (!ExteriorAmbienceComponent)
	{
		return;
	}
	ExteriorAmbienceComponent->FadeIn(3.0f, 0.7f);

	if (USoundBase* const Leaves = ExteriorLeavesSound.LoadSynchronous())
	{
		if (UAudioComponent* const Birds = UGameplayStatics::SpawnSound2D(this, Leaves, 0.35f, 1.18f, 0.5f, nullptr, true))
		{
			Birds->FadeIn(4.0f, 0.35f);
		}
	}
}

void ADYStageEnvironment::AdvanceExteriorGreening()
{
	if (!bExteriorGreeningActive)
	{
		GetWorldTimerManager().ClearTimer(ExteriorGreeningHandle);
		return;
	}

	const double Elapsed = FPlatformTime::Seconds() - ExteriorGreeningStartSeconds;
	const float Alpha = FMath::Clamp(static_cast<float>(Elapsed) / FMath::Max(ExteriorGreeningSeconds, 0.05f), 0.0f, 1.0f);
	const FLinearColor Tint = FMath::Lerp(ExteriorDeadTint, ExteriorAliveTint, Alpha);
	for (UMaterialInstanceDynamic* const Dynamic : ExteriorCanopyMaterials)
	{
		if (Dynamic)
		{
			Dynamic->SetVectorParameterValue(TEXT("BaseColor"), Tint);
		}
	}

	if (Alpha >= 1.0f)
	{
		bExteriorGreeningActive = false;
		bExteriorGreeningDone = true;
		GetWorldTimerManager().ClearTimer(ExteriorGreeningHandle);
		UE_LOG(LogTemp, Log, TEXT("[DYExterior] greening complete tint=(%.2f,%.2f,%.2f) mids=%d"), Tint.R, Tint.G, Tint.B, ExteriorCanopyMaterials.Num());
		for (UMaterialInstanceDynamic* const Dynamic : ExteriorCanopyMaterials)
		{
			FLinearColor Read;
			if (Dynamic && Dynamic->GetVectorParameterValue(FMaterialParameterInfo(TEXT("BaseColor")), Read))
			{
				UE_LOG(LogTemp, Warning, TEXT("[DYExterior] mid=%s parent=%s read=(%.2f,%.2f,%.2f)"), *Dynamic->GetName(), *GetNameSafe(Dynamic->Parent), Read.R, Read.G, Read.B);
				break;
			}
		}
	}
}

void ADYStageEnvironment::ApplyVisualState()
{
	float SunAccentIntensity = DYStageEnvironmentVisuals::DormantIntensityLumens;
	float ChaseAccentIntensity = DYStageEnvironmentVisuals::DormantIntensityLumens;
	if (CurrentState == EDYStageEnvironmentState::SunAwakened)
	{
		SunAccentIntensity = DYStageEnvironmentVisuals::SunAwakenedIntensityLumens;
	}
	else if (CurrentState == EDYStageEnvironmentState::ChaseAwakened)
	{
		SunAccentIntensity = DYStageEnvironmentVisuals::ChaseSunAccentIntensityLumens;
		ChaseAccentIntensity = DYStageEnvironmentVisuals::ChaseWingAccentIntensityLumens;
	}
	else if (CurrentState == EDYStageEnvironmentState::FinaleReady)
	{
		// Bounded Dev comparison under the unchanged manual exposure and existing light geometry.
		// Dim only the two non-shadowing accents; never change the player-controlled projection lamp.
		SunAccentIntensity = DYStageEnvironmentVisuals::ChaseSunAccentIntensityLumens * 0.5f;
		ChaseAccentIntensity = DYStageEnvironmentVisuals::ChaseWingAccentIntensityLumens * 0.25f;
	}
	else if (CurrentState == EDYStageEnvironmentState::ForestComplete)
	{
		// Recombine already tested maxima rather than raising an arbitrary new whole-room brightness.
		SunAccentIntensity = DYStageEnvironmentVisuals::SunAwakenedIntensityLumens;
		ChaseAccentIntensity = DYStageEnvironmentVisuals::ChaseWingAccentIntensityLumens;
	}
	SunAwakenedAccent->SetIntensity(SunAccentIntensity);
	ChaseAwakenedAccent->SetIntensity(ChaseAccentIntensity);
}

#if !UE_BUILD_SHIPPING
namespace DYStageEnvironmentDevCommands
{
	static void ForceForestComplete(UWorld* World)
	{
		if (!World)
		{
			return;
		}
		TWeakObjectPtr<UWorld> WeakWorld(World);
		FTimerHandle ApplyHandle;
		World->GetTimerManager().SetTimer(ApplyHandle, FTimerDelegate::CreateWeakLambda(World, [WeakWorld]()
		{
			UWorld* const LiveWorld = WeakWorld.Get();
			if (!LiveWorld)
			{
				return;
			}
			for (TActorIterator<ADYStageEnvironment> It(LiveWorld); It; ++It)
			{
				if (It->GetCurrentState() != EDYStageEnvironmentState::ForestComplete)
				{
					It->ApplyState(EDYStageEnvironmentState::ForestComplete);
					UE_LOG(LogTemp, Log, TEXT("[DYExterior] forced ForestComplete on %s"), *It->GetName());
				}
			}
		}), 6.0f, true, 6.0f);
		FTimerHandle StopHandle;
		World->GetTimerManager().SetTimer(StopHandle, FTimerDelegate::CreateWeakLambda(World, [WeakWorld, ApplyHandle]() mutable
		{
			if (UWorld* const LiveWorld = WeakWorld.Get())
			{
				LiveWorld->GetTimerManager().ClearTimer(ApplyHandle);
			}
		}), 96.0f, false);
	}
}

static FAutoConsoleCommandWithWorld GDYForceForestComplete(
	TEXT("dy.ForceForestComplete"),
	TEXT("Dev only: drive the stage environment to ForestComplete to review the exterior greening reaction."),
	FConsoleCommandWithWorldDelegate::CreateStatic(&DYStageEnvironmentDevCommands::ForceForestComplete));
#endif