#pragma once

#include "CoreMinimal.h"

/**
 * Shared entry-walk geometry. Lives in its own header so the entry controller and the
 * puzzle director agree on where the theater interior begins; duplicating the number in
 * two translation units is how the walk guidance and the stage reach guidance drift apart.
 */
namespace DYEntryWalk
{
	/** Theater interior floor starts behind the rear gate wall; the gate itself sits at X = -1800. */
	inline constexpr double TheaterThresholdX = -1700.0;
}
