# 复演者外观：免费源资产准备阶段

日期：2026-10-17。唯一人类作者与项目负责人：用户；Codex 为来源核查、整理和验证辅助工具。

## 本阶段交付与真实边界

已实际取得 Innerscene 的 CC0 便服人物 Sam，核查原始 Idle、Walk、Run 三个 GLB，制作了只含所需站立与移动动画的单一源 GLB 和打包贴图的可编辑 Blend。整理后文件经 Blender 4.5.14 实际重新导入、两条动画真实渲染，以及另行冷打开 Blend 验证。

**这是源资产准备完成，不是游戏内人物替换或正式美术验收完成。** 本轮没有 UE 导入，没有改 Pawn／GameMode／地图／菜单／C++／Config／镜头／输入／脚步声音，也没有构建或运行新游戏包。不能因为源文件有效就宣称玩家已不再是圆柱／球头。

## 来源、免费许可与选择依据

- [Idle 原作者页](https://www.innerscene.com/tools/library/3d-parts/idle-standing-sam-3d-person-animated-1f9f1217)
- [Walk 原作者页](https://www.innerscene.com/tools/library/3d-parts/brisk-walk-sam-3d-person-animated-bed03fa4)
- [Run 原作者页](https://www.innerscene.com/tools/library/3d-parts/run-sam-3d-person-animated-fa008c06)
- [Innerscene 库许可](https://www.innerscene.com/tools/library/terms)
- [MakeHuman 资产许可](https://static.makehumancommunity.org/about/license.html)
- [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)

原作者对这三个具体文件分别声明基于 MakeHuman／MPFB 的 CC0 身体、绑定和皮肤制作，并将所发布文件以 CC0 提供，可免费修改、使用和分发；不是把 MakeHuman 总许可套给未经核实的社区衣服。没有购买、登录付费档、订阅或使用付费生成服务。发布页说明动作来自作者周期姿势编排，不是动作捕捉，不能宣传为 mocap。保留原始文件与哈希，不依赖未来网站一直托管。

主代理实际检查了普通长袖上衣、长裤、鞋、短发、脸部与背面。模型没有盔甲、武器或西方职业徽记，可以作为虚构普通复演者的外观候选；没有赋予它新的神话身份、朝代或人物身世。衣料层次、皮肤质感、移动自然度和剧场融合仍有提升空间，后续必须在本游戏真实镜头与灯光下判断，不能仅以“比圆柱好”作为最终标准。

Quaternius 的 Base／Fantasy／UAL 原作者免费 Standard 层仍是备选，但 Source／Pro 付费层不在本项目范围。此轮实际取得并整理的是 Sam，不把尚未取得的 Quaternius 模块计为工程资源。

## 文件与规格

工程归档根：`Assets/Sources/Innerscene/Operator-20261017/`。

| 文件 | 用途 | 实际字节 / SHA-256 |
|---|---|---|
| `Original/sam-idle.glb` | 原作者原始文件，未改写 | 21,109,796 / `83FD621C92EB284585CD7D4F807697D59DCE723FCCA3910A48D0016D9F028AA6` |
| `Original/sam-run.glb` | 原作者原始文件，未改写 | 21,006,116 / `15BFD5C7E566A74447C246ABB24B60856AAC80CA1C4C661FBA3599380BB058C6` |
| `Prepared/SK_DY_Operator_Source.glb` | 同一人物＋Idle／Run；没有重复打包两套贴图 | 21,194,100 / `2670E4094E71570E9E38E86FCC20C5F4BA8FA9CEE63B91E5D3A8A02B00BC9871` |
| `Prepared/DY_Operator_Source.blend` | 可编辑、打包贴图、保留两条动作 | 31,197,924 / `1EEAC26A2C062E1513A9506344CB92B562E1B67616F466E9E926C376687E12BB` |

整理版实际冷读：1 个骨架、56 根骨骼、11 个有形 Mesh 对象，Idle 为 0–180 帧，Run 为 0–40 帧，30 fps。源 GLB 总三角统计约 9.16 万，包含原始退化附件定义，不能当作 UE 最终渲染三角或已优化 LOD 数。没有创建 LOD、PhysicsAsset、碰撞、IK、AnimBP 或根运动系统。

整理操作仅为：以 Idle GLB 为主体，追加同骨架 Run 的动画 accessor／bufferView；保留主体几何、UV、法线、材质、纹理、蒙皮权重、骨架层级与比例；仅移除原始零尺寸 Phone 节点的 mesh／skin 显示引用，不改动画骨骼。原始 BIN 前缀保留，原始来源另存不覆盖。未改肤色、服装配色或制造传统纹样，不把候选当成专属原创人物。

## 为什么没有直接套 Walk

原始 Walk 已实际下载并离线测量：动画时长约 1.733333 秒，但内含两遍约 0.866667 秒周期；Root 无平移。站地脚的世界后移速度约 1.7 m/s，单步距离约 73.67 cm。现有玩家 360 cm/s、脚步触发步距 150 cm。如果只在原速播放 Walk，会明显滑地；若单纯加速到匹配位移，又会让真实足落地频率约为音效的两倍。因此 Walk 只留本地对照，不纳入本阶段所选源模型。

同角色 Run 已实际取得并观察四个相位，骨架、网格和逆绑定与 Idle 相同。独立源数据测量得到：41 个 30 Hz 键、40/30 秒片段内有两遍 20/30 秒完整左右腿周期；支撑相位右脚0、左脚10、右脚20、左脚30，站地脚骨后移速度约4.5 m/s，因此单步约150 cm。以0.8倍播放时，脚骨后移约3.6 m/s，交替间隔约0.416667秒，与150/360秒同值。该结论是源数据的骨骼平台数值匹配，**不是渲染鞋底真实接触、起停同步或游戏运行验收**。任何建议播放速率只属于后续 Dev 显示层候选，不表示游戏已经修改；实际起步、加减速、转向、受阻、停止、E 操纵、切幕与 R／重演都须重新验证。**不为匹配动画擅自改变 360 cm/s、150 cm 或 2 cm 起步音效门槛，不新增跑步键、新移动状态或重复脚步 Notify。**

脚部骨架并非普通 calf→foot 链：foot_l／foot_r 是骨架的独立子节点，ball 是 foot 子节点，脚位移含 translation 动画。后续优先使用本源自己的骨架和动画，不强行套通用 Humanoid 重定向链或丢弃非根骨平移，否则会破坏步态。

## 实际检查、失败记录与图像

- 原始下载验证 GLB v2 头、完整长度、具体页面 CC0 声明及 SHA-256；无外部图像／buffer URI。
- 首轮动画矩阵检查失败并保留，真实 native exit=1；修正的是检查脚本中矩阵值拷贝／求值更新，未修改产品动画以迎合测试。后续实际骨矩阵变化成立。
- 初轮预览将导入器骨骼 custom-shape 的 Icosphere 算入地面范围，造成地面偏低；原图保留，没有拿来当角色悬浮已解决的游戏证据。修正为显式排除被骨骼引用的辅助形体并更新求值后重渲染。
- 原始候选和整理版均真实渲染；整理版七张检查图为 `Previews/` 内的正／后／侧站立与四个移动相位，1024×1280，Cycles CPU 16 samples／去噪／AgX。没有提亮、重绘或用概念图替代源模型画面；它们不是 UE 截图。
- `Checks/ROUNDTRIP.json` 与 `Checks/ROUNDTRIP-NATIVE-EXIT.json` 记录整理版实际重新导入、两条动作渲染和 Blend 冷打开，真实 native exit=0。
- 独立 GLB 检查没有读取或运行作者整理脚本，实际57项断言通过、原生命令退出0：原Idle 21,015,736字节BIN前缀、391旧accessors／401旧views保持，Run 336次输入／输出引用逐个字节相等，只有Phone63删除mesh7／skin0。结果为 `Checks/OPERATOR_SOURCE_INDEPENDENT_AUDIT.json`；这证明源数据等价，不能代替美术和UE验收。另一个手写蒙皮rest假设自检曾出现约1.49cm误差并失败，已弃用，未将该推算充当鞋底接地证据。

## 下一步与完成条件

下一步是独立 `Dev/PlayerAppearance/` 的 UE 骨骼导入与实际 POV 对照，先检查比例、材质、透明发丝／眼睫、骨骼平移曲线和资源引用。外观仍归已有 Theatre Pawn 所有，生命周期跟随 Pawn；不新增全局服务、复制、存档或谜题依赖。

若模型／动画可以接入，只在新显示子类中停用占位身体与头，保留旧图、旧 Pawn 和现有移动／相机／输入。脚步仍由原声音组件负责，动画只做显示，不通过根运动再次驱动位置。

角色替换完成必须有 UE 冷读与实际游戏画面、走停转向／碰撞／脚步／复位测试，以及明确打包目标的引用与运行验证；整体完成仍要求三幕／成林／重演回归、其他剩余美术、性能和参赛材料。当前所有这些后续项仍未完成。
