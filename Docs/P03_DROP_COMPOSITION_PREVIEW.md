# P03「杖落成林」无时长构图预览

日期：2026-10-04。

状态：**构图静态预览与技术检查完成；用户已确认下一步 Dev 使用高位地线。**
这不是正式连续落杖动画，不是完整第三幕或成林演出完成。

负责人：Codex 完成脚本、真实 PIE 取证、视觉复查和本轮事实记录。
原分工 WorkBuddy 整理文档，但本次粘贴交接因执行权限审核服务额度限制未执行；
没有把 Codex 写入的本文冒充 WorkBuddy 成果。

依据：`AGENTS.md`、`P03_DEV_IMPLEMENTATION_PLAN.md`、`P03_STAFF_CONTACT_VALIDATION.md`，
以及本机 `Saved/Audit-2026-10-04-P03DropPreview/` 内完整日志、原图与 SHA-256 审计。

> *永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*

## 1. 用户确认与准确范围

用户此前确认 **A 端 + 幕上叙事地线**，并选择真实树形几何投影方向。
本次在比较说明后回答 **“高位地线（推荐）”**：

- 下一步 Dev 高位地线采用幕布底部以上 **15%**；当前灰盒幕上世界 Z 为 **70 cm**。
- 这是 Dev 落点选择，不代表最终弃杖动作、演出时长、P03 目标/容差已确认。
- 正式皮影与幕布资产替换后，仍须验证相同视觉意图与因果关系，不照搬不同尺度下的 Z70。
- 5% / 10% 其他地线只保留为比较证据，不自动进入玩法。

没有扩展场景、输入、玩法、资产采购、镜头或团队关键路径。
本轮没有保存新地图或 BP / Sequence / 材质 / Definition，没有建立 Forest / Finale 状态。

## 2. 可见样本怎么取得

新增 `Scripts/Preview-P03StaffDrop.py`，仅运行于独立完整 Unreal Editor。
载入现有独立 `Dev/M3/Maps/LV_M3GeometryProbe`，在编辑器**内存**放置地线锚点与不投影的线标记，
临时启用 Presentation 显式引用，每组启动独立 PIE。不调用任何资产或关卡保存接口。

脚本从现有 **P02** Definition 读取 0.72 / 0.80 作为夹具目标，保持原 1.25 s Holding 和 15 Hz。
控制值设到原作者目标后，**自然等待真实 Director/Evaluator Resolve**；不是伪造成功事件或 Token，
也不是用户实际完成 P03。这些旧数字不是本轮批准的第三幕参数。

起始位置来自 live Resolve 的真实 Staff 世界变换。
根据实际发光点、幕布接收面与 A 中心射线反算实体目标，仅平移 Staff，不改旋转、缩放、
灯/偶 Actor 根、主灯或幕布，不用固定预制成功姿态替换最终构图。

0% / 50% / 100% 是**归一化位移采样**，不是动画时长或谜题评分。
20 个渲染稳定帧和脚本诊断截止时间也不是落杖/生长节奏参数。

截图由实际 PIE 玩家视口 HighResShot 生成，1600×900，保留原文件，未合成/编辑。
图中白色 Staff 是后台实体，黑色杖影是同一主灯的真实投影；A/B 字母只是开发探针。
不包含 HUD 的截图不能用来宣称本轮重新验收了中文 UI。

## 3. 比较结果

最新比较的六张原图在：

