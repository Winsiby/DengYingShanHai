#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "DYPuppetPerformanceTypes.generated.h"

class UAnimSequence;

/** One authored beat of the shadow-puppet performance. Cosmetic only: never puzzle judgement. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYPerformanceSegment
{
	GENERATED_BODY()

	/** Clip played on the active puppet mesh. Empty keeps the current pose and only shows the caption. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance")
	TSoftObjectPtr<UAnimSequence> Animation;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance", meta = (ClampMin = "0.2", ClampMax = "20.0", Units = "s"))
	float Seconds = 2.0f;

	/** Bottom-plaque caption. Empty shows nothing for this beat. Plain string so the data asset is
	 *  authorable from tools (UE Python has no FText constructor). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance")
	FString Caption;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance")
	bool bLoop = true;
};

/** One chapter (one act of the four-act campaign) of the shadow-puppet performance. */
USTRUCT(BlueprintType)
struct DENGYINGSHANHAI_API FDYActPerformance
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance")
	int32 ChapterIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance")
	FString ActTitle;

	/** Continuous show played once the final puzzle of the chapter resolves. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance")
	TArray<FDYPerformanceSegment> Segments;

	/** Short reaction clips fired while the player is still manipulating this chapter's act. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance")
	TArray<FDYPerformanceSegment> Feedback;
};

UCLASS(BlueprintType)
class DENGYINGSHANHAI_API UDYPuppetPerformanceData : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Performance")
	TArray<FDYActPerformance> Acts;

	const FDYActPerformance* FindAct(int32 ChapterIndex) const;
	float GetDurationSeconds(int32 ChapterIndex) const;
};
