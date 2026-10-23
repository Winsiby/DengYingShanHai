#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interaction/DYControllable.h"
#include "Interaction/DYStaffGeometryTypes.h"
#include "DYPuppetActor.generated.h"

class USceneComponent;
class UStaticMeshComponent;
class UDYPuppetControlComponent;
class UDYPuppetCastData;
class USkeletalMeshComponent;
class UDYPuppetPerformanceComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FDYPuppetResetRequestedSignature);

/** Shadow-casting puppet shell whose reusable control capability is enabled per puzzle. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYPuppetActor : public AActor, public IDYControllable
{
	GENERATED_BODY()

public:
	ADYPuppetActor();

	UFUNCTION(BlueprintPure, Category = "DY|Puppet")
	FName GetPoseId() const;

	/** Reads mesh bounds and the full component transform; never changes control or pose. */
	UFUNCTION(BlueprintPure, Category = "DY|Puppet")
	FDYStaffGeometrySnapshot GetStaffGeometrySnapshot() const;

	/** Swaps the visible puppet to the figure authored for this campaign chapter. Appearance only. */
	UFUNCTION(BlueprintCallable, Category = "DY|Puppet")
	void ApplyChapterFigure(int32 ChapterIndex, bool bForce = false);

	/** Cosmetic daylight fact supplied by the current chapter presentation, never puzzle judgement. */
	UFUNCTION(BlueprintCallable, Category = "DY|Puppet")
	void SetChapterDaylight(bool bDaylight);

	/** Plays the authored stance clip mapped to this pose ID, if the active figure has one. */
	UFUNCTION(BlueprintCallable, Category = "DY|Puppet")
	void ApplyPoseAnimation(FName PoseId);

	UFUNCTION(BlueprintPure, Category = "DY|Puppet")
	int32 GetActiveFigureIndex() const { return ActiveFigureIndex; }

	/** Skeletal mesh currently carrying the visible puppet; the performance plays on it. */
	USkeletalMeshComponent* GetActivePuppetMesh() const;

	UDYPuppetPerformanceComponent* GetPerformanceComponent() const { return Performance; }

	UDYPuppetControlComponent* GetPuppetControlComponent() const { return PuppetControl; }

	virtual bool CanBeginControl_Implementation(const FDYControlContext& Context) const override;
	virtual void BeginControl_Implementation(const FDYControlContext& Context) override;
	virtual void ApplyControlIntent_Implementation(const FDYControlIntent& Intent) override;
	virtual void EndControl_Implementation(const FDYControlContext& Context) override;
	virtual void ResetControlState_Implementation(const FDYControlContext& Context) override;
	virtual void SetControlEnabled_Implementation(bool bEnabled) override;
	virtual FDYControlSnapshot GetControlSnapshot_Implementation() const override;

	UPROPERTY(BlueprintAssignable, Category = "DY|Puppet")
	FDYPuppetResetRequestedSignature OnResetRequested;

protected:
	virtual void BeginPlay() override;

private:
	UFUNCTION()
	void HandleControlChanged(double NormalizedValue, FName NewPoseId);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> Torso;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> Head;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> Staff;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UDYPuppetControlComponent> PuppetControl;

	/** Authored act-show playback. Presentation only; the puzzle Director owns the sequencing. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UDYPuppetPerformanceComponent> Performance;

	/** Optional explicit cast. When unset the shipped cast is loaded from the project content path. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UDYPuppetCastData> FigureCast;

	UPROPERTY(Transient)
	TObjectPtr<USkeletalMeshComponent> FigureMesh;

	UPROPERTY(Transient)
	int32 ActiveFigureIndex = INDEX_NONE;

	/** Dedicated display component for chapter figures with baked pose clips. Keeping it
	 *  separate leaves the Blueprint's Kuafu mesh and its animation logic untouched. */
	UPROPERTY(Transient)
	TObjectPtr<USkeletalMeshComponent> CastMesh;

	bool bChapterDaylight = false;

	void ResolveFigureCast();
};