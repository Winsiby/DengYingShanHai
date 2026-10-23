# 美术优化与验证记录（2026-10-22）

本轮目标：核对实际工程进度，并完成一批能在既有剧场中验证的美术优化。负责人为用户本人；Codex 辅助实现与核查。概念图全部交付不等于对应模型已经全部落地，整体进度见 [进度核查](PROGRESS_REVIEW_20261022.md)。

## 本轮结果

- 8 个门楼、屋檐与屋顶装饰球灯替换为一套自制八角纸灯：纸面、八根竹骨、上下木圈与黄铜端部。共用一个 768 三角面网格；没有增加 Actor。
- 右侧立面装饰补光 `DYExt16_FacadeLamp_R` 从 2600 cd 调为 650 cd，减轻与门口争夺注意力的冷白亮斑。对比了原强度、1300、650 与关闭四种画面后选定 650。
- 纸灯共享材质的 Glow 保持 Run100 的 1.7；复用现有纸、木、黄铜材质。仅该补光强度改变，其他灯光参数、全局曝光和渲染配置未改。
- 保留 1577 个 Actor 的数量与变换、灯具包络、碰撞和投影属性。没有修改玩法源码、谜题条件、目标容差、输入、相机或演出状态机。

这是 A5 的局部落地。14 盏室内吊灯和 6 盏壁灯尚未替换，不能标记整个 A5 完成。

## 画面对照

三组取景均为 1920×1200、FOV 70，使用同一固定编辑器机位分别捕获原 Run100 主图与本轮已保存主图。取景脚本不保存临时相机。图像经过人工逐张查看，并由独立代理复评。

| 机位 | 优化前 | 优化后 | 可见结果 |
| --- | --- | --- | --- |
| 门楼近景 | [Before-Gate](../Saved/Audit-2026-10-22-ArtPolish/Before-Gate.png) | [Final-Gate](../Saved/Audit-2026-10-22-ArtPolish/Final-Gate.png) | 球形灯改为可辨识的纸灯构造；小灯不再只有光球轮廓 |
| 入场方向 | [Before-Entry](../Saved/Audit-2026-10-22-ArtPolish/Before-Entry.png) | [Final-Entry](../Saved/Audit-2026-10-22-ArtPolish/Final-Entry.png) | 冷白亮斑减弱；门口与暖色灯径仍保留层次 |
| 大厅幕面 | [Before-Hall](../Saved/Audit-2026-10-22-ArtPolish/Before-Hall.png) | [Final-Hall](../Saved/Audit-2026-10-22-ArtPolish/Final-Hall.png) | 未见可辨识的视觉回归；旧重复框、室内球灯仍存在 |

局部观感改善有图像依据；固定编辑器机位不代表所有玩家角度，也不代替独立玩家与最终美术验收。运行中的 Shipping 证据在同一审计目录 Runtime-Isolated 下。

## 源文件与接入

源目录：`Assets/Sources/DengYingArt/A5-LanternFamily-20261022/`，保留生成脚本、OBJ、MTL 与 SOURCE_MANIFEST.json。网格单位为厘米、Z 向上，原点居中，包络精确为 100×100×100。8 个实例保留原缩放，对应 115、66、50 厘米包络。

新资产：`/Game/DengYingShanHai/Dev/ArtPolish_20261022/Meshes/SM_DY_LanternFamily_Unit100`。按实际导入槽名赋 Brass / Paper / Wood，三个材质来自既有项目。此自制程序网格的来源登记见 [LICENSES](LICENSES.md) SELF-007，无外部下载或新增付费资产。

当前渲染为 Deferred DX12 / SM6，Lumen GI，硬件光追关闭；保留既有手动曝光。纸灯为装饰网格，不承担谜题光源或主投影判定。

## 技术验证

