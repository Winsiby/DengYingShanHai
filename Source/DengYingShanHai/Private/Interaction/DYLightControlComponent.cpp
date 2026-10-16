#include "Interaction/DYLightControlComponent.h"

#include "GameFramework/Actor.h"

UDYLightControlComponent::UDYLightControlComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UDYLightControlComponent::BeginPlay()
{
	Super::BeginPlay();

	if (AActor* Owner = GetOwner())
	{
		RailCenter = Owner->GetActorLocation();
		bRailInitialized = true;
		SetNormalizedValue(InitialNormalizedValue);
	}
}

void UDYLightControlComponent::BeginControl()
{
	bUnderControl = bControlEnabled;
}

void UDYLightControlComponent::EndControl()
{
	bUnderControl = false;
}

void UDYLightControlComponent::ApplyControlIntent(const FDYControlIntent& Intent)
{
	if (!bControlEnabled || !bUnderControl || Intent.Channel != EDYControlChannel::PrimaryAxis)
	{
		return;
	}

	SetNormalizedValue(CurrentNormalizedValue + Intent.Value.X * NormalizedUnitsPerSecond * Intent.DeltaSeconds);
}

void UDYLightControlComponent::SetControlEnabled(const bool bEnabled)
{
	bControlEnabled = bEnabled;
	// Enabling/disabling gameplay response must not silently end the owning
	// InteractionComponent's session. This preserves one source of truth for
	// input-context lifetime; ApplyControlIntent still gates on both flags.
}

void UDYLightControlComponent::SetNormalizedValue(const double NewValue)
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
	const bool bChanged = !FMath::IsNearlyEqual(CurrentNormalizedValue, ClampedValue, UE_DOUBLE_SMALL_NUMBER);
	CurrentNormalizedValue = ClampedValue;
	Owner->SetActorLocation(GetWorldLocationForNormalizedValue(CurrentNormalizedValue), false, nullptr, ETeleportType::TeleportPhysics);

	if (bChanged)
	{
		OnNormalizedValueChanged.Broadcast(CurrentNormalizedValue);
	}
}

void UDYLightControlComponent::ResetToInitialValue()
{
	SetNormalizedValue(InitialNormalizedValue);
}

FDYControlSnapshot UDYLightControlComponent::GetControlSnapshot() const
{
	FDYControlSnapshot Snapshot;
	if (const AActor* Owner = GetOwner())
	{
		Snapshot.bIsValid = true;
		Snapshot.PrimaryNormalized = CurrentNormalizedValue;
		Snapshot.WorldTransform = Owner->GetActorTransform();
	}
	return Snapshot;
}

FVector UDYLightControlComponent::GetWorldLocationForNormalizedValue(const double Value) const
{
	return RailCenter + GetSafeWorldAxis() * ((FMath::Clamp(Value, 0.0, 1.0) - 0.5) * TravelDistance);
}

void UDYLightControlComponent::GetRailWorldEndpoints(FVector& OutStart, FVector& OutEnd) const
{
	OutStart = GetWorldLocationForNormalizedValue(0.0);
	OutEnd = GetWorldLocationForNormalizedValue(1.0);
}

FVector UDYLightControlComponent::GetSafeWorldAxis() const
{
	const FVector Axis = WorldTravelAxis.GetSafeNormal();
	return Axis.IsNearlyZero() ? FVector::RightVector : Axis;
}
