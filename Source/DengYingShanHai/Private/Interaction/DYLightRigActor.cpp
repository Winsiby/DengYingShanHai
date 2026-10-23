#include "Interaction/DYLightRigActor.h"

#include "Components/SceneComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Interaction/DYLightControlComponent.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

namespace DYLightRigVisuals
{
	constexpr float SearchingIntensityLumens = 30000.0f;
	constexpr float ResolvedIntensityLumens = 42000.0f;
}

ADYLightRigActor::ADYLightRigActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);

	LampStand = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LampStand"));
	LampStand->SetupAttachment(SceneRoot);
	LampStand->SetRelativeLocation(FVector(0.0, 0.0, -95.0));
	LampStand->SetRelativeScale3D(FVector(0.12, 0.12, 1.0));
	LampStand->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	LampStand->SetCollisionResponseToAllChannels(ECR_Ignore);
	LampStand->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);

	LampBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LampBody"));
	LampBody->SetupAttachment(SceneRoot);
	LampBody->SetRelativeRotation(FRotator(0.0, 90.0, 0.0));
	LampBody->SetRelativeScale3D(FVector(0.45, 0.45, 0.55));
	LampBody->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	LampBody->SetCollisionResponseToAllChannels(ECR_Ignore);
	LampBody->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);

	KeyLight = CreateDefaultSubobject<USpotLightComponent>(TEXT("KeyLight"));
	KeyLight->SetupAttachment(SceneRoot);
	KeyLight->SetRelativeLocation(FVector(45.0, 0.0, 0.0));
	KeyLight->SetMobility(EComponentMobility::Movable);
	KeyLight->SetIntensityUnits(ELightUnits::Lumens);
	KeyLight->SetIntensity(DYLightRigVisuals::SearchingIntensityLumens);
	KeyLight->SetAttenuationRadius(2200.0f);
	KeyLight->SetInnerConeAngle(20.0f);
	KeyLight->SetOuterConeAngle(38.0f);
	KeyLight->SetSourceRadius(4.0f);
	KeyLight->SetCastShadows(true);
	KeyLight->SetLightColor(FLinearColor(1.0f, 0.78f, 0.52f));

	LightControl = CreateDefaultSubobject<UDYLightControlComponent>(TEXT("LightControl"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> ConeMesh(TEXT("/Engine/BasicShapes/Cone.Cone"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> BasicMaterial(TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	if (CylinderMesh.Succeeded())
	{
		LampStand->SetStaticMesh(CylinderMesh.Object);
	}
	if (ConeMesh.Succeeded())
	{
		LampBody->SetStaticMesh(ConeMesh.Object);
	}
	if (BasicMaterial.Succeeded())
	{
		LampStand->SetMaterial(0, BasicMaterial.Object);
		LampBody->SetMaterial(0, BasicMaterial.Object);
	}
}

void ADYLightRigActor::ApplyResolvedDevFeedback(const bool bResolved)
{
	KeyLight->SetLightColor(bResolved ? FLinearColor(1.0f, 0.42f, 0.08f) : FLinearColor(1.0f, 0.78f, 0.52f));
	KeyLight->SetIntensity(bResolved
		? DYLightRigVisuals::ResolvedIntensityLumens
		: DYLightRigVisuals::SearchingIntensityLumens);
}

bool ADYLightRigActor::CanBeginControl_Implementation(const FDYControlContext& Context) const
{
	return Context.InstigatorPawn != nullptr && LightControl && LightControl->IsControlEnabled() && !LightControl->IsUnderControl();
}

void ADYLightRigActor::BeginControl_Implementation(const FDYControlContext& Context)
{
	LightControl->BeginControl();
}

void ADYLightRigActor::ApplyControlIntent_Implementation(const FDYControlIntent& Intent)
{
	LightControl->ApplyControlIntent(Intent);
}

void ADYLightRigActor::EndControl_Implementation(const FDYControlContext& Context)
{
	LightControl->EndControl();
}

void ADYLightRigActor::ResetControlState_Implementation(const FDYControlContext& Context)
{
	OnResetRequested.Broadcast();
}

void ADYLightRigActor::SetControlEnabled_Implementation(const bool bEnabled)
{
	LightControl->SetControlEnabled(bEnabled);
}

FDYControlSnapshot ADYLightRigActor::GetControlSnapshot_Implementation() const
{
	return LightControl->GetControlSnapshot();
}
