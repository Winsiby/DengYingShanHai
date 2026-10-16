#include "Stage/DYStageEnvironment.h"

#include "Components/PointLightComponent.h"
#include "Components/SceneComponent.h"

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
}

void ADYStageEnvironment::BeginPlay()
{
	Super::BeginPlay();
	ApplyVisualState();
}

void ADYStageEnvironment::ApplyState(const EDYStageEnvironmentState NewState)
{
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
}

void ADYStageEnvironment::ResetToDormant()
{
	ApplyState(EDYStageEnvironmentState::Dormant);
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
