#include "Puppets/DYPuppetPerformanceComponent.h"

#include "DengYingShanHai.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "Interaction/DYPuppetActor.h"
#include "TimerManager.h"
#include "UI/DYInteractionHUDWidget.h"
#include "UObject/UObjectIterator.h"

UDYPuppetPerformanceComponent::UDYPuppetPerformanceComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
}

void UDYPuppetPerformanceComponent::BeginPlay()
{
	Super::BeginPlay();
	ResolveData();
}

void UDYPuppetPerformanceComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	CancelPlayback();
	Super::EndPlay(EndPlayReason);
}

void UDYPuppetPerformanceComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (!bPerforming) { return; }

	SegmentElapsed += DeltaTime;
	ElapsedSeconds += DeltaTime;

	const bool bSegmentOver = ActiveSegments.IsValidIndex(SegmentIndex) && SegmentElapsed >= ActiveSegments[SegmentIndex].Seconds;
	if (!bSegmentOver) { return; }

	if (SegmentIndex + 1 < ActiveSegments.Num())
	{
		PlaySegment(SegmentIndex + 1);
	}
	else
	{
		Finish(false);
	}
}

void UDYPuppetPerformanceComponent::ResolveData()
{
	if (ResolvedData) { return; }

	// Only an explicitly assigned data asset enables the continuous show. A fixed-path fallback
	// would also light up automation fixtures (which spawn default actors), silently deferring the
	// resolve notification that those tests expect immediately.
	if (!PerformanceData.IsNull())
	{
		ResolvedData = PerformanceData.LoadSynchronous();
	}

	if (!ResolvedData)
	{
		UE_LOG(LogTemp, Warning, TEXT("DYPuppetPerformance: no performance data asset; chapters fall back to the plain pose clips."));
	}
}

bool UDYPuppetPerformanceComponent::HasChapter(int32 ChapterIndex) const
{
	if (!ResolvedData) { return false; }
	const FDYActPerformance* Act = ResolvedData->FindAct(ChapterIndex);
	if (!Act) { return false; }
	return Act->Segments.Num() > 0;
}

bool UDYPuppetPerformanceComponent::StartChapterPerformance(int32 ChapterIndex)
{
	if (bPerforming) { return false; }

	ResolveData();
	if (!ResolvedData) { return false; }

	const FDYActPerformance* Act = ResolvedData->FindAct(ChapterIndex);
	if (!Act || Act->Segments.Num() == 0) { return false; }

	// Supersede the short reaction before the full show takes animation ownership.
	CancelPlayback();
	ActiveSegments = Act->Segments;
	ActiveFeedback = Act->Feedback;
	PerformingChapter = ChapterIndex;
	SegmentIndex = INDEX_NONE;
	SegmentElapsed = 0.f;
	ElapsedSeconds = 0.f;
	TotalSeconds = 0.f;
	for (const FDYPerformanceSegment& Segment : ActiveSegments)
	{
		TotalSeconds += FMath::Max(0.f, Segment.Seconds);
	}

	bPerforming = true;
	UE_LOG(LogDengYingShanHai, Display,
		TEXT("[PuppetPerformance] chapter %d starts: %d segments, %.2f s, mesh=%s"),
		PerformingChapter, ActiveSegments.Num(), TotalSeconds,
		GetTargetMesh() ? *GetTargetMesh()->GetName() : TEXT("none"));
	PlaySegment(0);
	return true;
}

void UDYPuppetPerformanceComponent::PlaySegment(int32 InSegmentIndex)
{
	if (!ActiveSegments.IsValidIndex(InSegmentIndex))
	{
		Finish(false);
		return;
	}

	SegmentIndex = InSegmentIndex;
	SegmentElapsed = 0.f;

	const FDYPerformanceSegment& Segment = ActiveSegments[InSegmentIndex];
	PlayOnMesh(Segment, Segment.bLoop);
	ShowCaption(FText::FromString(Segment.Caption), Segment.Seconds);
}

void UDYPuppetPerformanceComponent::PlayOnMesh(const FDYPerformanceSegment& Segment, bool bForceLoop)
{
	USkeletalMeshComponent* Mesh = GetTargetMesh();
	if (!Mesh) { return; }

	UAnimSequence* Animation = Segment.Animation.LoadSynchronous();
	if (!Animation) { return; }

	if (!PlaybackMesh.IsValid())
	{
		PlaybackMesh = Mesh;
		bRestoreAnimationBlueprint = Mesh->GetAnimationMode() == EAnimationMode::AnimationBlueprint;
	}
	// PlayAnimation preserves AnimClass, so legacy Kuafu can resume its own Blueprint.
	Mesh->PlayAnimation(Animation, bForceLoop);
	Mesh->SetPlayRate(1.f);
	Mesh->SetPosition(0.f, false);
}

