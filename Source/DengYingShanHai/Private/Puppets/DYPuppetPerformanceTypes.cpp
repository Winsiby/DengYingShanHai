#include "Puppets/DYPuppetPerformanceTypes.h"

const FDYActPerformance* UDYPuppetPerformanceData::FindAct(int32 ChapterIndex) const
{
	return Acts.FindByPredicate([ChapterIndex](const FDYActPerformance& Act)
	{
		return Act.ChapterIndex == ChapterIndex;
	});
}

float UDYPuppetPerformanceData::GetDurationSeconds(int32 ChapterIndex) const
{
	const FDYActPerformance* Act = FindAct(ChapterIndex);
	if (!Act) { return 0.f; }

	float Total = 0.f;
	for (const FDYPerformanceSegment& Segment : Act->Segments)
	{
		Total += FMath::Max(0.f, Segment.Seconds);
	}
	return Total;
}