- 保存后重新加载主图验证替换与补光值；A5-Apply.json、FacadeFill-Apply.json 均通过。
- 176 项原生自动化测试通过，失败 0；见 [AUTOMATION.json](../Saved/Audit-2026-10-22-ArtPolish/AUTOMATION.json)。
- Shipping 构建 Cook / Stage / Archive 实际退出 0，UFS 清单包含新网格，Cook 为主图与 Engine Entry 两张地图。
- 新包：`Builds/FormalMain-Shipping-20261022-ArtPolishA5/Windows`。31 个交付文件，751,260,131 字节（不含 RELEASE-ENTRY-BUILD.json）。
- 当前主图 SHA256：`1ABFC443A79F42B156F36EB65DE274FC7B9C9EBA18DC13FC2BED5232245AD7A9`。
- 新包原生 EXE SHA256：`1710A30AD8FC8E6488ADE4A60AC8855A88D5A656783B66B9BD90927172D9A8E4`。
- 实际 Shipping 窗口完成两轮四幕辅助流程，探针记录两次 phase=4 chapter=4/4、8 次章节结算、18 次音效事件；已观察“复演已成”和重演入口，正常关闭原生进程退出 0。辅助参数为已有 DY_CAMPAIGN_AUTOPLAY 与 DY_DEBUG_VIEW=1，不属于独立玩家盲测。见 [运行回执](../Saved/Audit-2026-10-22-ArtPolish/Runtime-Isolated/VERIFICATION.json) 与 [重演终态截图](../Saved/Audit-2026-10-22-ArtPolish/Runtime-Isolated/Replay-Observation.png)。
- 真实公开入口 Start-ReleaseEntry-Shipping.cmd 已切到新包，保留主图/EXE SHA256、31件数量与字节数、IoStore容器全部校验；-DryRun 通过，并清空辅助环境后实际启动到可响应菜单、正常退出 0。见 [入口核验](../Saved/Audit-2026-10-22-ArtPolish/Public-Verification.json) 与 [真实入口首帧](../Saved/Audit-2026-10-22-ArtPolish/Public-FirstFrame.png)。原用户 DYProgress.txt 哈希与备份一致。构建阶段 RESULT/identity 中的首帧字段为当时初始值；以独立运行回执记录本次已完成的技术核验。

构建脚本首次因 Windows PowerShell 模块路径继承问题在 Cook 之前中止；修正运行环境后构建成功。原错误日志保留，未关闭任何哈希校验。

## 尚需处理

1. 外景黑球树冠是当前最明显的美术缺口；B1/B2 前次失败方案已回退，不能把隐藏资产或概念图算作完成。
2. 大面积木墙与嵌套旧幕框仍显单调；需要按主要游玩机位分批处理，避免遮挡幕上结果。
3. B3 山石、C1 三具新增影偶、C2 锣鼓实体、C3 图鉴插图仍仅有概念参考。
4. 当前内容版本的帧时间复测、独立首次玩家 5–8 分钟体验、静音可解性、目标机三轮与人工最终美术验收仍未闭环。
5. 历史三互动目标与当前四幕实现存在范围文档差异，本轮仅记录，不据此改动已有玩法。

以上任务最终负责人均为用户。Codex 可继续辅助制作和核验，不把自动辅助流程视为独立人工验收。

## 回退

原主图、原启动脚本与原许可文件保存在 `Saved/Audit-2026-10-22-ArtPolish/Backup/`。旧 Run100 包完整保留，主图原 SHA256 为 `67B5E713693EF86A3EE99B7410C1A3B99866C836972C93D4E83C3B3C621C3449`。

需要回退时先正常关闭 UE 与游戏，再成对恢复备份主图和启动脚本，并运行启动脚本 -DryRun 校验旧包。不要单独回切包路径或关闭主图 SHA256 校验。新纸灯源文件与新资产可保留作过程证据；本轮没有删除或覆盖其他人类作者的源文件。

## DSH 补充轮：外景观感总补（Run101，2026-10-22 02:00）

上一节由 Codex 完成 A5 局部落地后，用户要求「继续推进项目美化，把建模全部完成，完成所有建模和美术优化确保观感」。这一轮把上面「尚需处理」的第 1、2 条正面处理，并把 B3/C2 从概念图变成场景实体。

