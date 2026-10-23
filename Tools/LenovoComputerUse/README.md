# Lenovo Computer Use

> 当前状态（2026-10-03）：按用户明确要求已卸载 `lenovo-computer-use@lenovo-local`，
> 并移除仅为它创建的 `lenovo-local` 来源登记。后续项目工作恢复安装前的非插件方式，
> 不调用本插件，不自动重装；只有用户再次明确要求才可安装/恢复。
> 源码和历史测试记录保留，不属于已安装状态。`Saved/LenovoComputerUse/STOP`
> 已建立，阻止当前会话尚未卸载的运行连接继续执行桌面动作。
> 下文的已安装描述是历史记录与重装说明，不代表当前启用状态。

这是为 lenovo 的 WorkBuddy / UE 开发工作制作的独立 Windows 桌面操作插件。
Codex 模型负责看图、判断与监督，本地工具执行截图及输入。
代码为本次独立编写并采用 MIT 许可；未复制官方 Computer Use 的专有代码，
不调用官方私有桌面运行时，不依赖官方 Computer Use 的账号开关。
不需要 API Key、付费服务、额外 Python 包或常驻网络端口。

## 启用与使用

本机已通过官方 CLI 注册本地市场 `lenovo-local`，安装并启用
`lenovo-computer-use@lenovo-local`。在“插件”页面的来源中寻找“Lenovo 专属工具”，
插件名称为 **Lenovo Computer Use**。

安装后需重新加载桌面客户端的工具配置。请完全退出并重新打开 Codex/ChatGPT
桌面端，然后开启一个聊天，检查 `/mcp` 中的 `lenovo_desktop`。
部分客户端展示名称可能带插件命名空间。
旧聊天的已加载工具列表可能不会自动增加该服务器；这是会话加载状态，
不是安装失败。应用界面是否显示及当前账号能否启动本地 MCP，仍以新会话为准。

可以直接说：

> 使用 Lenovo Computer Use 查看 WorkBuddy，继续监督《灯影山海》已批准的第三幕 Dev 原型。先核对当前工作区和未完成事项，再按已有授权继续。

窗口需要处于可见前台。操作过程中请暂时让出鼠标键盘；
失焦、弹窗、窗口移动或缩放后，工具会要求重新截图。
Windows 锁屏、UAC 安全桌面和权限更高的应用不在支持范围内。

## 已有能力

| 工具 | 用途 |
|---|---|
| `status` | 查询版本、允许的应用和停止状态 |
| `list_windows` | 列出允许应用的可见窗口与唯一标识 |
| `focus_window` | 恢复/激活指定窗口 |
| `observe_window` | 返回 PNG、坐标信息和短期操作凭据 |
| `ui_tree` | 尽力读取 Windows UI Automation 文本、控件与边界 |
| `click` | 左/右键单击或双击 |
| `type_text` | Unicode 中文与 emoji 输入，不操作剪贴板，不自动提交 |
| `press_key` | 组合键、方向键、UE 按键，最长保持 2 秒 |
| `scroll` | 在指定位置滚动 |
| `drag` | 有界左键拖拽，异常或中断时释放鼠标 |
| `stop` | 持久停止所有使用同一数据目录的插件会话 |

第一版聚焦当前项目的监督工作，不等同于官方产品的完整功能。
它没有系统级任意应用授权面板、官方状态浮条、后台窗口输入、
自动启动应用、OCR 模型、视频录制或 UAC 操作。阅读 GPU/Electron 应用
主要依赖截图；UI Automation 控件可能缺失或只有通用 Pane。

## 停止与恢复

- 双击本目录 `Stop-Control.cmd`：立即建立 STOP 标记。活动输入在下一次检查时停止。
- 操作执行期间按住 **Ctrl+Alt+Pause**：建立同一个持久 STOP 标记。
- 由你本人双击 `Resume-Control.cmd`：恢复。Codex 的 skill 明确禁止自行清除停止标记。

