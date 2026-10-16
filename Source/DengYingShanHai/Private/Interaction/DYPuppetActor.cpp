#include "Interaction/DYPuppetActor.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

ADYPuppetActor::ADYPuppetActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);

	Torso = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Torso"));
	Torso->SetupAttachment(SceneRoot);
	Torso->SetRelativeScale3D(FVector(0.48, 0.16, 1.15));
	Torso->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Torso->SetCollisionResponseToAllChannels(ECR_Ignore);
	Torso->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
	Torso->SetCastShadow(true);

	Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
	Head->SetupAttachment(SceneRoot);
	Head->SetRelativeLocation(FVector(0.0, 0.0, 145.0));
	Head->SetRelativeScale3D(FVector(0.38));
	Head->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Head->SetCastShadow(true);

	Staff = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Staff"));
	Staff->SetupAttachment(SceneRoot);
	Staff->SetRelativeLocation(FVector(0.0, -45.0, 25.0));
	Staff->SetRelativeRotation(FRotator(0.0, 0.0, -18.0));
	Staff->SetRelativeScale3D(FVector(0.06, 0.06, 1.55));
	Staff->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Staff->SetCastShadow(true);

	PuppetControl = CreateDefaultSubobject<UDYPuppetControlComponent>(TEXT("PuppetControl"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> BasicMaterial(TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	if (CubeMesh.Succeeded())
	{
		Torso->SetStaticMesh(CubeMesh.Object);
	}
	if (SphereMesh.Succeeded())
	{
		Head->SetStaticMesh(SphereMesh.Object);
	}
	if (CylinderMesh.Succeeded())
	{
		Staff->SetStaticMesh(CylinderMesh.Object);
	}
	if (BasicMaterial.Succeeded())
	{
		Torso->SetMaterial(0, BasicMaterial.Object);
		Head->SetMaterial(0, BasicMaterial.Object);
		Staff->SetMaterial(0, BasicMaterial.Object);
	}
}

void ADYPuppetActor::BeginPlay()
{
	Super::BeginPlay();
	PuppetControl->OnControlChanged.AddUniqueDynamic(this, &ADYPuppetActor::HandleControlChanged);
	HandleControlChanged(PuppetControl->GetNormalizedValue(), PuppetControl->GetPoseId());
}

FName ADYPuppetActor::GetPoseId() const
{
	return PuppetControl ? PuppetControl->GetPoseId() : NAME_None;
}

FDYStaffGeometrySnapshot ADYPuppetActor::GetStaffGeometrySnapshot() const
{
	FDYStaffGeometrySnapshot Result;
	if (!IsValid(Staff) || !Staff->GetStaticMesh()) { return Result; }
	Staff->GetLocalBounds(Result.LocalMin, Result.LocalMax);
	Result.ComponentTransform = Staff->GetComponentTransform();
	const FVector Scale = Result.ComponentTransform.GetScale3D();
	if (Result.LocalMin.ContainsNaN() || Result.LocalMax.ContainsNaN()
		|| Result.ComponentTransform.ContainsNaN()
		|| FMath::Abs(Scale.X) <= UE_SMALL_NUMBER
		|| FMath::Abs(Scale.Y) <= UE_SMALL_NUMBER
		|| FMath::Abs(Scale.Z) <= UE_SMALL_NUMBER
		|| Result.LocalMax.Z - Result.LocalMin.Z <= UE_SMALL_NUMBER)
	{
		return Result;
	}
	const FVector Center = (Result.LocalMin + Result.LocalMax) * 0.5;
	Result.EndAWorld = Result.ComponentTransform.TransformPosition(FVector(Center.X, Center.Y, Result.LocalMin.Z));
	Result.EndBWorld = Result.ComponentTransform.TransformPosition(FVector(Center.X, Center.Y, Result.LocalMax.Z));
	Result.bIsValid = !Result.EndAWorld.ContainsNaN() && !Result.EndBWorld.ContainsNaN();
	return Result;
}

bool ADYPuppetActor::CanBeginControl_Implementation(const FDYControlContext& Context) const
{
	return Context.InstigatorPawn != nullptr
		&& PuppetControl
		&& PuppetControl->IsControlEnabled()
		&& !PuppetControl->IsUnderControl();
}

void ADYPuppetActor::BeginControl_Implementation(const FDYControlContext& Context)
{
	PuppetControl->BeginControl();
}

void ADYPuppetActor::ApplyControlIntent_Implementation(const FDYControlIntent& Intent)
{
	PuppetControl->ApplyControlIntent(Intent);
}

void ADYPuppetActor::EndControl_Implementation(const FDYControlContext& Context)
{
	PuppetControl->EndControl();
}

void ADYPuppetActor::ResetControlState_Implementation(const FDYControlContext& Context)
{
	OnResetRequested.Broadcast();
}

void ADYPuppetActor::SetControlEnabled_Implementation(const bool bEnabled)
{
	PuppetControl->SetControlEnabled(bEnabled);
}

FDYControlSnapshot ADYPuppetActor::GetControlSnapshot_Implementation() const
{
	return PuppetControl->GetControlSnapshot();
}

void ADYPuppetActor::HandleControlChanged(const double NormalizedValue, const FName NewPoseId)
{
	// Minimal Dev-only pose readability. Final silhouette animation remains a
	// Blueprint/Control Rig responsibility and does not affect logical state.
	float SignedPose = static_cast<float>((NormalizedValue - 0.5) * 2.0);
	if (NewPoseId == TEXT("P02_StrideBack"))
	{
		SignedPose = -1.0f;
	}
	else if (NewPoseId == TEXT("P02_StrideMid"))
	{
		SignedPose = 0.0f;
	}
	else if (NewPoseId == TEXT("P02_StrideReach"))
	{
		SignedPose = 1.0f;
	}
	Torso->SetRelativeRotation(FRotator(0.0, SignedPose * 8.0f, SignedPose * 5.0f));
	Head->SetRelativeRotation(FRotator(0.0, SignedPose * 10.0f, 0.0));
	Staff->SetRelativeRotation(FRotator(0.0, 0.0, -18.0f - SignedPose * 20.0f));
}
