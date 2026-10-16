# 木地板 Dev 材质样本

负责人：项目作者本人。Codex 在既定单人开发模式下实施与验证。

## 本次玩家可见结果

将现有 `LV_EnvironmentStatesLab` 的地面替换为免费 CC0 木地板 PBR 材质。木纹、板缝、磨损和反射由原有舞台照明呈现，不新增照明，也不以改变曝光掩盖材质问题。这是环境美术的第一个独立样本，不代表小剧场空间、夸父形象或正式美术已完成。

上一轮“进入下一幕取消上一幕 E 操纵状态”已得到作者确认；本轮必须保留它以及现有三幕流程、声音和步态同步。

## 有界设计

- 只修改现有 Dev 地图中 `DEV_Floor` 的材质槽 0；其网格、尺寸、位置、碰撞与阴影设置保持原值。
- 新增三张 2K 纹理、一个仅供地面使用的父材质和一个常量实例，共五个资产；不建立通用大材质框架。
- 实际只读渲染诊断确认 `r.Substrate=0`，因此采用工程正在使用的标准 PBR 材质输出；不迁移渲染路线，不改项目配置，不引入多层材质、透明幕布、位移、WPO、MPC 或运行时材质写入。初版误用不生效的 Slab 输出所致地面发黑已在仅新父材质范围修正，失败记录保留。
- BaseColor 使用 sRGB；DirectX 法线采用 NormalMap 压缩、线性采样；ARM 使用线性 Masks，R=AO、G=Roughness。木材为介电体，F0=0.04，不使用金属度贴图。
- 初始平铺依据现场冷读地面尺寸与来源页面标称约 2 m 调整。平铺只属于该 Dev 样本，不是谜题参数或文化史实。
- 不修改 C++、Blueprint 事件图、输入、UI、相机、谜题数据、15 Hz、灯/偶位置、音频、演出时长、落杖接触与成林链路。

## 文件及回退边界

唯一既有内容资产：`Content/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab.umap`。

新增内容包均位于 `Content/DengYingShanHai/Dev/WoodFloor/`，不进入正式目录。新增作者脚本、独立启动器、来源记录及验证文档。相关 TECH_SPEC / DEVELOPMENT_PLAN 仅追加本轮事实，不重写旧记录。

先记录所有既有产品文件和旧包的 SHA256，并备份获准变更的地图和文档。旧 `Start-EnvironmentDev.cmd` 与 EnvironmentDev-20261011-Run2 包保持不变。新入口 `Start-WoodFloorDev.cmd` 只接受独立 WoodFloorDev-20261011-Run1 包。编辑器回退使用当前源地图，不能冒充历史已验收的灰盒画面。

## 资产与许可

仅使用 Poly Haven `Old Wooden Floor 02` 的官方下载 PNG，不将网站预览渲染、网站文案或商标当作游戏资产。作者：Charlotte Baglioni（扫描）、Jenelle van Heerden（处理）；许可 CC0-1.0。三份原始文件和官方 CC0 法律文本留存在 `Assets/Sources/PolyHaven/old_wooden_floor_02/`；来源、URL、像素尺寸及哈希另记 `Docs/WOOD_FLOOR_SOURCES.md`。

## 验证与交付

1. 只读冷探测地面实际属性、材质接口和场景合同。
2. 在精确五资产白名单内导入并制作材质，保存现有地图的一个材质槽变更。
3. 全新进程冷读：确认三纹理 2048²、色彩空间/压缩、实际父材质及地面槽、编译无错误；全场景合同除该槽外相同。
4. 原有 154 项原生测试、完整两轮三幕 PIE 与声音/环境检查、真实操纵会话跨幕检查均复跑。
5. 独立 Windows Development 打包：Cook 只指定现有这一张地图，确认五个新依赖实际进入 UFS。
6. 真实包首帧、完整性和启动器 DryRun；保存画面供视觉评估，不将技术通过写成人工画质认可。

降级方案是保留旧包继续演示，而不是降低谜题可靠性、改光照或扩大场景。全套结果通过后直接提供新的可双击文件位置；正式空间搭建仍是后续单独可验证任务。
