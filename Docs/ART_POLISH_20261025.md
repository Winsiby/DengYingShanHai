> 当前状态补记：此文件以下保留D13刚构建时的历史交接，不代表当前入口状态。Run170已完成正式CMD入口实机截图与正常退出0，最新交付见 [ART_POLISH_DELIVERY_20261025.md](D:/灯影山海/Docs/ART_POLISH_DELIVERY_20261025.md) 和 [PUBLIC-ENTRY-SMOKE.json](D:/灯影山海/Saved/ArtPolish-2026-10-25/PUBLIC-ENTRY-SMOKE.json)。用户随后提出的门楼修复已独立交付Run171，详见 [GATE_REPAIR_20261025.md](D:/灯影山海/Docs/GATE_REPAIR_20261025.md)。

# 2026-10-25 美术修整阶段记录（历史节点）

状态：修改已保存，Development RunD13构建完成；修复后的字幕实图检查因物理Esc停止Computer Use而中断，正式Shipping入口尚未替换。不得把本轮写成全部发布完成。

## 已落实

1. 菜单完整视口不透明遮幅，保留插画ScaleToFit与按钮安全区。Run168的16:9/16:10实际图均无3D露底。
2. 演出HUD采用明确开始/结束/跳过/取消状态，收起准星、操作、题签、保持条；复用暗木底牌与纸色字幕；唯一字幕承载者优先原生HUD GetView。
3. 八张 ART_AUD_Bench_{0..3}_{L/R} 使用新增 M_DY_AudienceWood，复制现有PBR母材质，保留原贴图/法线/UV，局部低反光与高粗糙度。固定机位Before/Candidate逐图复核及独立复核均确认灰白亮条收敛。
4. 地图冷读/保存差异只包含八张凳材质引用，1806 Actor数量和全部变换、灯光不变。15枝成林、角色、动画、判定、轨道、容差和时长未动。
5. 两项旧夸父装配测试按UE实读当前地图和新建BP实例更新为完整精确路径检查，未放宽为任意非空。

## 最新验证

- Final Editor R4实际exit0；Automation RunD14为186通过/0失败。
- Development RunD13真实Build/Cook/Stage/Archive exit0，49文件全哈希复核，输入前后无漂移；与Run169只差PC演出态HUD根可见性例外。
- Run169在字幕根修复前已完成两轮完整四幕、真实Replay、正常退出，StepMasks=[4095,4095]，PerformanceMasks=[15,15]。其字幕视觉失败，不能作为新版本完整验收。
- Run168扩展直线步行测试碰到入口构件，walked0严格失败；该测试扩展已撤回，PlayerTick与本轮原备份逐字一致。失败证据保存。
- 首次隐藏菜单窗口取样无效，进程是任务自建隔离测试；后续可见窗口正常退出。无效取样明确排除。
- 最新D13字幕根修复：WBP_DYThreeActHUD本身派生UDYInteractionHUDWidget，PC按ThreeActHUD类名曾把整根藏起。现在仅演出态跳过对原生HUD的整根隐藏，原生HUD自行隐藏操作子控件，独立Cue仍收起。代码编译/全测通过，实际字幕仍待新图。

## 可查看入口与边界

D盘 Start-ArtPreview-Development.cmd 启动Development RunD13，保留地图/EXE身份校验、独立用户目录及实际退出记录。当前D13诊断窗口交还用户，不再自动发送输入。

公开 Start-ReleaseEntry-Shipping.cmd 仍指向旧Run167。由于主地图已按批准修改，旧入口的一致性检查会阻止启动；保护未关闭。不要把未通过视觉的Run169切过去，也不要直接删除校验。接续应先验证D13字幕，构建全新Run170，然后完整/跳过流程、菜单比例及公开入口实机通过后切换。旧Run167、源文件和地图原样备份均保留。

## 复现证据

- Saved/ArtPolish-2026-10-25/CURRENT-HANDOFF.json
- Source-Delta.json、Bench-Apply.json、Bench-Matte-Compare/Before.png与Candidate.png
- Build-Summary-DevD13.json、Automation-RunD14/RESULT.json
- Runtime-Run169-FullFlow/FLOW-RESULT.json与Runtime-Images/Run169-Flow-*.png
- Runtime-Images/Run168-Menu16x9.png、Run168-Menu16x10.png
- Backup下保留八个源文件、原地图与旧Shipping启动脚本。

取景复核显示Inside/Operate两个位置能完整读幕面，但只属这些机位的证据；没有改玩家相机或用瞬移解决遮挡。彩偶与影子局部叠压、主体偏下及既有林影造型仍是后续美术提升项，不写成已解决。人类作者与最终责任人为用户，Codex为辅助工具，新增本地材质复用登记见LICENSES第13节。
