#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "UI/DYInteractionHUDWidget.h"

namespace DYChapterCardTests
{
	constexpr EAutomationTestFlags TestFlags =
		EAutomationTestFlags::EditorContext |
		EAutomationTestFlags::EngineFilter;

	FDYActSequenceSnapshot MakeSnapshot(const int32 ChapterIndex, const int32 ChapterCount, const TCHAR* Title, const bool bEnabled = true)
	{
		FDYActSequenceSnapshot Snapshot;
		Snapshot.bSequenceEnabled = bEnabled;
		Snapshot.ChapterIndex = ChapterIndex;
		Snapshot.ChapterCount = ChapterCount;
		Snapshot.ChapterTitle = FText::FromString(Title);
		return Snapshot;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYChapterCardTest,
	"DengYingShanHai.M1.UI.ChapterCard",
	DYChapterCardTests::TestFlags)

bool FDYChapterCardTest::RunTest(const FString& Parameters)
{
	using namespace DYChapterCardTests;

	// 四幕 campaign：第一次看到某一幕就出题签，题签文字就是幕名。
	const FDYActSequenceSnapshot Second = MakeSnapshot(1, 4, TEXT("Chapter Two"));
	TestTrue(TEXT("First sight of chapter 2 shows the card"),
		UDYInteractionHUDWidget::ShouldShowChapterCard(Second, INDEX_NONE));
	TestEqual(TEXT("Card text is the chapter title"),
		UDYInteractionHUDWidget::MakeChapterCardText(Second).ToString(), FString(TEXT("Chapter Two")));

	// 同一幕重复下发快照时不再重复出题签。
	TestFalse(TEXT("The same chapter never re-shows the card"),
		UDYInteractionHUDWidget::ShouldShowChapterCard(Second, 1));

	// 下一幕是新一轮题签。
	TestTrue(TEXT("The next chapter shows a new card"),
		UDYInteractionHUDWidget::ShouldShowChapterCard(MakeSnapshot(2, 4, TEXT("Chapter Three")), 1));

	// 单幕夹具与开发序列：没有章可题，保持原来的步骤标题。
	TestFalse(TEXT("A single-chapter sequence never shows a card"),
		UDYInteractionHUDWidget::ShouldShowChapterCard(MakeSnapshot(0, 1, TEXT("Chapter One")), INDEX_NONE));
	TestTrue(TEXT("A single-chapter sequence has no card text"),
		UDYInteractionHUDWidget::MakeChapterCardText(MakeSnapshot(0, 1, TEXT("Chapter One"))).IsEmpty());

	// 边界：序列关闭、章节索引无效、幕名为空，都不该出题签。
	TestFalse(TEXT("A disabled sequence never shows a card"),
		UDYInteractionHUDWidget::ShouldShowChapterCard(MakeSnapshot(1, 4, TEXT("Chapter Two"), false), INDEX_NONE));
	TestFalse(TEXT("An invalid chapter index never shows a card"),
		UDYInteractionHUDWidget::ShouldShowChapterCard(MakeSnapshot(-1, 4, TEXT("Chapter Two")), INDEX_NONE));
	TestFalse(TEXT("An empty chapter title never shows a card"),
		UDYInteractionHUDWidget::ShouldShowChapterCard(MakeSnapshot(1, 4, TEXT("")), INDEX_NONE));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
