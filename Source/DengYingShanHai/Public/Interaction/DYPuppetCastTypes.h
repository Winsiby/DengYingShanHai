#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "DYPuppetCastTypes.generated.h"

class USkeletalMesh;
class UAnimSequence;

/** One chapter's puppet appearance: mesh, per-pose stance clips and the operator props that belong to it. */
USTRUCT(BlueprintType)
struct FDYPuppetFigureEntry
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet")
	FString Label;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet")
	TSoftObjectPtr<USkeletalMesh> SkeletalMesh;

	/** Pose ID from the puppet control rail to a one-second authored stance. NAME_None is the idle stance. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet")
	TMap<FName, TSoftObjectPtr<UAnimSequence>> PoseAnimations;

	/** Only the Kuafu figure carries the separate staff; puppets with baked control rods hide it. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet")
	bool bHideStaff = true;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet")
	FVector MeshRelativeLocation = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet")
	FRotator MeshRelativeRotation = FRotator::ZeroRotator;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet")
	FVector MeshRelativeScale = FVector::OneVector;
};

/** Ordered per-chapter cast, index 0 is chapter one. Appearance only: puzzle judgement stays in the Director. */
UCLASS(BlueprintType)
class DENGYINGSHANHAI_API UDYPuppetCastData : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "DY|Puppet")
	TArray<FDYPuppetFigureEntry> Figures;
};
