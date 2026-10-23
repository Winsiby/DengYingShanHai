#include "Core/DYReleaseEntryPlayerController.h"

#include "Engine/World.h"

namespace DYReleaseEntry
{
	static const TCHAR* MainMap = TEXT("/Game/DengYingShanHai/Maps/L_DY_Main");
}

FName ADYReleaseEntryPlayerController::ResolveReleaseEntryMapName(
	const FString& PackageName, const EWorldType::Type WorldType)
{
	if (WorldType != EWorldType::Game && WorldType != EWorldType::PIE) { return NAME_None; }
	const FString Canonical = UWorld::RemovePIEPrefix(PackageName);
	return Canonical == DYReleaseEntry::MainMap ? FName(DYReleaseEntry::MainMap) : NAME_None;
}

FName ADYReleaseEntryPlayerController::GetCurrentDevEntryMap() const
{
	const UWorld* World = GetWorld();
	return World ? ResolveReleaseEntryMapName(World->GetOutermost()->GetName(), World->WorldType) : NAME_None;
}