- **树冠不再是黑球**：322 个 `MI_DY_TreeDead` 球冠换成 Codex 已交付的 `SM_DY_BranchCrown_A/B_Unit100`（不重做、直接复用），scale = 原包围盒 extent / 50，Z 旋转用标签字符和保证可复现。
- **大面积墙面有材质了**：PIL 现生成 6 张贴图（土、石板路、竖板墙、石膏、树皮、岩石），做 5 个「世界坐标 UV + TileU/TileV 参数」母材质与实例，指派给 8 面墙、83 个石构件、1 块外景地面、1 条石径；石膏与岩石的 tile 压到 130–300，否则 600 cm 尺度会读成大理石。
- **外景有建筑层次了**：外墙面加 18 件壁柱 / 石墙裙 / 木带 / 檐口；补 17 块 B3 山石（按 20% 埋深）与 27 件 C2 锣鼓道具（戏箱、案桌、堂鼓、大锣架 + Ø90 锣、小锣、钹一对、鼓槌）。全部为装饰件，不参与判定、不改槽位。
- **光照与曝光**：门楼灯 2600/650 → 600/380 cd、月光轮廓 35 → 700、天光 0.8 → 1.35、外景雾 0.008 → 0.018，加一盏无阴影月光补光（150 lux）与 3 个道具点光。查明后处理卷是手动曝光（`AEM_MANUAL`、bias 3.5），暗是缺光而非自动曝光。
- **交付**：Run101，`PASS-BUILD-COOK-STAGE-ARCHIVE`、UAT 0、31 文件 / `752,992,875` 字节、map `0846A10E…B3B61D99`、exe `1710A30A…72D9A8E4`（无 C++ 改动）；自动化 176/0（`AutomationV32.log`），`verify_sfx` 9 条与 `verify_replay` 25 行双绿。真机 `Saved/Audit-2026-10-20-V21/s101-w01/w03/w05.png`，编辑器对照 `Saved/Audit-2026-10-22-ArtPolishFinal/`。启动器已改指 Run101，`-DryRun` = `PASS-PREFLIGHT-ONLY` / 31 / 752992875 / 退出 0。
- **仍未闭环**：B1 山体仍是 91 个 Cone；C1 三具影偶、C3 图鉴版式未做；性能复测与人工美术验收未做。详细记录见 `Docs/FORMAL_SHIPPING_20261020.md` §9.33 与 `Docs/THEATER_WORLD_V21_20261020.md` §11.38。

## 追加：Run101 → Run118 期间落地的美术项（汇总）

