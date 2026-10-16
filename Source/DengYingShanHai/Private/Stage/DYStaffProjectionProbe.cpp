#include "Stage/DYStaffProjectionProbe.h"

#include "Components/TextRenderComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Interaction/DYLightControlComponent.h"
#include "Interaction/DYLightRigActor.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "TimerManager.h"

ADYStaffProjectionProbe::ADYStaffProjectionProbe()
{
	PrimaryActorTick.bCanEverTick = false;
	Readout = CreateDefaultSubobject<UTextRenderComponent>(TEXT("Readout"));
	SetRootComponent(Readout);
	Readout->SetWorldSize(15.0f);
	Readout->SetTextRenderColor(FColor::White);
	MarkerA = CreateDefaultSubobject<UTextRenderComponent>(TEXT("MarkerA"));
	MarkerB = CreateDefaultSubobject<UTextRenderComponent>(TEXT("MarkerB"));
	for (UTextRenderComponent* Marker : { MarkerA.Get(), MarkerB.Get() })
	{
		Marker->SetupAttachment(Readout);
		Marker->SetWorldSize(18.0f);
		Marker->SetHorizontalAlignment(EHTA_Center);
		Marker->SetVerticalAlignment(EVRTA_TextCenter);
	}
	MarkerA->SetText(FText::FromString(TEXT("A")));
	MarkerB->SetText(FText::FromString(TEXT("B")));
	MarkerA->SetTextRenderColor(FColor::Cyan);
	MarkerB->SetTextRenderColor(FColor::Magenta);
	for (UTextRenderComponent* Text : { Readout.Get(), MarkerA.Get(), MarkerB.Get() })
	{
		Text->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Text->SetCastShadow(false);
		Text->SetVisibility(false);
	}
}

void ADYStaffProjectionProbe::BeginPlay()
{
	Super::BeginPlay();
	// Editor RefreshProjection can serialize visible text into a Dev map. Always
	// override that persisted render state before the Development-only refresh.
	for (UTextRenderComponent* Text : { Readout.Get(), MarkerA.Get(), MarkerB.Get() }) { Text->SetVisibility(false); }
#if !UE_BUILD_SHIPPING
	if (IsValid(Light) && Light->GetLightControlComponent())
	{
		Light->GetLightControlComponent()->OnNormalizedValueChanged.AddUniqueDynamic(this, &ADYStaffProjectionProbe::HandleLightChanged);
	}
	if (IsValid(Puppet) && Puppet->GetPuppetControlComponent())
	{
		Puppet->GetPuppetControlComponent()->OnControlChanged.AddUniqueDynamic(this, &ADYStaffProjectionProbe::HandlePuppetChanged);
	}
	QueueRefresh();
#endif
}

void ADYStaffProjectionProbe::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (IsValid(Light) && Light->GetLightControlComponent())
	{
		Light->GetLightControlComponent()->OnNormalizedValueChanged.RemoveDynamic(this, &ADYStaffProjectionProbe::HandleLightChanged);
	}
	if (IsValid(Puppet) && Puppet->GetPuppetControlComponent())
	{
		Puppet->GetPuppetControlComponent()->OnControlChanged.RemoveDynamic(this, &ADYStaffProjectionProbe::HandlePuppetChanged);
	}
	if (GetWorld()) { GetWorld()->GetTimerManager().ClearTimer(RefreshTimer); }
	LastCapture = FDYStaffProjectionCapture();
	for (UTextRenderComponent* Text : { Readout.Get(), MarkerA.Get(), MarkerB.Get() }) { Text->SetVisibility(false); }
	Super::EndPlay(EndPlayReason);
}

void ADYStaffProjectionProbe::HandleLightChanged(double Value) { QueueRefresh(); }
void ADYStaffProjectionProbe::HandlePuppetChanged(double Value, FName Pose) { QueueRefresh(); }

void ADYStaffProjectionProbe::QueueRefresh()
{
#if !UE_BUILD_SHIPPING
	if (!GetWorld()) { return; }
	// Coalesce and read after every listener (including Staff pose animation) has run.
	GetWorld()->GetTimerManager().ClearTimer(RefreshTimer);
	RefreshTimer = GetWorld()->GetTimerManager().SetTimerForNextTick(
		FTimerDelegate::CreateUObject(this, &ADYStaffProjectionProbe::RefreshProjection));
#endif
}

void ADYStaffProjectionProbe::UpdateMarker(UTextRenderComponent* Marker, const FDYStaffProjectionPoint& Point)
{
	Marker->SetVisibility(Point.Status == EDYStaffProjectionStatus::OnScreen);
	if (Point.Status != EDYStaffProjectionStatus::OnScreen) { return; }
	FVector Normal = LastCapture.ScreenTransform.GetRotation().GetAxisX();
	if (FVector::DotProduct(Normal, LastCapture.EmitterWorld - Point.WorldPosition) < 0.0) { Normal *= -1.0; }
	// Render-only 1 cm lift avoids z-fighting; evidence retains the exact receiving surface.
	Marker->SetWorldLocationAndRotation(Point.WorldPosition + Normal, Normal.Rotation());
}

void ADYStaffProjectionProbe::RefreshProjection()
{
#if !UE_BUILD_SHIPPING
	LastCapture = UDYStaffProjectionLibrary::CaptureStaffProjection(Light, Puppet,
		IsValid(ScreenActor) ? ScreenActor->GetStaticMeshComponent() : nullptr);
	UpdateMarker(MarkerA, LastCapture.EndA);
	UpdateMarker(MarkerB, LastCapture.EndB);
	Readout->SetVisibility(true);
	Readout->SetText(FText::FromString(FString::Printf(
		TEXT("DEV geometry only - NOT P03 success\nA = local -Z, B = local +Z\nA status=%d  B status=%d"),
		static_cast<int32>(LastCapture.EndA.Status), static_cast<int32>(LastCapture.EndB.Status))));
#endif
}
