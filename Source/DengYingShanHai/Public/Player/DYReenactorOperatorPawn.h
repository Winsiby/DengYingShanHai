#pragma once

#include "CoreMinimal.h"
#include "Player/DYTheatreOperatorPawn.h"
#include "DYReenactorOperatorPawn.generated.h"

class UAnimInstance;
class USkeletalMesh;
class USkeletalMeshComponent;

/** Isolated Dev visual candidate. Movement, input, camera and interaction stay inherited. */
UCLASS(Blueprintable)
class DENGYINGSHANHAI_API ADYReenactorOperatorPawn : public ADYTheatreOperatorPawn
{
	GENERATED_BODY()

public:
	ADYReenactorOperatorPawn();

	virtual void BeginPlay() override;

	UFUNCTION(BlueprintPure, Category = "DY|Reenactor")
	bool HasReenactorVisual() const;

private:
	void HideLegacyPlaceholders();

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Reenactor", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<USkeletalMesh> ReenactorMeshAsset;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "DY|Reenactor", meta = (AllowPrivateAccess = "true"))
	TSubclassOf<UAnimInstance> ReenactorAnimClass;
};