热键以轮询检测，单击瞬时动作不能保证赶在输入前被取消；
文件停止入口适合在开始操作前明确阻止后续动作。

默认允许的应用见 `plugins/lenovo-computer-use/policy.json`：

- `D:\LenovoSoftstore\Install\WorkBuddy\WorkBuddy.exe`
- `C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe`
- 名为 `Lenovo Computer Use Test` 的专用 PowerShell 测试窗口

没有开放浏览器、聊天软件、所有 PowerShell 窗口或任意进程。
配置允许应用只决定工具技术上可访问哪些窗口，不代替用户对任务本身的授权。
后续若需 VS 等其他应用，应按实际任务扩充规则并复验。

截图最长边默认 1600 像素；工具按 PNG 坐标自动换算为物理像素，
已在本机 150% DPI 下验证。操作凭据默认 60 秒有效、仅属于当前运行会话，
且每次输入尝试后失效。截图不会持续后台录制；提供给 Codex 的图像会成为
该聊天的工具结果，按所用聊天服务的数据处理规则传递，不能理解为截图永不离开本机。

运行数据放在工程的 `Saved/LenovoComputerUse/`，由现有 `.gitignore` 排除。
日志只记录操作类型、窗口 ID、成功/失败和输入字数，不记录输入文本或截图。
测试窗口的示例文本、测试截图、WorkBuddy 检查截图是验收证据，单独保存在该目录。

## 安装结构与限制

```text
LenovoComputerUse/
├─ .agents/plugins/marketplace.json
├─ plugins/lenovo-computer-use/
│  ├─ .codex-plugin/plugin.json
│  ├─ .mcp.json
│  ├─ policy.json
│  ├─ server.py
│  ├─ desktop.py
│  ├─ ui_tree.ps1
│  ├─ skills/lenovo-computer-use/SKILL.md
│  └─ LICENSE
├─ tests/
├─ Install.cmd / Install.ps1
└─ Stop-Control.cmd / Resume-Control.cmd / Control-State.ps1
```

安装副本位于：

`C:\Users\lenovo\.codex\plugins\cache\lenovo-local\lenovo-computer-use\0.1.0`

这是个人专用版本：`.mcp.json` 使用本机 Python 与源码的绝对路径。
即使插件清单被复制到 Codex 缓存，启动代码仍来自这个工具目录。
请保留 `Tools/LenovoComputerUse/`；移动工程或升级 Python 路径后需更新该清单。
若需重装，运行 `Install.cmd`。本地插件 API/市场由 Codex 宿主管理；
插件安装成功不代表宿主在所有账号、设备或聊天中均开放本地 MCP。

卸载可执行 `codex plugin remove lenovo-computer-use@lenovo-local`。
这只卸载自己的插件；源码、运行证据和停止标记继续保留，便于回退。
无需更改 UE 的 `.uproject`、C++、蓝图或关卡，插件不会进入游戏 Cook。

## 验证与负责人

实现、安装和技术验证：Codex；桌面使用、停止/恢复和最终人工验收：项目负责人。
测试结果和实际限制见 [VALIDATION.md](VALIDATION.md)。

可复跑命令（实际桌面测试需要 Windows 交互桌面权限）：

```powershell
python -m unittest discover -s Tools/LenovoComputerUse/tests -p 'test_*.py' -v
python Tools/LenovoComputerUse/tests/smoke_desktop.py --data-dir Saved/LenovoComputerUse/Test
```

实现参考：

- [OpenAI 本地插件与市场格式](https://developers.openai.com/plugins/build/plugins)
- [Codex 本地 MCP 配置与重启](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [MCP stdio 传输规范](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
- [Microsoft SendInput 与权限限制](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput)
- [Microsoft DPI awareness](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setprocessdpiawarenesscontext)
- [Microsoft UI Automation](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-uiautomationoverview)