void UDYPuppetPerformanceComponent::TriggerFeedback(int32 ChapterIndex)
{
	if (bPerforming) { return; }

	ResolveData();
	if (!ResolvedData) { return; }

	const FDYActPerformance* Act = ResolvedData->FindAct(ChapterIndex);
	if (!Act || Act->Feedback.Num() == 0) { return; }

	// Rotate through the authored reactions so repeated progress steps never look identical.
	FeedbackCursor = (FeedbackCursor + 1) % Act->Feedback.Num();
	const FDYPerformanceSegment& Segment = Act->Feedback[FeedbackCursor];
	UE_LOG(LogDengYingShanHai, Display, TEXT("[PuppetPerformance] chapter %d feedback beat %d"), ChapterIndex, FeedbackCursor);
	bFeedbackActive = true;
	PlayOnMesh(Segment, false);

	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(FeedbackHandle);
		World->GetTimerManager().SetTimer(FeedbackHandle, this, &UDYPuppetPerformanceComponent::RestorePose, FMath::Max(0.2f, Segment.Seconds), false);
	}
	else
	{
		RestorePose();
	}
}

void UDYPuppetPerformanceComponent::RestorePose()
{
	if (bPerforming) { return; }
	if (UWorld* World = GetWorld()) { World->GetTimerManager().ClearTimer(FeedbackHandle); }
	bFeedbackActive = false;
	USkeletalMeshComponent* Mesh = PlaybackMesh.Get();
	const bool bResumeBlueprint = bRestoreAnimationBlueprint;
	PlaybackMesh.Reset();
	bRestoreAnimationBlueprint = false;
	if (Mesh && bResumeBlueprint)
	{
		Mesh->SetAnimationMode(EAnimationMode::AnimationBlueprint);
	}

	if (ADYPuppetActor* Puppet = GetPuppetOwner())
	{
		Puppet->ApplyPoseAnimation(Puppet->GetPoseId());
	}
}

void UDYPuppetPerformanceComponent::SkipPerformance()
{
	Finish(true);
}

void UDYPuppetPerformanceComponent::CancelPlayback()
{
	const bool bHadPlayback = OwnsAnimation() || PlaybackMesh.IsValid();
	if (UWorld* World = GetWorld()) { World->GetTimerManager().ClearTimer(FeedbackHandle); }
	bPerforming = false;
	bFeedbackActive = false;
	PerformingChapter = INDEX_NONE;
	SegmentIndex = INDEX_NONE;
	ActiveSegments.Reset();
	ActiveFeedback.Reset();
	SegmentElapsed = ElapsedSeconds = TotalSeconds = 0.f;
	if (bHadPlayback) { RestorePose(); }
}

void UDYPuppetPerformanceComponent::Finish(bool bSkipped)
{
	if (!bPerforming) { return; }

	const int32 FinishedChapter = PerformingChapter;
	UE_LOG(LogDengYingShanHai, Display, TEXT("[PuppetPerformance] chapter %d finished skipped=%d at %.2f/%.2f s"),
		FinishedChapter, bSkipped ? 1 : 0, ElapsedSeconds, TotalSeconds);
	bPerforming = false;
	PerformingChapter = INDEX_NONE;
	SegmentIndex = INDEX_NONE;
	ActiveSegments.Reset();
	ActiveFeedback.Reset();

	RestorePose();
	OnPerformanceFinished.Broadcast(FinishedChapter, bSkipped);
}

float UDYPuppetPerformanceComponent::GetPerformanceProgress() const
{
	return TotalSeconds > KINDA_SMALL_NUMBER ? FMath::Clamp(ElapsedSeconds / TotalSeconds, 0.f, 1.f) : 0.f;
}

void UDYPuppetPerformanceComponent::ShowCaption(const FText& Caption, float Seconds)
{
	// The skip key is discoverable from the show itself; no separate tutorial line.
	const FText Suffix = NSLOCTEXT("DYPuppetPerformance", "SkipHint", "　空格可跳过演出");
	const FText Shown = Caption.IsEmpty() ? Suffix : FText::FromString(Caption.ToString() + Suffix.ToString());

	UWorld* World = GetWorld();
	if (!World) { return; }

	for (TObjectIterator<UDYInteractionHUDWidget> It; It; ++It)
	{
		UDYInteractionHUDWidget* Widget = *It;
		if (IsValid(Widget) && Widget->GetWorld() == World)
		{
			Widget->ShowHint(Shown, Seconds);
			return;
		}
	}
}

ADYPuppetActor* UDYPuppetPerformanceComponent::GetPuppetOwner() const
{
	return Cast<ADYPuppetActor>(GetOwner());
}

USkeletalMeshComponent* UDYPuppetPerformanceComponent::GetTargetMesh() const
{
	const ADYPuppetActor* Puppet = GetPuppetOwner();
	return Puppet ? Puppet->GetActivePuppetMesh() : nullptr;
}

bool UDYPuppetPerformanceComponent::SkipAnyPerformanceInWorld(UWorld* World)
{
	if (!World) { return false; }

	for (TObjectIterator<UDYPuppetPerformanceComponent> It; It; ++It)
	{
		UDYPuppetPerformanceComponent* Component = *It;
		if (!IsValid(Component) || Component->GetWorld() != World || !Component->IsPerforming()) { continue; }
		Component->SkipPerformance();
		return true;
	}
	return false;
}