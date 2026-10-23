#pragma once

#include "CoreMinimal.h"
#include "DYStageFeedbackTypes.generated.h"

/**
 * Purely presentational state for player UI and the compatible Dev readout.
 *
 * This enum deliberately does NOT reuse EDYPuzzleFeedbackState:
 *  - puzzle feedback answers "how close is the current sample", and it has no
 *    notion of an interruption, because the Director re-evaluates every sample;
 *  - the Dev readout must be able to hold a transient "interrupted" on screen even
 *    while later samples keep arriving, so it needs its own baseline/override split.
 *
 * It carries no target value, no tolerance and no progress, so nothing here can
 * leak the answer to the player.
 */
UENUM(BlueprintType)
enum class EDYStageFeedbackDisplay : uint8
{
	/** No puzzle is active yet, or the readout is not applicable. */
	Hidden,

	/** Puzzle is active, the current sample is not close to any condition. */
	Adjust,

	/** Puzzle is active and the current sample is close to at least one condition. */
	Near,

	/** Every required condition currently holds and the hold timer is running. */
	Holding,

	/**
	 * Transient override: the hold was interrupted. The Presentation owns a one-shot
	 * timer and restores the baseline when it expires.
	 */
	Interrupted,

	/** The puzzle resolved. */
	Complete
};

/** Cosmetic projection of existing evaluation, never current/target/tolerance or overlap score. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYPlayerAlignmentDisplay
{
	GENERATED_BODY()
	UPROPERTY(BlueprintReadOnly, Category="DY|Player Feedback") bool bEnabled = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Player Feedback") bool bHasValidSample = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Player Feedback") bool bLightRequired = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Player Feedback") bool bLightReady = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Player Feedback") bool bPuppetRequired = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Player Feedback") bool bPuppetReady = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Player Feedback") bool bJointReady = false;
	UPROPERTY(BlueprintReadOnly, Category="DY|Player Feedback") bool bHolding = false;
	/** Existing hold-clock fraction, NOT pixel similarity or puzzle Progress. */
	UPROPERTY(BlueprintReadOnly, Category="DY|Player Feedback") double HoldFraction = 0.0;

	bool operator==(const FDYPlayerAlignmentDisplay& Other) const
	{
		return bEnabled == Other.bEnabled && bHasValidSample == Other.bHasValidSample
			&& bLightRequired == Other.bLightRequired && bLightReady == Other.bLightReady
			&& bPuppetRequired == Other.bPuppetRequired && bPuppetReady == Other.bPuppetReady
			&& bJointReady == Other.bJointReady && bHolding == Other.bHolding && HoldFraction == Other.HoldFraction;
	}
};

/**
 * Whether a world package belongs to the Dev content tree.
 *
 * The legacy Dev getter/readout is gated on this; public player UI is not.
 * UE's PIE prefix is added
 * to the map's short name, leaving its content directory unchanged.
 */
FORCEINLINE bool IsDevContentPackage(const FString& PackageName)
{
	return PackageName.StartsWith(TEXT("/Game/DengYingShanHai/Dev/"), ESearchCase::CaseSensitive);
}
