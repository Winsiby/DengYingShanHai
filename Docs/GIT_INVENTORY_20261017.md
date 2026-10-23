# Git 文件盘点表（阶段 G 第一步，只读）

> **日期：** 2026-10-17　**执行者：** Codex（只读盘点，未执行任何 staging/提交/推送/删除）
> **依据：** 《下一步执行安排_v6核验更新版.md》§九 Git 安全要求；**修订 2**（2026-10-17 晚：响应《Git盘点整合版》§G4 复核项）
> **用途：** 供作者确认文件范围与同步策略。在作者批准前不做任何 Git 写操作。

## 0. 修订 2 的重要修正：仓库实际启用了 LFS

复核 §G4"检查 `.gitattributes`"时发现**与此前记录不同的事实**：

1. **`git-lfs 3.7.1` 已安装**，`.gitattributes` 的 LFS filter **实际生效**：`*.uasset`、`*.umap`、`*.fbx`、`*.psd` 等均配置了 `filter=lfs diff=lfs merge=lfs -text`。
2. **两个 Dev `.umap` 的 diff 显示的是 LFS 指针变化**（oid sha256 + size 61393→64211 / 61133→65619），不是二进制内容——证明这两个文件在 Git 中以 LFS 指针存储。
3. **含义修正**：29 个未跟踪 Content 资产 + 2 个 umap 修改若被 `git add`，Git 对象只存 **约 130 字节的 LFS 指针**，真实内容进本地 LFS 存储——**Content 入库的 Git 体积风险远小于此前评估**；实际成本转移到推送时的 LFS 上传（需要远端支持 LFS）。
4. **根目录 README"此独立快照未启用 LFS"的说法与当前事实不符**（过时信息），建议作者更新 README 或澄清 LFS 策略。
5. **两个 Dev `.umap` 的修改来源已确认**：修改时间 2026-10-02 / 10-03，与 M2 slice 开发同期——**是有意的保存**（M2 开发过程产物），不是意外改动。

## 1. 总览

| 项 | 值 |
|---|---|
| 本地分支 / HEAD | `master` @ `dda43f2`（2026-10-02 M2 slice） |
| 已修改（M） | 40 |
| 未跟踪（??） | 246 |
| 删除 / 暂存新增 / 重命名 | 0 / 0 / 0 |
| 远端 | **无**（`git remote` 为空） |
| 公开仓库 | `main@b5ed7c0`（另一条提交线，不含本地修改） |

## 2. 已修改文件分组（40 个）

| 组 | 数量 | 明细 |
|---|---|---|
| Docs | 18 | 架构/资产/计划/验证类文档（ARCHITECTURE×2、ASSET×2、GDD、TECH_SPEC、M1/M2_VALIDATION 等） |
| Source | 14 | M2/M3 slice 代码（GameMode、PuppetActor、PuzzleDirector、StageEnvironment、M1/M2 测试等——**均非本轮 M1 修复文件**） |
| Scripts | 4 | Create-M1/M2DevSlice、Verify-M1/M2DevSlice |
| Content | 2 | `Dev/Interaction/LV_InteractionLab.umap`、`Dev/M2/Maps/LV_M2PuzzleLab.umap`（Dev 图，历史被脚本/编辑器保存） |
| Config | 1 | DefaultEngine.ini |
| 根 | 1 | AGENTS.md |

**本轮 M1 修复的归属**：`DYInteractionComponent.h/.cpp` 修改 + `DYControlStaleActorAutomationTests.cpp` / `DYControlExitRecorder.h` 新增 + 3 份 Docs 新增——**全部尚未提交**，混在上表未跟踪/已修改集合中。

## 3. 未跟踪文件分组（246 个，修订 2 按 LFS 事实更新）

