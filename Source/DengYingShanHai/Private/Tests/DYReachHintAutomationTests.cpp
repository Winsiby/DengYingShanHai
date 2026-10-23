#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Puzzles/DYPuzzleDirector.h"

namespace DYReachHintTests
{
	constexpr EAutomationTestFlags TestFlags =
		EAutomationTestFlags::EditorContext |
		EAutomationTestFlags::EngineFilter;
}

/**
 * The reach hint is cosmetic guidance only: it must never gate evaluation, and it
 * must stay silent whenever the player already stands where every part this act
 * needs can be reached. MakeReachHint is pure (no world access) so the copy and the
 * silence conditions can be asserted directly.
 */
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FDYReachHintCopyTest,
	"DengYingShanHai.M1.Puzzle.ReachHintCopy",
	DYReachHintTests::TestFlags)

bool FDYReachHintCopyTest::RunTest(const FString& Parameters)
{
	// Light-only act, lamp in reach: nothing to say.
	TestTrue(
		TEXT("A reachable lamp with no puppet gate stays silent"),
		ADYPuzzleDirector::MakeReachHint(true, false, false).IsEmpty());

	// Light-only act, lamp out of reach: point the player at the lamp only.
	const FText LightOnly = ADYPuzzleDirector::MakeReachHint(false, false, false);
	TestFalse(TEXT("An unreachable lamp produces a hint"), LightOnly.IsEmpty());
	TestTrue(
		TEXT("The light-only hint talks about the lamp"),
		LightOnly.ToString().Contains(TEXT("\u706f")));

	// Two-part act, both parts in reach: silent.
	TestTrue(
		TEXT("Reachable lamp and puppet stay silent"),
		ADYPuzzleDirector::MakeReachHint(true, true, true).IsEmpty());

	// Two-part act, either part out of reach: the middle-of-both hint, never the
	// light-only copy, because the player has two things to line up.
	const FText Both = ADYPuzzleDirector::MakeReachHint(false, true, true);
	const FText PuppetMissing = ADYPuzzleDirector::MakeReachHint(true, true, false);
	TestFalse(TEXT("A missing lamp produces a hint"), Both.IsEmpty());
	TestFalse(TEXT("A missing puppet produces a hint"), PuppetMissing.IsEmpty());
	TestFalse(TEXT("The two-part hint is not the light-only copy"), Both.EqualTo(LightOnly));
	TestTrue(TEXT("Both two-part cases share the same copy"), Both.EqualTo(PuppetMissing));
	TestTrue(
		TEXT("The two-part hint names both parts"),
		Both.ToString().Contains(TEXT("\u706f")) && Both.ToString().Contains(TEXT("\u5076")));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
