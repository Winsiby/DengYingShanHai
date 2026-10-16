#include "Player/DYTheatreOperatorPawn.h"
#include "Player/DYFootstepAudioComponent.h"

ADYTheatreOperatorPawn::ADYTheatreOperatorPawn()
{
	FootstepAudio = CreateDefaultSubobject<UDYFootstepAudioComponent>(TEXT("FootstepAudio"));
}
