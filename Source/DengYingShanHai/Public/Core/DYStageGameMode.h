#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "DYStageGameMode.generated.h"

class ADYStagePresentation;

// Native multicast: HUD adapters bind from C++, and a dynamic delegate would require
// a UFUNCTION reflection target. No Blueprint operation is exposed.
DECLARE_MULTICAST_DELEGATE_OneParam(FDYStagePresentationRegisteredSignature, ADYStagePresentation*);

/**
 * Minimal game-mode boundary for the stage experience.
 * Puzzle state and presentation orchestration intentionally do not live here.
 *
 * The GameMode only introduces the explicit cosmetic Presentation of
 * this world plus a register/unregister notification. It never decides puzzle truth
 * and never scans the world for actors.
 */
UCLASS()
class DENGYINGSHANHAI_API ADYStageGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ADYStageGameMode();

	/** Formal main world opts into the V2.2 entry menu; other worlds keep the plain stage controller. */
	virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;

	/**
	 * Legacy Dev getter: null outside the Dev tree or in Shipping.
	 * Public player views use GetPlayerStagePresentation instead.
	 */
	UFUNCTION(BlueprintPure, Category = "DY|Stage Game Mode")
	ADYStagePresentation* GetStagePresentation() const;

	/** Public cosmetic registration, available in all runtime builds. No puzzle answers. */
	UFUNCTION(BlueprintPure, Category = "DY|Stage Game Mode")
	ADYStagePresentation* GetPlayerStagePresentation() const { return StagePresentation.Get(); }

	/** Fired when a Presentation registers itself, and again with null when it leaves. */
	FDYStagePresentationRegisteredSignature OnStagePresentationChanged;

	/** Called by the Presentation from its own BeginPlay/EndPlay. */
	void RegisterStagePresentation(ADYStagePresentation* InPresentation);
	void UnregisterStagePresentation(ADYStagePresentation* InPresentation);

private:
	/**
	 * Runtime-only registration target. It is deliberately NOT EditInstanceOnly: the
	 * binding is established by the Presentation itself during play, never authored in
	 * the editor, so exposing it as editable would let it desync from the real actor.
	 */
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Transient, Category = "DY|Stage Game Mode", meta = (AllowPrivateAccess = "true"))
	TWeakObjectPtr<ADYStagePresentation> StagePresentation;
};
