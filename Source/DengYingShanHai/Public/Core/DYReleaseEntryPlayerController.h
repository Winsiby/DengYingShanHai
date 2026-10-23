#pragma once

#include "CoreMinimal.h"
#include "Core/DYDevEntryPlayerController.h"
#include "DYReleaseEntryPlayerController.generated.h"

/** Reuses the existing entry loop; only the formal main-world identity differs. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYReleaseEntryPlayerController : public ADYDevEntryPlayerController
{
	GENERATED_BODY()

protected:
	virtual FName GetCurrentDevEntryMap() const override;

private:
	static FName ResolveReleaseEntryMapName(const FString& PackageName, EWorldType::Type WorldType);

#if WITH_DEV_AUTOMATION_TESTS
	friend struct FDYReleaseEntryTestSeam;
#endif
};
