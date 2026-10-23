#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "UI/DYInteractionHUDWidget.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYChapterFinaleHUDText,
	"DengYingShanHai.UI.ChapterFinaleStatus",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDYChapterFinaleHUDText::RunTest(const FString&)
{
	FDYActSequenceSnapshot Snapshot;
	Snapshot.bSequenceEnabled = true;
	Snapshot.ActCount = 3;
	Snapshot.ActIndex = 2;
	Snapshot.ChapterCount = 4;
	Snapshot.Phase = EDYActSequencePhase::AwaitingFinale;
	const TCHAR* Expected[] = {
		TEXT("影形已合，静待杖落成林"),
		TEXT("石影已合，静待填海成洲"),
		TEXT("干戚已成，静待本幕落定"),
		TEXT("昼夜相合，静待四幕落定")
	};
	for (int32 Chapter = 0; Chapter < UE_ARRAY_COUNT(Expected); ++Chapter)
	{
		Snapshot.ChapterIndex = Chapter;
		const FString Actual = UDYInteractionHUDWidget::GetActStatusText(Snapshot, EDYStageFeedbackDisplay::Complete).ToString();
		TestEqual(FString::Printf(TEXT("Chapter %d has its own finale status"), Chapter + 1), Actual, FString(Expected[Chapter]));
		if (Chapter > 0) { TestFalse(TEXT("Later chapters never promise Kuafu's falling staff"), Actual.Contains(TEXT("杖落成林"))); }
	}
	Snapshot.ChapterIndex = INDEX_NONE;
	Snapshot.ChapterCount = 0;
	TestEqual(TEXT("Legacy single chapter retains its forest status"),
		UDYInteractionHUDWidget::GetActStatusText(Snapshot, EDYStageFeedbackDisplay::Complete).ToString(), FString(Expected[0]));
	Snapshot.Phase = EDYActSequencePhase::Complete;
	TestEqual(TEXT("Only completed campaign announces the ending"),
		UDYInteractionHUDWidget::GetActStatusText(Snapshot, EDYStageFeedbackDisplay::Complete).ToString(), FString(TEXT("复演已成")));
	return true;
}
#endif
