# GitHub 私有仓库上传前只读核查

核查时间：2026-10-16 17:25:56–17:25:59 +08:00（目录统计快照）。工程物理目录：`D:\灯影山海`。

本报告只为“本轮成林美术迭代收尾后，先上传当前工程到 GitHub 私有仓库”准备；不等待其余全部美术，不表示比赛作品或当前叶冠艺术方案已验收。

负责人：用户为唯一人类作者与项目负责人；本轮 Codex 子任务只做只读核查和本文，实际建仓/上传由主代理执行。

## 1. 结论先行

- 源工程主要目录及根文件的粗统计为 **615 个文件、944,899,751 bytes（901.127 MiB）**；这是待筛选范围，不是已暂存清单。包含了只做 stat 的受限登记文件，以及根目录中已被忽略的生成型 solution。
- `Source/Content/Config/Scripts/Docs` 没有单文件超过 50,000,000 bytes。`Assets` 有 5 个超过该阈值的源文件，均不足 100,000,000 bytes；五个也都超过 50 MiB，但均不足 100 MiB。
- **不要上传整份工程目录。** 本机 `Builds/` 21.222 GiB、`Saved/` 41.398 GiB、`Intermediate/` 6.685 GiB、`Binaries/` 1.131 GiB，不能与源码混装。
- 现有 `.gitignore` **没有 `Builds/`**。这是本轮最明确的误上传风险；不要把已有的 `Build/Receipts/` 或 `StagedBuilds/` 当作等效规则。
- Git 与 Git LFS 可执行文件可用；**`gh` 不在本次 PATH**，因此没有调用 `gh auth status`。不能据此认定 GitHub 已认证，也不能认定浏览器/连接器未登录。
- 在禁止读取/哈希 `Docs/LICENSES.md` 的约束仍有效时，实际上传必须继续明确排除该文件；不能用全量 `git add .`、`git add -A` 或全仓打包/哈希替代白名单选择。

## 2. 已执行与未执行

已执行：`Get-ChildItem` 的文件名/Length/时间元数据统计、`Get-Command` 应用程序定位、读取根 `.gitignore` 与 `README.md`、对 README 提及的工程/脚本和已存在发布 CMD 做路径存在性检查。

未执行：远程仓库创建、安装、`git add`、commit、push、Git status、Git diff、Git remote 查询、仓库全量哈希、`.git` 内部枚举、Git 凭据配置或 token 读取、源文件内容级密钥扫描、游戏启动、构建、打包、D 盘修改。

**没有读取或哈希 `D:\灯影山海\Docs\LICENSES.md`。** 它随 Docs 的 Length 元数据统计计入总数，不代表其内容或许可结论已审查。根 `LICENSES/` 是另一独立目录，本次也只有 stat。

以下统计使用递归文件元数据，不带 `-FollowSymlink`。它不是原子仓库快照，也不包含 Git 历史或 Git LFS 对象状态；主代理应在本轮美术写入结束后重新做最终上传清单核对。

## 3. 源工程范围的实际体量

| 目录 | 文件数 | Bytes | MiB | >50,000,000 B | >100,000,000 B |
|---|---:|---:|---:|---:|---:|
| `Source/` | 89 | 730,803 | 0.697 | 0 | 0 |
| `Content/` | 142 | 243,148,230 | 231.884 | 0 | 0 |
| `Config/` | 3 | 1,700 | 0.002 | 0 | 0 |
| `Scripts/` | 67 | 791,344 | 0.755 | 0 | 0 |
| `Docs/` | 98 | 1,350,105 | 1.288 | 0 | 0 |
| `Assets/` | 180 | 698,572,724 | 666.211 | 5 | 0 |
| 仅根目录文件，不含子目录 | 36 | 304,845 | 0.291 | 0 | 0 |
| **上述合计** | **615** | **944,899,751** | **901.127** | **5** | **0** |

分类建议：

- `Source`、`Content`、`Config`、`.uproject` 属于可重建 UE 源工程核心；不要因 `.uasset/.umap` 是二进制就排除 Content。
- `Scripts`、经筛选的 `Docs`、`Assets/Sources` 属于作者工具、规格和来源/可编辑源，应与当前工程版本一同备份；不是运行时缓存。
- 根目录的 `.gitignore/.gitattributes/.editorconfig/.vsconfig`、README 与选定 CMD 需要逐项保留/审查，不要把生成 `.sln/.slnx` 当成构建源必需品。
- 本次并未证明所有根 CMD 在排除 Saved/Builds 后仍能独立工作。不能只由名称猜它是当前新版游戏入口。

## 4. 源范围内全部大于 50,000,000 bytes 的文件

阈值按任务指定的十进制 MB 筛选；另列 MiB 便于与 Windows/工具输出比较。此表是文件元数据结果，不是对任何服务实时限额、配额或付费政策的判定。

