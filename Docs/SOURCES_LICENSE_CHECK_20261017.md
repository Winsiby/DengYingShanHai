# `Assets/Sources` 许可核查现状（阶段 G3 第一步）

> **日期：** 2026-10-17　**执行者：** Codex（只读盘点，未执行任何提交/推送）
> **依据：** 《下一步执行安排_Git盘点修订2.md》§G3
> **目的：** 汇总三来源的本地许可证据现状，作为作者复核与解除 `Assets/Sources` 暂缓的输入。

## 1. 三来源核查结果

| 来源 | 规模 | 许可类型 | 本地证据 | 状态 |
|---|---|---|---|---|
| **DengYingArt** | 574 MB | **作者自制**（Codex 辅助程序化几何） | 6 个分批 README（ForestBranch/ForestCanopy/ForestCanopyWide-20261016、FrameFullSpan-20261015、StageProps-20261016/R2），均明确声明 "no download, paid asset, image/3D generation service or third-party mesh/texture"；FrameFullSpan 衍生自 CC0 VVayToyek 四角亭梁 + Poly Haven Dark Wood，上游 CC0 证据在 `Docs/FRAME_BEAM_ASSET_SOURCES.md`、`FRAME_POST_ASSET_SOURCES.md`；各批含 SOURCE.json/DERIVATION.json 哈希溯源 | **证据完备**，README 即许可声明 |
| **Innerscene** | 97 MB | **CC0 1.0 Universal**（Sam 人物源资产，基于 MakeHuman/MPFB CC0 body） | `Operator-20261017/LICENSE.md`：原页面逐项声明 CC0、允许免费使用/修改/再分发；含 Idle/Run 两个来源 URL；保留来源/原始文件/哈希为归档要求（非许可强制署名） | **证据完备**；注意这是历史 Sam 源资产——许可清晰**不等于**重新启用为正式角色（该设计决定仍由作者负责） |
| **PolyHaven** | 94 MB | **CC0**（知名 CC0 PBR 库） | 直接许可文件未见；既有证据：`FRAME_BEAM_ASSET_SOURCES.md`/`FRAME_POST_ASSET_SOURCES.md` 记录的 Poly Haven Dark Wood 纹理家族 CC0 证据 | **基本完备**；建议补一份 94 MB 内逐资产的来源清单（哪些具体资产实际被使用） |

## 2. 结论与剩余动作

**三来源许可均可追溯，`Assets/Sources` 暂缓提交的解除条件基本满足**：

1. DengYingArt：原创声明 + 上游 CC0 衍生证据齐备——**可直接解除暂缓**（随 Content 一并入库，LFS 指针化）。
2. Innerscene：CC0 逐项 URL + LICENSE.md——**可解除暂缓**（作者复核 CC0 适用性后）。
3. PolyHaven：库级 CC0 明确——建议补一份"94 MB 内实际使用的资产清单"（逐资产 URL），再解除。

**重要边界（重申审查意见）**：Innerscene 的 Sam 源资产许可清晰，但《下一步执行安排》与历次审查均规定**复演者设计由作者先行决定**——本核查只证明"可以合法保留与再分发"，不授权把 Sam 重新导入为正式角色。

## 3. 顺带完成：Builds/ 两个 2026-10-14 正式包的仓库外归档（证据保全）

- 目标：`D:\灯影山海_GitArchive_20261017\`
- `ReleaseEntry-Development-20261014-Run1`：50 文件 / 1,070,714,095 字节 — **VERIFY_OK**（文件数与字节数与源一致）
- `ReleaseEntry-Shipping-20261014-Run1`：32 文件 / 713,062,879 字节 — **VERIFY_OK**
- 原文件保留在 `Builds/` 未动；归档为复制备份，供后续 Builds/ 清理决策参考。

## 4. 建议下一步（均待作者批准）

1. 作者复核本清单 → 解除 `Assets/Sources` 暂缓（或要求补充 PolyHaven 逐资产清单）。
2. 批准提交分组（候选 A：历史工作补登；候选 B：M1 修复 + 文档）。
3. 决定远端（需 LFS 支持）与两条提交线整合策略。