| 组 | 数量 | 说明 | 入库建议（供作者决策） |
|---|---|---|---|
| Docs | 81 | 验证/计划/审查记录（含本轮 5 份） | 建议**入库**（纯文本，项目记录） |
| Scripts/Tools | 57 | Dev 切片与验证脚本 | 建议**入库**（可复现记录） |
| Source | 51 | M2/M3/P03 slice 代码与测试（含本轮 2 个新测试文件） | 建议**入库** |
| Content | 29 | Dev/正式资产（**LFS filter 生效，入库为指针**；真实内容推送时需远端 LFS 支持） | 建议**入库**（体积风险已修正；需作者确认远端 LFS 策略） |
| **Builds** | **26 目录，共 22 GB** | **历史构建包**（2026-10-06 至 10-14 各候选 Run；**含 ReleaseEntry-Development/Shipping-20261014——即 RELEASE_ENTRY_FOUNDATION.md 记录的 2026-10-14 正式构建证据**） | **建议不入库**（构建产物可重建）；因含 10-14 正式构建证据，建议**仓库外归档**至少保留这两个正式包 |
| Assets | 1 目录（Sources，764 MB） | 原始资产源文件，三来源：**DengYingArt 574 MB / Innerscene 97 MB / PolyHaven 94 MB**（.gitattributes 含 *.fbx/*.psd/*.tif 的 LFS 条目，入库为指针可行） | **暂缓**——三个来源对应审查意见 §8.3 的许可核对对象（PolyHaven 为 CC0 类、Innerscene/DengYingArt 需逐条核对），核对完成前不提交 |
| 根级 | 26 | Start-*.cmd 启动器 ×24、Start-ReleaseEntry-Shipping.cmd 等 | 建议**入库**（小文本；内含固定 D 盘历史路径，与 §8.4 跨机说明一并标注） |

### Builds/ 完整清单（26 个，供作者归档决策）

```
AlignmentDev-20261010-Run1/Run2          AudioDev-20261010-Run1/2/3
EntryLoopDev-20261009-Run1/Run2          EnvironmentDev-20261011-Run1/Run2
FrameBeamCandidate-20261013-Run1         FrameBeamDev-20261012-Run1
FrameBeamTopUV-20261013-Run1             FramePostDev-20261012-Run1
M3Runtime-20261006-Run1/2/3/4            M3Runtime-20261007-Run1
ReadabilityDev-20261009-Run1             StageWingsDev-20261011-Run1
ThreeActDev-20261009-Run1/2/3
ReleaseEntry-Development-20261014-Run1   ReleaseEntry-Shipping-20261014-Run1  ← 正式构建证据
```

## 4. 风险项（v6 §九要求检查，修订 2 更新）

| 检查项 | 结果 |
|---|---|
| **大目录** | `Builds/` 22 GB（构建产物，含 10-14 正式构建证据）；`Assets/` 764 MB（原始资产，LFS filter 已配置可入库为指针）——**Builds 仍是最大风险**：非 LFS 类型（构建产物无 .gitattributes 规则），`git add .` 将把 22 GB 推入普通 Git 对象 |
| 敏感文件名（.env/secret/credential/token/.pem/.key/password） | **未发现** |
| LFS 状态 | **git-lfs 3.7.1 已安装且 filter 生效**；Content 资产入库为指针。推送需远端 LFS 支持 |
| 个人路径泄露 | `Scripts/Start-M3Runtime.ps1` 等含固定 `D:\灯影山海` 路径（历史已知，非本轮引入）；本轮新增文档均用相对描述 |
| README 过时信息 | 根 README"未启用 LFS"与 `.gitattributes` LFS 配置矛盾，建议作者更新 |
| 两个 Dev .umap 修改 | **确认为有意保存**（M2 同期，LFS 指针更新），可随 Content 一并入库 |

## 5. 建议的分组决策清单（待作者逐项批准，修订 2 按口头LFS事实更新）

| 组 | 建议 | 前置条件 |
|---|---|---|
| Source + Scripts + Docs（全部已修改与未跟踪） | 提交（本地 commit） | 作者过目文件清单 |
| Content（29 个资产 + 2 个修改 Dev 图） | **提交（LFS 指针化，体积风险小）** | 作者确认远端是否支持 LFS（推送时上传真实内容）；确认 .umap 是有意保存（已确认） |
| 根级 Start-*.cmd（26 个） | 提交 | 与 §8.4 跨机路径说明一并标注 |
| **Builds/（22 GB）** | **不提交**；加 `.gitignore: Builds/` 或移出仓库归档 | **建议至少仓库外保留 `ReleaseEntry-Development/Shipping-20261014` 两个正式构建**（历史验收证据） |
| Assets/Sources（764 MB） | 暂缓提交 | 先完成 §8.3 资产许可逐条核对（DengYingArt/Innerscene/PolyHaven 三来源） |
| 提交信息建议 | 分两个 commit：① M2/M3 slice 与历史工作补登；② M1 操纵态修复 + 五份核验/盘点文档 | 由作者定 |
| 远端同步 | 作者决定是否建立 remote、指向哪个远端（**需支持 LFS**）、如何与公开仓 `main@b5ed7c0` 关联（两条提交线合并需要作者明确策略） | — |
| README 修正 | 更新"未启用 LFS"的过时描述 | 建议随首次提交一并处理 |

## 6. 明确未做

未执行 `git add`、commit、stash、reset、checkout、push 或任何远端操作；未修改 `.gitignore`；未移动或删除任何文件（含 Builds/）。全部结论只读。

## 7. 本轮 M1 修复文件的精确归属（便于作者挑选）

```
修改：Source/DengYingShanHai/Public/Interaction/DYInteractionComponent.h
修改：Source/DengYingShanHai/Private/Interaction/DYInteractionComponent.cpp
新增：Source/DengYingShanHai/Private/Tests/DYControlStaleActorAutomationTests.cpp
新增：Source/DengYingShanHai/Private/Tests/DYControlExitRecorder.h
新增：Docs/CONTROL_STALE_ACTOR_FIX_20261017.md
新增：Docs/REFERENCE_MAP_20261017.md
新增：Docs/UE_VERIFY_20261017.md
新增：Docs/STAGE_A_VERIFY_20261017.md
新增：Docs/GIT_INVENTORY_20261017.md（本文件）
```