| 相对路径 | Bytes | MiB | >100,000,000 B / >100 MiB |
|---|---:|---:|---|
| `Assets/Sources/DengYingArt/Staff-20261014/DY_Kuafu_Staff.blend` | 66,714,160 | 63.624 | 否 / 否 |
| `Assets/Sources/DengYingArt/Lamp-20261014/DY_HeroSpotlight_Source.blend` | 65,964,610 | 62.909 | 否 / 否 |
| `Assets/Sources/DengYingArt/LampBaked-20261014/DY_HeroSpotlight_Baked.blend` | 65,293,767 | 62.269 | 否 / 否 |
| `Assets/Sources/DengYingArt/Lamp-20261014/RuntimeVariant/DY_HeroSpotlight_RuntimeVariant.blend` | 62,979,066 | 60.062 | 否 / 否 |
| `Assets/Sources/DengYingArt/ArtBatch-20261014/MaterialCandidate/Leather037-2K/Leather037_2K-PNG.zip` | 57,088,064 | 54.443 | 否 / 否 |

这些文件是源范围内的 Blender 源或来源 ZIP，**不能只因较大便当作可删除缓存**。是否需要所有版本、是否进入 Git LFS，由主代理审查用途、许可与现有 attributes 后决定；本轮没有删除、改写或迁移它们。

## 5. 生成物、包与其他目录

| 目录 | 文件数 | Bytes | GiB | >50,000,000 B / >100,000,000 B | 本轮判断 |
|---|---:|---:|---:|---:|---|
| `Binaries/` | 19 | 1,214,161,714 | 1.131 | 5 / 4 | 编译生成物，现 ignore 已覆盖 |
| `Builds/` | 1,158 | 22,787,304,416 | 21.222 | 66 / 66 | 打包/归档输出范围，现 ignore 缺项 |
| `DerivedDataCache/` | 6 | 1,627,832 | 0.002 | 0 / 0 | 派生缓存，现 ignore 已覆盖 |
| `Intermediate/` | 952 | 7,177,673,474 | 6.685 | 7 / 4 | 构建中间物，现 ignore 已覆盖 |
| `Saved/` | 19,426 | 44,451,111,079 | 41.398 | 160 / 159 | 日志/审计/包/临时结果混合，现 ignore 已覆盖；不要整目录上传 |
| `.vs/` | 5 | 262,511 | 0.000 | 0 / 0 | 本机 IDE 状态，现 ignore 已覆盖 |
| `Build/` | 2 | 1,479,916 | 0.001 | 0 / 0 | 本次只有两份 `FileOpenOrder/*.log`，现 `*.log` 可覆盖 |
| `Tools/` | 23 | 160,254 | 0.000 | 0 / 0 | 可能含可复现工具；仅 stat，须审查后决定，不应一律当缓存 |
| 根 `LICENSES/` | 2 | 6,213 | 0.000 | 0 / 0 | 可能为随附许可文本；不是禁读登记文件，仅 stat，不宜自动丢弃 |
| `.agents/` | 1 | 1,113 | 0.000 | 0 / 0 | 本地代理配置范围；仅 stat，非 UE 运行必需，审查后决定 |

前六项生成物/缓存合计 **75,632,141,026 bytes（70.438 GiB）**，远高于源工程范围。此处给出其大文件数量而不逐条列出：上传建议是排除整个生成范围，不是逐个挑包入库。

不要笼统排除所有 `Build/`：UE 项目该目录也可能承载将来需要的图标/平台源配置。本次实际两项是 `Build/Windows/FileOpenOrder/CookerOpenOrder.log`（397 B）和 `EditorOpenOrder.log`（1,479,519 B）。

## 6. Git 工具与认证证据

| 检查 | 实际结果 |
|---|---|
| `Get-Command git -CommandType Application` | 可用：`C:\Program Files\Git\cmd\git.exe` |
| `Get-Command git-lfs -CommandType Application` | 可用：`C:\Program Files\Git\cmd\git-lfs.exe` |
| `Get-Command gh -CommandType Application` | 本次 PATH 未找到 |
| `gh auth status --hostname github.com` | 未执行，因为没有定位到 gh 可执行文件 |
| 根 `.git` | 目录存在；未读取内部、历史、index、remote 或 config |
| 根 `.gitattributes` | 文件存在，699 B；仅 stat，未核对其 LFS 匹配规则 |

Git LFS 二进制存在不等于仓库 filter 已配置、所有大文件已由 LFS 跟踪、对象已上传或账户有足够免费额度。以上均未验证。不要自动读取凭据、覆盖全局 Git 配置、安装 CLI 或购买额度。

主代理后续补充：已有连接器与受授权的只读凭据账户识别，本子任务不复查/输出账号或凭据；尚无新远程仓库，用户待建空私有库。主代理选定本次使用**普通 Git 白名单快照，不用 LFS**，原 D 盘 `.gitattributes` 不改。故本报告中的 LFS 可执行文件仅是环境事实，不构成“必须安装/启用 LFS”的要求。普通 Git 快照若带入原 attributes 中的 LFS 指令，须由主代理在快照副本内正确处理，不能生成 LFS 指针后却报告成普通 Git 完整源文件上传。

## 7. 当前 ignore 和入口的具体问题

### Ignore

