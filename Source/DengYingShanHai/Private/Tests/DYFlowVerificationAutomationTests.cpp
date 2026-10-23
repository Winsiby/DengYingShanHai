#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Core/DYDevEntryPlayerController.h"

struct FDYFlowVerifyTestSeam
{
    static bool Complete(uint32 Steps, uint32 Shows, bool Walked)
    {
        return ADYDevEntryPlayerController::FlowVerificationHasCompleteEvidence(Steps, Shows, Walked);
    }
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYFlowVerificationEvidenceTest,
    "DengYingShanHai.EntryLoop.FlowVerificationRequiresWholeCampaign",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter)
bool FDYFlowVerificationEvidenceTest::RunTest(const FString& Parameters)
{
    TestTrue(TEXT("All twelve steps, four real shows, and the real entrance crossing qualify"),
        FDYFlowVerifyTestSeam::Complete(0xFFF, 0xF, true));
    for (uint32 MissingStep = 0; MissingStep < 12; ++MissingStep)
    {
        TestFalse(FString::Printf(TEXT("Missing step %u must prevent a gameplay pass"), MissingStep),
            FDYFlowVerifyTestSeam::Complete(0xFFF & ~(1u << MissingStep), 0xF, true));
    }
    for (uint32 MissingShow = 0; MissingShow < 4; ++MissingShow)
    {
        TestFalse(FString::Printf(TEXT("Missing real chapter show %u must prevent a pass"), MissingShow),
            FDYFlowVerifyTestSeam::Complete(0xFFF, 0xF & ~(1u << MissingShow), true));
    }
    TestFalse(TEXT("Skipping the physical entrance walk is incomplete"),
        FDYFlowVerifyTestSeam::Complete(0xFFF, 0xF, false));
    TestFalse(TEXT("An empty fixture cannot qualify"), FDYFlowVerifyTestSeam::Complete(0, 0, false));
    return true;
}
#endif