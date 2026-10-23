#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Interaction/DYPuppetActor.h"
#include "Interaction/DYPuppetControlComponent.h"
#include "UObject/StrongObjectPtr.h"

namespace DYCastTests
{
 constexpr EAutomationTestFlags Flags = EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter;
 struct FWorld
 {
  UWorld* World = nullptr;
  TStrongObjectPtr<UWorld> Strong;
  ADYPuppetActor* Puppet = nullptr;
  FWorld()
  {
   World=UWorld::CreateWorld(EWorldType::Game,false);Strong.Reset(World);
   if(World && GEngine)
   {
    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
    World->InitializeActorsForPlay(FURL());
    Puppet=World->SpawnActor<ADYPuppetActor>();
   }
  }
  ~FWorld()
  {
   if(World && GEngine){World->EndPlay(EEndPlayReason::Quit);GEngine->DestroyWorldContext(World);World->DestroyWorld(false);}
   Strong.Reset();
  }
 };
 void Pose(ADYPuppetActor& Puppet,double Value)
 {
  Puppet.GetPuppetControlComponent()->SetNormalizedValue(Value);
  Puppet.ApplyPoseAnimation(Puppet.GetPoseId());
  if(USkeletalMeshComponent* Mesh=Puppet.GetActivePuppetMesh())
  {Mesh->TickAnimation(0.f,false);Mesh->RefreshBoneTransforms();}
 }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYCastActualBones,"DengYingShanHai.Presentation.Cast.ActualPoseBones",DYCastTests::Flags)
bool FDYCastActualBones::RunTest(const FString&)
{
 DYCastTests::FWorld F;
 if(!TestNotNull(TEXT("Puppet fixture"),F.Puppet)){return false;}
 for(int32 Chapter=1;Chapter<=2;++Chapter)
 {
  F.Puppet->ApplyChapterFigure(Chapter,true);
  USkeletalMeshComponent* Mesh=F.Puppet->GetActivePuppetMesh();
  if(!TestNotNull(TEXT("Imported chapter mesh"),Mesh)){return false;}
  TestEqual(TEXT("Fresh cast uses a single-node instance"),Mesh->GetAnimationMode(),EAnimationMode::AnimationSingleNode);
  const FName Bone=Chapter==1 ? FName(TEXT("WingL_Upper")) : FName(TEXT("Arm_L_Upper"));
  TestTrue(TEXT("Authored joint exists"),Mesh->GetBoneIndex(Bone)!=INDEX_NONE);
  DYCastTests::Pose(*F.Puppet,.15);
  UAnimSingleNodeInstance* Instance=Mesh->GetSingleNodeInstance();
  if(!TestNotNull(TEXT("Actual animation instance"),Instance)){return false;}
  UAnimationAsset* Rest=Instance->GetAnimationAsset();
  const FTransform RestJoint=Mesh->GetSocketTransform(Bone,RTS_Component);
  DYCastTests::Pose(*F.Puppet,.5);
  TestTrue(TEXT("A second logical pose uses a different actual clip"),Rest!=Instance->GetAnimationAsset());
  TestFalse(TEXT("The imported joint really changes in component space"),RestJoint.Equals(Mesh->GetSocketTransform(Bone,RTS_Component),.001));
  Mesh->SetPosition(.4f,false);
  DYCastTests::Pose(*F.Puppet,.52);
  TestEqual(TEXT("Rail motion inside one pose does not rewind animation"),Mesh->GetPosition(),.4f);
 }
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDYCastZhulongDaylight,"DengYingShanHai.Presentation.Cast.ZhulongDaylightFact",DYCastTests::Flags)
bool FDYCastZhulongDaylight::RunTest(const FString&)
{
 DYCastTests::FWorld F;
 if(!TestNotNull(TEXT("Puppet fixture"),F.Puppet)){return false;}
 F.Puppet->ApplyChapterFigure(3,true);
 USkeletalMeshComponent* Mesh=F.Puppet->GetActivePuppetMesh();
 if(!TestNotNull(TEXT("Zhulong mesh"),Mesh)){return false;}
 F.Puppet->SetChapterDaylight(false);
 DYCastTests::Pose(*F.Puppet,.86);
 UAnimSingleNodeInstance* Instance=Mesh->GetSingleNodeInstance();
 if(!TestNotNull(TEXT("Actual Zhulong instance"),Instance)){return false;}
 TestTrue(TEXT("Night target position keeps the Night clip"),Instance->GetAnimationAsset()->GetName().EndsWith(TEXT("Night")));
 const float NightScale=Mesh->GetSocketTransform(TEXT("Eyelid"),RTS_Component).GetScale3D().GetMax();
 F.Puppet->SetChapterDaylight(true);
 DYCastTests::Pose(*F.Puppet,.86);
 TestTrue(TEXT("Solved daylight fact opens the eye"),Instance->GetAnimationAsset()->GetName().EndsWith(TEXT("Day")));
 const float DayScale=Mesh->GetSocketTransform(TEXT("Eyelid"),RTS_Component).GetScale3D().GetMax();
 TestTrue(TEXT("Real eyelid bone changes from covering the eye to retracted"),NightScale>.5f && DayScale<.01f);
 F.Puppet->SetChapterDaylight(false);
 DYCastTests::Pose(*F.Puppet,.86);
 TestTrue(TEXT("Resetting the daylight fact restores Night at the same rail value"),Instance->GetAnimationAsset()->GetName().EndsWith(TEXT("Night")));
 return true;
}
#endif