`C:\UEProjects\DengYingShanHai\Saved\Audit-2026-10-04-P03DropPreview\VisibilityRefinement\`

| 样本 | 地线高度 | 起始 / 中途 / 接触图 | 幕上 A 的世界 Z：起始 → 中途 → 接触 | 视觉结论 |
|---|---|---|---|---|
| High，15% | Z70 | High-000.png / High-050.png / High-100.png | 130.359688 → 100.179844 → 70 | 接触更远离后台地板；**用户选择用于下一步 Dev** |
| Low，10% | Z30 | Low-000.png / Low-050.png / Low-100.png | 130.359688 → 80.179844 → 30 | 下落更长，标记可见但更靠近地板；未选择 |

共同幕上 X925、Y约 -11.156213，均从相同真实 Resolve 起点继续。
POV 为 `(-1260,-155,178.150002)`、FOV70，全程保持原玩家相机所有权，没有新 Camera Cut。
实体 A 初始 Z173.929167；High 终点 Z128.208955，Low 终点 Z97.910448。
因此**幕上叙事接触不要求实体 Staff 碰后台地板**。

### 不能用几何通过代替可见性

第一轮比较 High=15% 与 Low=5%，原图位于同一审计目录根部，日志为 `Preview-Attempt3.log`。
5% 的幕上地线世界 Z=-10，被后台地板遮挡，接触标记不可读。
原生接触虽然为 true，**视觉不通过**。该候选被排除，保持机位、灯和幕不动，补拍 10% 对比。
旧图、旧日志均保留，没有覆盖它们制造“从未出错”的证据。

## 4. 技术验证与限制

最新 `Preview-VisibilityRefinement.log`：完成记录 `Completed`、`error=null`，两组各三张截图。
两组均实际检查：

- 0% / 50% 原生 `TryAcceptStaffContact` 返回 false，100% 返回 true。
- 同 Token 二次调用拒绝；中途非接触和终点接触均不撤销已成立的谜题成功。
- 起始 Staff 世界变换必须等于 Resolve 快照；截图前后锁定该帧 Staff 的真实变换。
- Token、地线、主灯发光点、幕布、灯/偶根与实际玩家 POV 保持一致。
- 清理时显式恢复完整 Staff 相对变换，而不是只依赖旧控制复位恢复旋转。
- 使用既有 Reset 进行诊断清理后旧 Token 被拒绝；这**不是**正式 R / Skip / RestartExperience 策略。
- 结束 PIE 后释放其 wrapper，不继续访问死亡世界，注销 Slate 回调并还原临时编辑器引用。

前两次运行因脚本 `get_pawn` / `get_relative_rotation` 反射名称不匹配而失败；已在编辑器脚本修正，
完整日志分别为 `Preview-Attempt1.log` / `Preview-Attempt2.log`。不是产品源码 Bug，两次均安全结束会话。

最新全日志仍包含既有本地化 smoke-test **13 条 Condition failed Error**，以及一条 NVIDIA TSR 驱动兼容 Warning。
因此只能说本轮预览检查完成，**不能说整日志零 Error/Warning**；没有为这些提示改驱动或引擎配置。

本轮不是新增 C++ Automation 测试。上一轮 **48 Success / 0 Failed** 及三目标编译是历史基线，
本轮源码没有改变，未重跑这些命令，也未新 Cook / Stage / Package / Shipping 运行。

## 5. 文件保护、证据与回退

写文档前，132 项旧产品文件 **132 相同 / 0 改变 / 0 缺失**，仅新增预览 `.py`。
本轮允许产品变化只有：

- 新增 `Scripts/Preview-P03StaffDrop.py`。
- 新增本事实记录 `Docs/P03_DROP_COMPOSITION_PREVIEW.md`。
- 对 `Docs/P03_DEV_IMPLEMENTATION_PLAN.md` 追加本轮状态与用户确认，不删除历史章节。

Source / Config / Content / .uproject / 旧 Scripts / 根启动入口均未改；没有 `.uasset/.umap` 磁盘变化。
精确最终数字见审计 `ProductScopeAudit.json`。开发计划原文在 `Backup/Docs/` 保存，
回退只恢复明确的单文件，不 reset/checkout 脏工作树，不进行 Git 写操作。
生成的 Python 字节码移入审计 `Diagnostics/`，没有删除用户文件。

主要证据：`Execution-Contract.md` / `Supervisor-Results.md`、最新 `Preview-VisibilityRefinement.log`、
`VisibilityRefinement/*.png`、原三份 Attempt 日志及第一轮截图、`Baseline.json` / `ProductScopeAudit.json`。

卸载的 Computer Use 插件未使用，STOP 文件保持。
WorkBuddy 仅恢复窗口并截取其当前聊天做交接准备，模型/权限未改；粘贴请求被审核服务额度限制拦住，未执行。

## 6. 下一步与未完成项

**下一步采用已确认的 High 构图**，从当前真实实体 A 端继续验证同一点树形几何展开，
由同一 Movable 主灯投出连续林影。幕上投影点不能直接拿来当幕后几何生成点。
先使用归一化展开样本确认构图，不暗中设定正式生长时长。

当前仍未实现连续落杖编排、保存的地线关卡实例、树形灰盒/林影、Forest Actor、
P03 Definition、Finale、三幕队列、Skip、统一重启、两种新环境态、正式美术/声音及新游戏包。
当前原图是技术灰盒，不是高质量参赛美术完成。

地线位置已确认这一小步不扩大为动作、时长、参数或所有收尾规则的批准。
需要启动 UE、构建验收或操作 WorkBuddy 的后续执行，等待权限审核服务恢复后继续；不绕过审核。
