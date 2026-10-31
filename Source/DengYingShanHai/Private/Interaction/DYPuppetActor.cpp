#include "Interaction/DYPuppetActor.h"

#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Interaction/DYPuppetCastTypes.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "Materials/MaterialInterface.h"
#include "Puppets/DYPuppetPerformanceComponent.h"
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
	Performance = CreateDefaultSubobject<UDYPuppetPerformanceComponent>(TEXT("PuppetPerformance"));

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

USkeletalMeshComponent* ADYPuppetActor::GetActivePuppetMesh() const
{
	if (FigureCast && FigureCast->Figures.IsValidIndex(ActiveFigureIndex))
	{
		const FDYPuppetFigureEntry& Figure = FigureCast->Figures[ActiveFigureIndex];
		if (Figure.PoseAnimations.Num() > 0)
		{
			return CastMesh;
		}
	}
	return FigureMesh;
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

	ApplyPoseAnimation(NewPoseId);
}

void ADYPuppetActor::ResolveFigureCast()
{
	if (FigureCast)
	{
		return;
	}
	// The shipped cast lives at a stable content path so the level and Blueprint stay untouched.
	FigureCast = LoadObject<UDYPuppetCastData>(nullptr,
		TEXT("/Game/DengYingShanHai/Puppets/DA_DYPuppetCast.DA_DYPuppetCast"));
}

void ADYPuppetActor::ApplyChapterFigure(const int32 ChapterIndex, const bool bForce)
{
	ResolveFigureCast();
	if (!FigureCast || !FigureCast->Figures.IsValidIndex(ChapterIndex))
	{
		return;
	}
	if (!bForce && ActiveFigureIndex == ChapterIndex)
	{
		ApplyPoseAnimation(GetPoseId());
		return;
	}
	const FDYPuppetFigureEntry& Figure = FigureCast->Figures[ChapterIndex];
	USkeletalMesh* LoadedMesh = Figure.SkeletalMesh.LoadSynchronous();
	if (!FigureMesh)
	{
		FigureMesh = FindComponentByClass<USkeletalMeshComponent>();
	}
	if (!LoadedMesh)
	{
		return;
	}

	const bool bBakedClips = Figure.PoseAnimations.Num() > 0;
	if (bBakedClips && !CastMesh)
	{
		// A private display component avoids the Blueprint's Kuafu Anim Blueprint, which
		// drives a different bone set and would distort these rigs.
		CastMesh = NewObject<USkeletalMeshComponent>(this, TEXT("DYChapterCastMesh"));
		CastMesh->SetMobility(EComponentMobility::Movable);
		CastMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
		CastMesh->SetupAttachment(SceneRoot);
		CastMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		CastMesh->SetCastShadow(true);
		CastMesh->RegisterComponent();
		AddInstanceComponent(CastMesh);
	}

	USkeletalMeshComponent* ActiveMesh = bBakedClips ? CastMesh : FigureMesh;
	if (!ActiveMesh)
	{
		return;
	}
	if (ActiveMesh->GetSkeletalMeshAsset() != LoadedMesh)
	{
		ActiveMesh->SetSkeletalMeshAsset(LoadedMesh);
	}
	ActiveMesh->SetRelativeLocation(Figure.MeshRelativeLocation);
	ActiveMesh->SetRelativeRotation(Figure.MeshRelativeRotation);
	ActiveMesh->SetRelativeScale3D(Figure.MeshRelativeScale);
	Torso->SetRelativeLocation(Figure.ControlProxyRelativeLocation);
	ActiveMesh->SetVisibility(true, true);
	ActiveMesh->SetCastShadow(true);
	// Jingwei's animated feathers leave bind-pose bounds; retain their VSM invalidation region.
	ActiveMesh->SetBoundsScale(ChapterIndex == 1 ? 1.5f : 1.0f);

	// Only one display component may draw or cast at a time, otherwise a leftover Kuafu
	// mesh would double the silhouette.
	if (CastMesh)
	{
		CastMesh->SetVisibility(bBakedClips, true);
		CastMesh->SetCastShadow(bBakedClips);
	}
	if (FigureMesh)
	{
		FigureMesh->SetVisibility(!bBakedClips, true);
		FigureMesh->SetCastShadow(!bBakedClips);
	}
	if (Staff)
	{
		Staff->SetVisibility(!Figure.bHideStaff, true);
	}
	ActiveFigureIndex = ChapterIndex;
	ApplyPoseAnimation(GetPoseId());
}

void ADYPuppetActor::SetChapterDaylight(const bool bDaylight)
{
	if (bChapterDaylight == bDaylight) { return; }
	bChapterDaylight = bDaylight;
	ApplyPoseAnimation(GetPoseId());
}

void ADYPuppetActor::ApplyPoseAnimation(const FName PoseId)
{
	// Rail facts keep updating while the short reaction owns the visible pose.
	if (Performance && Performance->OwnsAnimation()) { return; }
	if (!FigureCast || !FigureCast->Figures.IsValidIndex(ActiveFigureIndex))
	{
		return;
	}
	auto& Figure = FigureCast->Figures[ActiveFigureIndex];
	USkeletalMeshComponent* ActiveMesh = Figure.PoseAnimations.Num() > 0 ? CastMesh : FigureMesh;
	if (!ActiveMesh)
	{
		return;
	}
	const TMap<FName, TSoftObjectPtr<UAnimSequence>>& Clips = Figure.PoseAnimations;
	// Zhulong's eye is a chapter fact: moving its rail must not open it during Night.
	const FName DisplayPose = ActiveFigureIndex == 3
		? FName(bChapterDaylight ? TEXT("P02_StrideReach") : TEXT("P02_StrideBack")) : PoseId;
	const TSoftObjectPtr<UAnimSequence>* Found = Clips.Find(DisplayPose);
	if (!Found)
	{
		Found = Clips.Find(NAME_None);
	}
	if (!Found || Found->IsNull())
	{
		return;
	}
	if (UAnimSequence* Clip = Found->LoadSynchronous())
	{
		// SetAnimation/Play alone do nothing on a fresh component in Blueprint mode.
		if (ActiveMesh->GetAnimationMode() != EAnimationMode::AnimationSingleNode)
		{
			ActiveMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
		}
		UAnimSingleNodeInstance* Instance = ActiveMesh->GetSingleNodeInstance();
		if (!Instance || Instance->GetAnimationAsset() != Clip)
		{
			ActiveMesh->PlayAnimation(Clip, false);
			ActiveMesh->SetPosition(0.0f, false);
		}
		// Repeated rail updates keep the same clip and do not rewind its playback.
	}
}