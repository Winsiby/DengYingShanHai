#include "Interaction/DYPuppetControlComponent.h"

#include "GameFramework/Actor.h"

UDYPuppetControlComponent::UDYPuppetControlComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	PoseIds = {
		TEXT("P02_StrideBack"),
		TEXT("P02_StrideMid"),
		TEXT("P02_StrideReach")
	};
}

void UDYPuppetControlComponent::BeginPlay()
{
	Super::BeginPlay();

	if (AActor* Owner = GetOwner())
	{
		RailCenter = Owner->GetActorLocation();
		bRailInitialized = true;
		SetNormalizedValue(InitialNormalizedValue);
	}
}

void UDYPuppetControlComponent::BeginControl()
{
	bUnderControl = bControlEnabled;
}

void UDYPuppetControlComponent::EndControl()
{
	bUnderControl = false;
}

void UDYPuppetControlComponent::ApplyControlIntent(const FDYControlIntent& Intent)
{
	if (!bControlEnabled || !bUnderControl || Intent.Channel != EDYControlChannel::PrimaryAxis)
	{
		return;
	}

	SetNormalizedValue(CurrentNormalizedValue + Intent.Value.X * NormalizedUnitsPerSecond * Intent.DeltaSeconds);
}

void UDYPuppetControlComponent::SetControlEnabled(const bool bEnabled)
{
	bControlEnabled = bEnabled;
	// The InteractionComponent remains the sole owner of the active control
	// session and input context, matching the light-control capability.
}

void UDYPuppetControlComponent::SetNormalizedValue(const double NewValue)
{
	AActor* Owner = GetOwner();
	if (!Owner)
	{
		return;
	}

	if (!bRailInitialized)
	{
		RailCenter = Owner->GetActorLocation();
		bRailInitialized = true;
	}

	const double ClampedValue = FMath::Clamp(NewValue, 0.0, 1.0);
	const int32 PreviousPoseIndex = GetPoseIndexForNormalizedValue(CurrentNormalizedValue);
	const bool bValueChanged = !FMath::IsNearlyEqual(CurrentNormalizedValue, ClampedValue, UE_DOUBLE_SMALL_NUMBER);
	CurrentNormalizedValue = ClampedValue;
	Owner->SetActorLocation(GetWorldLocationForNormalizedValue(CurrentNormalizedValue), false, nullptr, ETeleportType::TeleportPhysics);

	if (bValueChanged || PreviousPoseIndex != GetPoseIndexForNormalizedValue(CurrentNormalizedValue))
	{
		OnControlChanged.Broadcast(CurrentNormalizedValue, GetPoseId());
	}
}

void UDYPuppetControlComponent::ResetToInitialValue()
{
	SetNormalizedValue(InitialNormalizedValue);
}

FName UDYPuppetControlComponent::GetPoseId() const
{
	const int32 PoseIndex = GetPoseIndexForNormalizedValue(CurrentNormalizedValue);
	return PoseIds.IsValidIndex(PoseIndex) ? PoseIds[PoseIndex] : NAME_None;
}

FDYControlSnapshot UDYPuppetControlComponent::GetControlSnapshot() const
{
	FDYControlSnapshot Snapshot;
	if (const AActor* Owner = GetOwner())
	{
		Snapshot.bIsValid = true;
		Snapshot.PrimaryNormalized = CurrentNormalizedValue;
		Snapshot.PoseId = GetPoseId();
		Snapshot.WorldTransform = Owner->GetActorTransform();
	}
	return Snapshot;
}

FVector UDYPuppetControlComponent::GetWorldLocationForNormalizedValue(const double Value) const
{
	return RailCenter + GetSafeWorldAxis() * ((FMath::Clamp(Value, 0.0, 1.0) - 0.5) * TravelDistance);
}

void UDYPuppetControlComponent::GetRailWorldEndpoints(FVector& OutStart, FVector& OutEnd) const
{
	OutStart = GetWorldLocationForNormalizedValue(0.0);
	OutEnd = GetWorldLocationForNormalizedValue(1.0);
}

FVector UDYPuppetControlComponent::GetSafeWorldAxis() const
{
	const FVector Axis = WorldTravelAxis.GetSafeNormal();
	return Axis.IsNearlyZero() ? FVector::RightVector : Axis;
}

int32 UDYPuppetControlComponent::GetPoseIndexForNormalizedValue(const double Value) const
{
	if (PoseIds.IsEmpty())
	{
		return INDEX_NONE;
	}

	return FMath::Clamp(
		FMath::RoundToInt(FMath::Clamp(Value, 0.0, 1.0) * static_cast<double>(PoseIds.Num() - 1)),
		0,
		PoseIds.Num() - 1);
}