已读取的根 `.gitignore` 覆盖 `Binaries/`、`DerivedDataCache/`、`Intermediate/`、`Saved/`、IDE 状态、生成 solution、`*.log`、`.env`/`.env.*`（保留 `.env.example`）等。

主执行上传前建议补审查两项，而非本轮直接改写：

1. 明确排除根 `Builds/`；现有规则并未覆盖它。
2. 在禁读条件持续时明确排除 `Docs/LICENSES.md`，并确保真正暂存白名单不包含它。

`.gitignore` 不能证明已跟踪文件或历史中没有这些路径。本轮未做 Git status/index/history 查询，因此不能宣称现忽略规则已经足够，也不能据此给出“仓库干净”的结论。

### 入口

根 README 当前仍以早期启动包和第一阶段复核为主，文件最后写入时间为 2026-10-01 22:56:13 +08:00。它明确给出的工程打开入口是 `C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject`（本机英文 junction），并给出环境检查与 Phase1 校验命令。

已确认以下相对路径实际存在，但**没有运行它们**：

- `DengYingShanHai.uproject`
- `Scripts/Check-Environment.ps1`
- `Scripts/Verify-Phase1Assets.py`
- `Docs/ENVIRONMENT_SETUP.md`
- `Docs/PHASE1_VALIDATION.md`
- `Start-ReleaseEntry.cmd`、`Start-ReleaseEntry-Shipping.cmd`（存在性检查，不是依赖/功能验收）

新电脑不会因为 clone 就自动拥有本机 C/D 盘路径、junction、UE 或工具链。首次上传 README 应由主代理补充“源码如何打开/生成工程/构建”和当前候选/已发布包的区别。不要把旧包启动器存在视为其依赖也会随源码上传；本轮没有审查所有 CMD/Scripts 对 Saved 审计或本机绝对路径的依赖。

## 8. 主代理实际上传前的安全顺序建议（本轮未执行）

1. 收尾并记录当前这轮成林候选的真实状态；不等待后续所有美术，不将未完成的 PIE 候选或新资产测试标为正式比赛完成。
2. 用明确白名单选择源工程与必要来源材料；排除受限登记、缓存、日志、大型本地包、IDE 状态和凭据。保留原工作目录和所有未提交内容，不做清理/reset。
3. 采用主代理已选的普通 Git 快照方案；审查快照副本的 `.gitattributes`/过滤器，确保是实际源文件而非未上传的 LFS 指针。原 D 盘 attributes 不改，不安装/启用 LFS或购买额度。
4. 若原仓库状态或历史无法在不触及受限文件的前提下安全确认，可优先采用**干净的白名单导出目录**创建新的私有仓库；不复制旧 `.git`，不改写或删除旧仓库。是否保留既有历史由主代理另行处理，本文不擅自决定。
5. 为私有仓库提供经过核对的当前状态 README、相对路径启动/构建说明、必要许可/来源说明和作者辅助工具。不要将当前工作区中尚未同步到 D 盘的工具误称为已备份；本文只统计了 D 盘范围。
6. 创建时明确 private，上传后由主代理实际确认远端私有性、文件清单、commit/LFS 对象与可取得性，再报告成功；本报告不构成任何远端完成证据。

限制：没有内容级秘密扫描、Git 状态/历史检查、LFS 策略/账户配额验证、第三方再分发许可审查或另一台机器克隆验证。私有仓库不是存放 token/凭据的理由；本文也不能证明所有材料均可再分发。

## 9. 补充只读核查：插件、可疑文件名与 reparse point

按主代理补充要求，仅读取根 `.uproject` 中的依赖字段，并对路径做 stat；没有启动插件或引擎。

| 项目描述符字段 | 实际值 |
|---|---|
| `EngineAssociation` | `5.8`，这个字段本身不证明已安装的精确 patch 版本 |
| Modules | `DengYingShanHai`，Runtime，LoadingPhase=Default |
| EnhancedInput | Enabled=true |
| PythonScriptPlugin | Enabled=true，TargetAllowList=[Editor] |
| AndroidFileServer | Enabled=false |
| 工程内 `Plugins/` 目录 | 不存在 |

没有工程内插件目录不等于所有引擎插件依赖已在新电脑验证；本轮未复制/安装任何 Engine 插件。

对根条目，以及 `Source/Content/Config/Scripts/Docs/Assets/Tools` 递归文件名检查了 `.env`、credential、token、private-key、secret、id_rsa、id_ed25519、pem/key/pfx/p12 等模式：**没有匹配文件名**。这是名字检查，不是内容密钥扫描，不能证明源文件或日志内容中绝无秘密。

对上述范围的文件/目录属性检查：**未发现 reparse point**；物理工程根目录本身也不是 reparse point。未带 FollowSymlink，未进入 `.git` 内部，也未枚举项目范围之外的链接目标。README 引用的 C 盘英文 junction 不属于这次 D 盘统计范围。

本次补充仍未读取/哈希受限许可登记、Git 凭据配置或 token；没有 Git 状态/网络写入/建仓/commit/push。
