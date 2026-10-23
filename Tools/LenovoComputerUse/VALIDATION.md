# Lenovo Computer Use 0.1.0 验收记录

日期：2026-10-03，Asia/Shanghai。实现与技术验收负责人：Codex。
用户需求：官方 Computer Use 无法使用，为本机制作个人桌面操作插件。

## 已完成

- 独立 Python 标准库 + Windows API 实现；无第三方 Python 包、API Key 或网络监听端口。
- MCP stdio、11 个工具、配套 skill、Codex 兼容插件清单、本地市场、停止/恢复入口。
- 官方 CLI 成功注册 `lenovo-local`，安装 `lenovo-computer-use@lenovo-local`。
- 安装清单与缓存副本已读回；用户配置包含该插件的 `enabled = true`。
- 使用**已安装缓存中的 `.mcp.json`**启动真实服务器，完成
  `initialize` → `notifications/initialized` → `tools/list` → `tools/call`。
- 实际识别 WorkBuddy，恢复到前台截图，再还原此前的最小化状态。
  截图可清楚阅读《灯影山海》项目接管与状态审计页面。
  本轮没有给 WorkBuddy 输入、提交或下发项目任务。

## 自动化结果

`python -m unittest discover -s Tools/LenovoComputerUse/tests -p 'test_*.py' -v`

**10 passed / 0 failed**：

- MCP 初始化、版本协商、工具发现与通知无响应
- 不合法 JSON、请求及参数拒绝
- 输入类型、未知参数和布尔坐标拒绝
- 按键保持时间上限、重复组合键拒绝
- STOP 跨服务器实例保持
- 日志不写入输入内容
- 实际子进程 stdio 编码与消息分隔
- 负坐标显示器与缩放后的图像坐标换算
- PNG 图像尺寸、RGB 通道和 CRC 正确

Skill Creator 的 `quick_validate.py`：**Skill is valid**。

## 本机真实桌面测试

`python Tools/LenovoComputerUse/tests/smoke_desktop.py --data-dir Saved/LenovoComputerUse/Test`

**12 checks passed**。测试只在本轮创建的独立 WinForms 窗口内输入。
控件接收到的真实状态由测试窗口自身回报，再与操作结果对照，
不是只判断 SendInput 的返回值。

| 项目 | 结果 |
|---|---|
| 允许应用的枚举与进程身份 | 通过 |
| UI Automation 控件/区域读取 | 通过；部分控件为 unnamed Pane，测试明确使用唯一几何区域 |
| 真实前台截图与 PNG | 通过；人工查看截图 |
| 中文和 emoji 输入 | 通过；文本框实际内容精确匹配，包括 UTF-16 surrogate pair |
| Ctrl+A、方向键、按钮点击 | 通过；按钮计数实际为 1 |
| 已消费截图的重复输入拒绝 | 通过；按钮计数仍为 1 |
| 拖拽与释放 | 通过；在本机 150% DPI 下对比物理/逻辑距离 |
| 滚轮输入 | 通过；目标区域实际收到 2 步 |
| 截图后移动窗口 | 通过；旧坐标被拒绝 |
| 最小化/失焦时键盘输入 | 通过；文本保持原样 |
| 过期截图 | 通过；超过 TTL 的输入拒绝 |
| 持久 STOP | 通过；新服务器实例不能激活窗口 |

MCP 安装探测：**协议 2025-11-25、11 个工具、WorkBuddy 截图通过**。

## 实测发现与修正

- Windows 沙箱无法枚举交互桌面：已通过产品的权限升级机制获得正常桌面访问，
  未尝试绕开该限制。插件由桌面宿主启动时仍需要宿主允许本地桌面操作。
- PowerShell 队列中 `@($child, $depth + 1)` 的表达式优先级造成深度错误：
  加括号后验证树节点深度正确。
- WinForms UI Automation 不保证使用 `AccessibleName`，也可能只暴露通用 Pane：
  保留真实数据，不伪造控件语义；截图仍作为主要视觉证据。
- 本机显示缩放为 150%，测试窗口鼠标事件回报逻辑坐标：
  使用实际区域缩放比验收拖拽距离，插件继续使用物理像素与图像坐标换算。

## 证据位置

运行数据、截图和日志位于 `Saved/LenovoComputerUse/`，由既有 `.gitignore` 排除。

- `Test/smoke-results.json`：12 项实测结果
- `Test/smoke-state.json`：测试窗口实际状态
- `Test/smoke-ui-tree.json`：测试窗口真实 UIA 数据
- `Test/smoke-before.png` / `Test/smoke-after.png`：操作前后截图
- `InstalledProbe/installed-probe.json`：安装清单启动、握手和真实应用验证
- `InstalledProbe/workbuddy-observed.png`：实际 WorkBuddy 只读截图
- `audit.jsonl`：应用识别与只读安装探测记录

## 尚未验收的能力与边界

1. 当前聊天的工具列表是在安装前加载的；**未声称本聊天已可直接调用新 MCP 工具**。
   用户需重新启动桌面端，在聊天中通过 `/mcp` 核验连接。
   插件来源/卡片在桌面端 UI 的实际显示同样待用户确认。
2. 本轮没有打开 UE 编辑器，UE 内的输入、GPU 截图和 Blueprint UIA 仍待实际关卡验证。
3. STOP 文件已验证；Ctrl+Alt+Pause 的物理热键检测未由用户人工测试。
4. MCP 输入取消采用协作检查，长按/拖拽会检查取消并释放；没有对用户的物理抢占行为
   或每一种 Windows 输入设备做全面测试。短暂单击不能保证在任何时刻被即时中止。
5. 不能在锁屏、UAC 安全桌面或权限更高的应用内工作；不提升目标应用权限。
6. 这不是官方权限 UI 的复刻。默认应用范围由 `policy.json` 明确限制；
   配套 skill 保持项目授权边界，但插件本身不理解“发布消息”等动作的业务含义。
   应由 Codex 依据用户任务判断提交授权。
7. 绝对路径使此版本绑定本机与当前工程位置。搬迁后需要更新 `.mcp.json`。

## 项目影响与回退

新增源码、测试、使用文档和插件清单位于 `Tools/LenovoComputerUse/`。
Codex 用户配置由官方 CLI 新增市场与插件启用项，安装缓存只新增本插件。
没有修改 UE Source、Content、Config、地图、已有项目文档或已有 Git 改动；未提交 Git。

回退：`codex plugin remove lenovo-computer-use@lenovo-local` 卸载自身插件。
若不再使用该唯一市场，可再执行 `codex plugin marketplace remove lenovo-local`。
源码与证据均保留，未实施文件删除。

AI 使用记录：本工具源码、skill、测试和说明由 Codex 根据用户本轮明确需求生成，
本机执行验证；没有引入官方 Computer Use 的专有源码。
它是开发工具，不属于参赛游戏的发行内容；若后续随参赛材料提交，需按比赛要求披露。
