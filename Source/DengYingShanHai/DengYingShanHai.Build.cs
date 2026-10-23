using UnrealBuildTool;

public class DengYingShanHai : ModuleRules
{
	public DengYingShanHai(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"UMG"
		});
		PrivateDependencyModuleNames.Add("SlateCore");
		// FSlateApplication::Get() (keyboard-focus mirroring for the menu overlay rows) lives in Slate,
		// not SlateCore: without this the linker cannot resolve FSlateApplication::CurrentApplication.
		PrivateDependencyModuleNames.Add("Slate");
		// Human-readable OFL/copyright must accompany the embedded FontFace payload.
		RuntimeDependencies.Add("$(ProjectDir)/LICENSES/SourceHanSans/LICENSE.txt", StagedFileType.NonUFS);
	}
}
