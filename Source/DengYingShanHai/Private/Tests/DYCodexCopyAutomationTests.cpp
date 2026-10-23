#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "UI/DYDevEntryWidget.h"

namespace DYCodexTests
{
	constexpr EAutomationTestFlags TestFlags =
		EAutomationTestFlags::EditorContext |
		EAutomationTestFlags::EngineFilter;

	// V2.3 的非遗清单：皮影造型、幕后操偶、制作七步、锣鼓器乐、通关后图鉴。
	// 正文是纯函数拼出来的，所以这五项可以直接断言，不必起 UMG。
	const TCHAR* const CodexWords[] = {
		TEXT("\u9020\u578b"),      // 造型
		TEXT("\u64cd\u6f14"),      // 操演
		TEXT("\u5236\u4f5c\u4e03\u6b65"),  // 制作七步
		TEXT("\u9523\u9f13"),      // 锣鼓
		TEXT("\u56fe\u9274"),      // 图鉴
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYCodexCopyTest,
	"DengYingShanHai.M1.UI.CodexCopy",
	DYCodexTests::TestFlags)

bool FDYCodexCopyTest::RunTest(const FString& Parameters)
{
	static const TCHAR* const Purposes[4] = {
		TEXT("\u6756"),            // 杖 (夸父落杖)
		TEXT("\u7fc5"),            // 翅 (精卫分节翅)
		TEXT("\u76fe"),            // 盾 (刑天盾影)
		TEXT("\u86c7"),            // 蛇 (烛龙人面蛇身)
	};
	for (int32 Index = 0; Index < 4; ++Index)
	{
		const FString Entry = UDYDevEntryWidget::MakeCodexEntry(Index);
		TestFalse(FString::Printf(TEXT("Codex %d is not empty"), Index), Entry.IsEmpty());
		for (const TCHAR* Word : DYCodexTests::CodexWords)
		{
			if (!Entry.Contains(Word))
			{
				AddError(FString::Printf(TEXT("Codex %d is missing %s"), Index, Word));
			}
		}
		if (!Entry.Contains(Purposes[Index]))
		{
			AddError(FString::Printf(TEXT("Codex %d does not name its own puppet"), Index));
		}
	}
	// 越界索引落在同一具影偶上，不崩、不空。
	TestEqual(
		TEXT("Out-of-range index clamps onto the last puppet"),
		UDYDevEntryWidget::MakeCodexEntry(9),
		UDYDevEntryWidget::MakeCodexEntry(3));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