- **外景材质**：世界坐标 UV 母材质 `M_DY_GroundTex` / `M_DY_StonePathTex` / `M_DY_WallPlankTex` / `M_DY_PlasterTex` + 5 张自制程序化贴图，替换走廊地面、踏石、木构与灰泥；灰泥 Tile 130→**95**、Tint 压到 (0.62,0.575,0.515)，墙面不再像细密网格。
- **树干与枝条**：`M_DY_TrunkTex`（WorldPosition→ComponentMask→Divide(Tile 220)→TextureSample→×Tint）替换 **632 个树干**；322 个球冠换成枯枝剪影网格并把 `MI_DY_BranchBark` 压到 (0.09,0.065,0.045)，夜里读成深色枯枝而不是奶油珊瑚。
- **山石**：B3 山石换程序化棱面 OBJ（二十面体细分 + 随机位移 + 逐三角硬棱），**49 件**（17 个 `ART_B3_Rock_*` + 32 个 `DYTheater_Rock_*`），夜间有真实受光棱面。
- **灯具**：门楣以上山墙 6 盏壁灯 + 4 盏暖点光；观众厅 **14 盏吊灯 + 14 根吊绳 + 6 盏壁灯 + 13 盏点光**，吊灯 2600 cd / 壁灯 1200 cd；补两块内顶望板 `ART_A6_HallCeiling*`，厅顶不再死黑。
- **锣鼓**：`MI_DY_AgedBrassProp`（`Pigment` (0.78,0.58,0.26)、Metallic 0.6、RoughnessLevel 0.52）覆盖大锣/小锣/钹，锣从"黑板"变成可读铜盘，另加 2 盏乐班暖点光。
- **图鉴**：`DYDevEntryWidget` 增第 5 行「制作七步」，C1 三具影偶以概念图插画承载（夸父 598×643 绝对像素框、精卫/刑天/烛龙、七步图版 1990×1085），卡片 1040×1000 + `UScaleBox` 缩放，任何比例不变形。
- **收掉的观感问题**：门前 16 根黑锥隐藏；64 座近场三角锥隐藏（保留 43 座远景）；7 盏冷色灯的颜色序（`FColor` 是 B,G,R,A）修正为暖色；门脸过曝配光 5200→3000/3600。
- **明确停止的方向**：B1 真山体两次尝试（墨色剪影卡片板、棱面山脊网格）都被 Shipping 实机帧证伪（看不见 / 头顶白色碎片），已回退并停止；远景保留 Cone + 分层墨色 + 随距隐藏。
- **当前包 Run118**：31 文件 / 760,801,003 字节、map `AEF5A6F9…2F8FEF75`；自动化 176/0、锣鼓 9 cue、连演到「复演已成」终局面板、性能探针 AVG **145.3 fps** / MIN 128.4（1920×1200）。
- **仍需人工**：独立玩家 5–8 分钟可解性、观感与听感验收、最终提交；入口路面那条淡色引导带已归因为运行时生成并接受。

## Run121–Run128 汇总（2026-10-22 夜）

| Run | 主题 | 关键改动 | 结果 |
| --- | --- | --- | --- |
| Run122 | 路面青石板 | 重画 `T_DY_StonePathTex_BaseColor`、Tile 170→250、Tint (0.80,0.80,0.78) | 31 文件 / 760,814,219 B |
| Run123 | 门脸木格窗 | 26 件 `ART_EXT_Lattice_*`，框 24×14 / 棂 16×5 cm | 同上字节，只 map 变 |
| Run124 | 入口白片→嵌石 | `LayReadableEntry()` Plane/BasicShape → Cube/`MI_DY_StonePathTex` MID、2 cm 厚、抬 1.1 cm、抖动 | 760,814,219 B，exe 哈希首变 |
| Run125 | 后台锣鼓曲面化 | 11 个 OBJ → `SM_DY_C2_*`，替换 23 件基本体，新增 12 件 | 760,983,728 B |
| Run126 | 影窗绢面 + 灰泥 | 2048×1820 软竖缝绢面；Plaster Tile 95→240 | 760,539,025 B（贴图低频化后反而更小） |
| Run127 | 观众厅挂屏 | 空心框 `SM_DY_PuppetFrame` + 4 幅图鉴插画 + 每屏 120 cd 灯 | 760,544,163 B |
| Run128 | 观众席长凳 | `SM_DY_AudBench` 8 件 + 8 坐垫 + 8 座位灯 | 760,556,929 B |

- 每轮都跑：`Package-Shipping.ps1`（31 文件、`UATExit=0`）、`run_automation.ps1`（176 tests / 0 fail）、`verify_sfx`（9 cue）、`verify_replay`（`REACHED_PHASE4=True`）、`run_art_shipping2.ps1` 真机帧。
- 现包 **Run128**，map `A9A581AC…052FAD`，启动器 `Scripts/Start-FormalShipping.ps1` 已指向 Run128 并带 UTF-8 BOM。
- 待办：`Docs/FORMAL_SHIPPING_20261020.md` 因一次 read→write 往返丢过 §8–§9.53（不可恢复，已重建为 §10 台账 + §11 近轮详解 + §12 长凳）；后续**大文件只用 `fs.readFileSync`/`fs.appendFileSync` 或 `edit`**。
