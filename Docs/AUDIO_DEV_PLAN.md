# 基础演出声音 Dev 合同（2026-10-10）

用户已签收第二幕躯干角标校准。下一步按 M3 计划接入基础声音，不宣布完整 Alpha/盲测、5–8 分钟、正式美术或 Shipping 通过。

唯一作者与负责人：用户；Codex 辅助本轮技术与声音适配；不依赖 WorkBuddy 或其他制作成员。

## 可见／可听结果

开始后低层微风；实际 Holding 进入克制的 impact 节奏，打断/复位立即停止；P01/P02 成功各一次木击；P03 Resolve 不播落杖重音，只有 Stage 实际接受杖尖接触才播放一次重音；实际 Forest Complete 后进入轻枝叶声。静音时原流程完整，声效缺失不阻塞成功。全部是免费 CC0 Dev 声音，不称传统锣鼓、唱腔或实地风录音。

## 所有权与通信

Stage（原有唯一表现事实源）→ 显式引用的独立 `ADYStageAudioPresentationActor`（本世界被动音频发声实体）→ 五个默认不自动播放的 Audio Component。Actor 不 Tick、不扫描世界、不查询 Director 或操纵输入/相机，不新建全局管理器、Subsystem、计时器、成功状态机或第二接触算法。仅订阅现有无答案幕次/反馈/已接受接触 Native delegate，BeginPlay 单次绑定、EndPlay 对称解绑并停止声音。声音 Actor 只拥有发声实例与去重标记；不持有目标/容差/数值进度。

使用原生底层是为生命周期、一次性去重与自动测试提供可复用边界；当前组装由 Editor API 在同一 Dev 地图中配置声音引用。没有臆造或复制 Blueprint 判定图。

## 最小改动白名单

- 新 native Audio Actor 头／实现、一个 native Automation 测试文件；不改任何已有 C++、Build.cs 或插件。
- `Dev/Audio/` 下精确选择的五个声音（环境风、保持节奏、成功木击、接触木击、成林叶声），不导入整包。
- 当前 AlignmentFeedback Dev 地图只增加一名默认关闭类、显式启用实例的声音 Actor，原 Actor Transform/主灯/皮影/幕布/提示引用冻结。
- 独立 `Start-AudioDev.cmd` 与 helper、新 AudioDev Run1 包，旧 Alignment Run2 源入口／包继续保留；它们进入同一当前地图，但旧固定包不变。
- 新来源/验证文档，TECH_SPEC、DEVELOPMENT_PLAN 更新，P02 验证文档追加用户体验签收（不改历史机器记录）。

禁区：15 Hz、目标／容差／1.25秒保持／2秒题签、灯速.2625、偶速.28、E/A/D/R、菜单、镜头、A端/Z70、落杖/接触/林形/完成权威、Config、旧包。暂不做唱腔、传统锣鼓谱、脚步、音乐、设置系统、暂停或Skip。只新增声音表现，不扩大场景或体验时长。

## 素材与回退

Kenney Impact Sounds 与 OpenGameArt 原作者 wind1／dry leaves 的具体来源、CC0、文件hash和转码记录保存于本轮独立来源证据；不读取旧许可登记表，不借付费或来源不明替代。辅助转码库仅在项目开发工具目录使用，不进入游戏或Cook。

当前地图 Before 镜像及源码hash在 `Saved/Audit-2026-10-10-AudioDev`；旧 Run2 包可直接比较。回写前检查后续编辑，禁止全仓 reset/clean；不得删除旧证据。

## 验证

纯去重策略／默认关闭／无Tick／生命周期自动测试；真实两轮三幕的 Hold→打断、当前幕复位、P03接触前静默、一次接触重音、实际成林、同图重演新世界无旧声；记录发声请求、音频设备播放状态与真人试听分别证明的范围；静音对照仍完成。最后独立 Development Build/Cook/Stage/Archive、声音依赖manifest、真实首帧/退出与实际启动器DryRun。
