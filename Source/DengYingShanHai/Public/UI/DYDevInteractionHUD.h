#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "Stage/DYStageFeedbackTypes.h"
#include "DYDevInteractionHUD.generated.h"

class ADYStageOperatorPawn;
class ADYStageGameMode;
class ADYStagePresentation;
class UDYInteractionComponent;

/**
 * Development-only interaction readout.
 *
 * It answers exactly one question the current build cannot: "is the thing under the
 * crosshair interactive right now?". To do that it only reads the two states the
 * interaction component already exposes - GetFocusedActor() and IsControlling().
 *
 * It deliberately does NOT:
 * - scan the world or keep any actor list of its own;
 * - re-implement focus, radius or occlusion gating;
 * - drive the camera, the view target or the pawn;
 * - depend on DebugFont, a Widget Blueprint, a plugin or any project asset.
 *
 * The formal art UI replaces this class later; until then it is the only place that
 * turns interaction state into something the player can see.
 */
UCLASS()
class DENGYINGSHANHAI_API ADYDevInteractionHUD : public AHUD
{
	GENERATED_BODY()

public:
	ADYDevInteractionHUD();

	virtual void DrawHUD() override;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	/** Binds to (or reads) whichever Presentation the GameMode currently exposes. */
	void AttachToPresentation(ADYStagePresentation* InPresentation);

	/** Drops the current binding and hides the Dev status line. */
	void DetachFromPresentation();

	/** GameMode registration hook; a null Presentation means "unregistered". */
	void HandlePresentationChanged(ADYStagePresentation* InPresentation);

	/** Native multicast sink; only receives the snapshot, never queries puzzle state. */
	void HandleFeedbackDisplayChanged(EDYStageFeedbackDisplay NewDisplay);

	/** Dev map gate: the status line exists only inside the Dev content tree. */
	bool IsDevContentWorld() const;

	/** ASCII placeholder text for a display state; empty when nothing should be shown. */
	static const TCHAR* GetPlaceholderText(EDYStageFeedbackDisplay Display);

	/** Resolves the operator's interaction component. Read-only, cached per frame. */
	UDYInteractionComponent* ResolveInteractionComponent() const;

	/** Draws the centre crosshair; green only when a candidate can actually be taken. */
	void DrawCentreCrosshair(bool bHasCandidate, bool bIsControlling);

	/** Draws the short contextual prompt line under the crosshair. */
	void DrawInteractionPrompt(bool bHasCandidate, bool bIsControlling);

	/** Draws the Dev status line below the interaction prompt. */
	void DrawDevStatusLine();

	/**
	 * Cached snapshot. The HUD only ever writes this from the Presentation callback and
	 * only ever reads it while drawing; it never reads the Director, the Evaluator, a
	 * definition, a target, a tolerance or a normalized position.
	 */
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Transient, Category = "DY|Interaction|Dev", meta = (AllowPrivateAccess = "true"))
	EDYStageFeedbackDisplay CachedFeedbackDisplay = EDYStageFeedbackDisplay::Hidden;

	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Transient, Category = "DY|Interaction|Dev", meta = (AllowPrivateAccess = "true"))
	TWeakObjectPtr<ADYStagePresentation> BoundPresentation;

	/** Handle of the GameMode's registration delegate, so EndPlay can remove it. */
	FDelegateHandle PresentationChangedHandle;
	TWeakObjectPtr<ADYStageGameMode> BoundGameMode;
	void BindToGameMode(ADYStageGameMode* GameMode);
	void UnbindGameMode();

#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYStageFeedbackTestSeam;
#endif
};
