# 思源黑体：实际采用来源

- 作者/权利人：Adobe；字体家族 Source Han Sans SC / 思源黑体。
- 原始文件：SourceHanSansSC-Regular.otf，未经修改、未经子集化；16,529,832 bytes。
- 二进制 name 表版本实读：Version 2.005;addfeatures 5.0.0b21。
- 官方仓库：https://github.com/adobe-fonts/source-han-sans
- 固定 release 分支提交：a4f7cf94edfb9d7ffbdfc4841de276358bd7e0f2。
- 下载：https://raw.githubusercontent.com/adobe-fonts/source-han-sans/a4f7cf94edfb9d7ffbdfc4841de276358bd7e0f2/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf
- 下载日期：2026-10-03。
- SHA256：F1D8611151880C6C336AABEAC4640EF434FA13CBFBF1FFE82D0A71B2A5637256。
- 完整版权/许可：同提交 LICENSE.txt，已原文保存本目录；SIL OFL 1.1，保留版权与许可，禁止字体本身单独出售，修改版遵守 Reserved Font Name。
- 使用：Dev/M2/UI/FF_DYSourceHanSansSC FontFace（Inline 原始负载）、FF_DYSourceHanSansSC_Font UFont、WBP_DYInteractionHUD 原型。没有安装系统字体，没有引入思源宋体或额外字重。
- 发布：Build.cs RuntimeDependencies 自动将 LICENSE.txt 作为 NonUFS 放入包的 DengYingShanHai/LICENSES/SourceHanSans/LICENSE.txt，不靠手工补文件。
- 验证：Saved/Audit-2026-10-03-M2UI/FontSource/Inspect-Font.py 只读检查 name/cmap；本轮 45 种文案字符（包含 U+3000 全角空格）无缺字。另已在本机 Editor PIE 与独立 Development/Shipping 测试包验证中文显示；不以 cmap 检查代替显示验收。
- 原始 OTF 与检验脚本保存在 Saved/Audit-2026-10-03-M2UI/FontSource（Saved 默认不入 Git，交付时须保全该证据；产品 FontFace 与许可需跟随正式恢复点保存）。
