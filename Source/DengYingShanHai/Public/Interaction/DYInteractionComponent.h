#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "DYInteractionComponent.generated.h"

class AActor;
class APawn;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FDYFocusChangedSignature, AActor*, PreviousActor, AActor*, NewActor);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FDYControlStateChangedSignature, AActor*, ControlledActor, bool, bIsControlling);

#if WITH_DEV_AUTOMATION_TESTS
struct FDYFocusAutomationSeam;
#endif

#if !UE_BUILD_SHIPPING
/**
 * 聚焦诊断状态。纯 C++、非反射，只在非 Shipping 构建中存在。
 * 只观察聚焦流程，永不参与判定。Shipping 下不存在任何可开启的调试属性或 API。
 *
 * 这里只保存「本次求值」的观察结果；日志节流所需的「上次已输出」状态是
 * 独立的成员，不存放在本结构体内，避免刷新快照时被一并重置。
 */
struct FDYFocusDebugState
{
	FVector ViewLocation = FVector::ZeroVector;
	FVector PawnLocation = FVector::ZeroVector;
	FVector TraceEnd = FVector::ZeroVector;
	double TraceLength = 0.0;
	TWeakObjectPtr<AActor> HitActor;
	TWeakObjectPtr<AActor> FocusedActor;
	bool bControllable = false;
	bool bWithinReach = false;
	bool bCanBeginControl = false;
	double PawnToCandidateDistance = 0.0;
	FName RejectReason;
};
#endif

UCLASS(ClassGroup = (DY), meta = (BlueprintSpawnableComponent))
class DENGYINGSHANHAI_API UDYInteractionComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UDYInteractionComponent();

	UFUNCTION(BlueprintCallable, Category = "DY|Interaction")
	bool ToggleControl();

	UFUNCTION(BlueprintCallable, Category = "DY|Interaction")
	void EndActiveControl();

	UFUNCTION(BlueprintCallable, Category = "DY|Interaction")
	void ApplyPrimaryAxis(double AxisValue, double DeltaSeconds);

	UFUNCTION(BlueprintCallable, Category = "DY|Interaction")
	bool ResetActiveControl();

	UFUNCTION(BlueprintPure, Category = "DY|Interaction")
	AActor* GetFocusedActor() const { return FocusedActor.Get(); }

	UFUNCTION(BlueprintPure, Category = "DY|Interaction")
	AActor* GetActiveControlledActor() const { return ActiveControlledActor.Get(); }

	UFUNCTION(BlueprintPure, Category = "DY|Interaction")
	bool IsControlling() const { return ActiveControlledActor.IsValid(); }

	/**
	 * 角色到交互物的真实最大可交互半径，单位为厘米。
	 * 该值只描述角色半径，不代表相机射线长度。
	 */
	UFUNCTION(BlueprintPure, Category = "DY|Interaction")
	double GetFocusDistance() const { return FocusDistance; }

	/**
	 * 从相机视点出发时，为覆盖角色 FocusDistance 球内全部候选对象所需的射线长度。
	 *
	 * 第三人称相机位于角色之后，固定长度的射线会在角色仍处于交互半径内时提前耗尽，
	 * 因此射线长度必须补偿「相机到角色」的偏移。该长度为三角不等式给出的安全上界：
	 * 角色 FocusDistance 球内任意点到相机的距离都不超过此值，故不会漏掉合法候选。
	 * 纯函数，不访问世界，供自动化测试直接验证。
	 */
	static double ComputeFocusTraceLength(
		const FVector& ViewLocation,
		const FVector& PawnLocation,
		double InFocusDistance);

	/**
	 * 命中后的唯一准入门控：候选对象到角色的距离必须不超过 FocusDistance。
	 * 射线负责遮挡语义，本门控负责半径语义，两者职责不合并。
	 * 纯函数，不访问世界，供自动化测试直接验证。
	 */
	static bool IsWithinFocusDistance(
		const FVector& PawnLocation,
		const FVector& CandidateLocation,
		double InFocusDistance);

	UPROPERTY(BlueprintAssignable, Category = "DY|Interaction")
	FDYFocusChangedSignature OnFocusChanged;

	UPROPERTY(BlueprintAssignable, Category = "DY|Interaction")
	FDYControlStateChangedSignature OnControlStateChanged;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYFocusAutomationSeam;
#endif

private:
	/**
	 * 唯一的聚焦判定实现：trace → 接口检查 → 半径门控 → CanBeginControl → SetFocusedActor。
	 * UpdateFocusedActor 取得视点后调用它；自动化测试通过 friend seam 调用同一个函数，
	 * 因此测试验证的是生产逻辑本身，而不是测试内的副本。
	 * 非反射、不暴露给 Blueprint。
	 */
	void EvaluateFocus(
		const FVector& ViewLocation,
		const FRotator& ViewRotation,
		const FVector& PawnLocation);

	void UpdateFocusedActor();
	void SetFocusedActor(AActor* NewFocusedActor);
	APawn* GetOwnerPawn() const;

	UPROPERTY(EditAnywhere, Category = "DY|Interaction", meta = (ClampMin = "50.0", Units = "cm"))
	double FocusDistance = 700.0;

	UPROPERTY(EditAnywhere, Category = "DY|Interaction", meta = (ClampMin = "0.02", Units = "s"))
	double FocusRefreshInterval = 0.10;

	TWeakObjectPtr<AActor> FocusedActor;
	TWeakObjectPtr<AActor> ActiveControlledActor;
	FTimerHandle FocusTimerHandle;

#if !UE_BUILD_SHIPPING
	/** Observes one evaluation. Draws a trace and logs only on a real change. */
	void PublishFocusDebug(const FDYFocusDebugState& State);

	/** Opt-in switch, parsed from the same -DYDebug flag the Puzzle Director uses. */
	bool bFocusDebugEnabled = false;

	/** Latest observed evaluation. Overwritten every pass; carries no log history. */
	FDYFocusDebugState FocusDebugState;

	/**
	 * What was actually written to the log last time. Kept apart from
	 * FocusDebugState so refreshing the observation cannot reset the throttle.
	 */
	TWeakObjectPtr<AActor> LastLoggedHitActor;
	TWeakObjectPtr<AActor> LastLoggedFocusedActor;
	FName LastLoggedRejectReason = NAME_None;
	bool bHasLoggedFocus = false;
#endif
};

#if WITH_DEV_AUTOMATION_TESTS
/**
 * Automation-only seam. Lets the focus test drive the real private evaluation helper
 * without adding any public, reflected or Blueprint-callable entry point.
 */
struct FDYFocusAutomationSeam
{
	static void EvaluateFocus(
		UDYInteractionComponent& Component,
		const FVector& ViewLocation,
		const FRotator& ViewRotation,
		const FVector& PawnLocation);
};
#endif
