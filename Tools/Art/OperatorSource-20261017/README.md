# 复演者源资产阶段工具归档

这些是已用于本机来源检查、整理与实际渲染的辅助工具，不是 UE 游戏插件，不在运行时执行，也不是新电脑的一键人物导入器。

下载仅访问脚本内固定的 Innerscene 原作者 CC0 页面和官方 GLB 入口。`Download-Sam.ps1` 和 `Run-SamPreview.ps1` 使用本机路径；运行前必须核对脚本、Blender 4.5.14 路径与工作目录，禁止为方便删除既有来源或证据。下载文件不含执行内容，Blender 使用 `--disable-autoexec`。

本轮 C 盘工作目录布局为 `Sam-Original/`（Idle、Walk和DOWNLOAD.json）、`Sam-Run-Original/`（Run和DOWNLOAD.json）、`Operator-Prepared-Run1/`、各 Preview／RoundTrip 输出。工程归档将所选原始 Idle／Run 放入 `Assets/Sources/Innerscene/Operator-20261017/Original/`，整理版放 `Prepared/`；**归档布局不同**。如需重做，应先在新的、可写的临时工作副本中按前述工作布局准备来源，再运行工具，不要直接对归档路径运行并期望自动覆盖。

`prepare_operator_source.py` 固定核验原始Idle／Run哈希，将Run动画缓冲区追加到Idle，保留几何／权重／材质；`roundtrip_operator.py` 从同目录 `preview_sam.py` 只加载可信函数定义，对整理版重导入／渲染并冷开Blend；`inspect_sam_pose.py` 是原始Idle／Walk骨骼与鞋底定位诊断。工具不会打开 UE、修改游戏源码／地图或启用根运动。

失败Run1和早期地面基准偏低的Run2证据仍保留在原C盘工作目录，不能改写成全程成功。工程图册使用已修正基准的最终整理版真实渲染；实际执行记录和独立源数据审计同资产归档。
